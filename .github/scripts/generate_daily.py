from __future__ import annotations

from pathlib import Path
import re
import sys
from typing import Iterable


ROOT_README = Path("README.md")
TARGET_ROOT = Path("problem_solve")
DEFAULT_LANGUAGES = ["java"]

LANG_EXTENSIONS = {
    "java": "java",
    "swift": "swift",
    "python": "py",
    "c++": "cpp",
    "cpp": "cpp",
    "c": "c",
    "javascript": "js",
    "typescript": "ts",
    "kotlin": "kt",
}

DAILY_BLOCK_PATTERN = re.compile(
    r"^###\s*📝💯\s*(?P<title>.+?)\s*문제\s*$"
    r"(?P<body>[\s\S]*?)"
    r"(?=^###\s|^##\s|\Z)",
    re.MULTILINE,
)

# [Easy], [Normal], [Hard], [Level 1] 등 다양한 레벨 태그 및 불릿 기호 지원
MARKDOWN_LINK_PATTERN = re.compile(
    r"^(?:[-*]\s*)?"
    r"(?:\[(?P<level>Easy|Normal|Hard|Level\s*\d+)\]\s*)?"
    r"\[(?P<title>.+?)\]\((?P<url>.+?)\)\s*$",
    re.IGNORECASE
)


def sanitize(name: str) -> str:
    invalid = r'<>:"/\\|?*'

    for character in invalid:
        name = name.replace(character, "-")

    name = re.sub(r"\s+", " ", name).strip()
    return name.rstrip(".")


def extract_daily_blocks(text: str) -> list[tuple[str, str]]:
    blocks = [
        (
            match.group("title").strip(),
            match.group("body"),
        )
        for match in DAILY_BLOCK_PATTERN.finditer(text)
    ]

    if not blocks:
        raise ValueError(
            "README에서 "
            "'### 📝💯 {주차} 문제' 형식의 블록을 찾지 못했습니다."
        )

    return blocks


def extract_links(body: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    
    # 레벨이 지정되지 않았을 때 순차적으로 부여할 기본 순서
    fallback_levels = ["Easy", "Normal", "Hard"]
    valid_line_count = 0

    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue

        match = MARKDOWN_LINK_PATTERN.match(line)

        if not match:
            continue

        level = match.group("level")
        
        # 명시된 level 태그가 없는 경우 처리
        if not level:
            if valid_line_count < len(fallback_levels):
                level = fallback_levels[valid_line_count]
            else:
                level = f"Level {valid_line_count + 1}"

        problem_title = match.group("title").strip()
        
        # 제목 안에 남아있을 수 있는 난이도 태그([Easy] 등) 정제
        problem_title = re.sub(
            r"^\[(Easy|Normal|Hard|Level\s*\d+)\]\s*", 
            "", 
            problem_title, 
            flags=re.IGNORECASE
        ).strip()
        
        problem_url = match.group("url").strip()

        links.append({
            "level": level.capitalize(),
            "title": problem_title,
            "url": problem_url
        })
        
        valid_line_count += 1

    if not links:
        raise ValueError("문제 블록에서 문제 링크를 찾지 못했습니다.")

    return links


def detect_platform_tag(url: str) -> str:
    lower_url = url.lower()

    if "acmicpc.net" in lower_url:
        return "BOJ"

    if (
        "programmers.co.kr" in lower_url
        or "school.programmers.co.kr" in lower_url
    ):
        return "PGS"

    if "swexpertacademy.com" in lower_url:
        return "SWEA"

    if "leetcode.com" in lower_url:
        return "LTC"

    if "codeforces.com" in lower_url:
        return "CF"

    return "ETC"


def build_daily_readme(
    title: str,
    links: list[dict[str, str]],
) -> str:
    lines = [
        f"# {title} 문제",
        "",
        "## 문제 목록",
        "",
    ]

    for item in links:
        lines.append(f"- [{item['level']}] [{item['title']}]({item['url']})")

    lines.append("")
    return "\n".join(lines)


def build_problem_folder_name(
    item: dict[str, str],
) -> str:
    platform_tag = detect_platform_tag(item["url"])
    # 폴더명 형식: [레벨] [태그] {문제이름}
    return sanitize(f"[{item['level']}] [{platform_tag}] {item['title']}")


def extract_member_section(text: str) -> str:
    tables = re.findall(
        r"<table>([\s\S]*?)</table>",
        text,
        re.IGNORECASE,
    )

    for table in tables:
        if "github.com/" in table.lower():
            return table

    raise ValueError(
        "README에서 GitHub 링크가 포함된 "
        "스터디 멤버 테이블을 찾지 못했습니다."
    )


def extract_members(
    member_section: str,
) -> list[dict[str, object]]:
    cells = re.findall(
        r"<td\b[^>]*>[\s\S]*?</td>",
        member_section,
        re.IGNORECASE,
    )

    usernames: list[str] = []

    for cell in cells:
        match = re.search(
            r"github\.com/([^\"'/<>?#]+)",
            cell,
            re.IGNORECASE,
        )

        if not match:
            continue

        username = match.group(1)

        if username not in usernames:
            usernames.append(username)

    if not usernames:
        raise ValueError(
            "스터디 멤버 테이블에서 GitHub 사용자명을 찾지 못했습니다."
        )

    language_cells = find_language_cells(member_section)

    members: list[dict[str, object]] = []

    for index, username in enumerate(usernames):
        languages: list[str] = []

        if index < len(language_cells):
            languages = extract_languages_from_cell(
                language_cells[index]
            )

        if not languages:
            languages = DEFAULT_LANGUAGES.copy()

        members.append(
            {
                "username": username,
                "languages": languages,
            }
        )

    return members


def find_language_cells(member_section: str) -> list[str]:
    rows = re.findall(
        r"<tr\b[^>]*>([\s\S]*?)</tr>",
        member_section,
        re.IGNORECASE,
    )

    for row in rows:
        cells = re.findall(
            r"<td\b[^>]*>[\s\S]*?</td>",
            row,
            re.IGNORECASE,
        )

        if not cells:
            continue

        if any(extract_languages_from_cell(cell) for cell in cells):
            return cells

    return []


def extract_languages_from_cell(
    cell_html: str,
) -> list[str]:
    languages: list[str] = []

    data_match = re.search(
        r"data-languages?=[\"']([^\"']+)[\"']",
        cell_html,
        re.IGNORECASE,
    )

    if data_match:
        candidates = re.split(
            r"[,\s]+",
            data_match.group(1),
        )

        for candidate in candidates:
            language = normalize_language_name(candidate)

            if language and language not in languages:
                languages.append(language)

    badge_matches = re.findall(
        r"badge/([^?\-\s]+)-",
        cell_html,
        re.IGNORECASE,
    )

    for badge in badge_matches:
        language = normalize_language_name(badge)

        if language and language not in languages:
            languages.append(language)

    plain_text = re.sub(r"<[^>]+>", " ", cell_html)

    for candidate in re.split(r"[,/\s]+", plain_text):
        language = normalize_language_name(candidate)

        if language and language not in languages:
            languages.append(language)

    return languages


def normalize_language_name(raw: str) -> str | None:
    normalized = raw.strip().lower()

    mapping = {
        "java": "java",
        "swift": "swift",
        "python": "python",
        "py": "python",
        "c++": "c++",
        "c%2b%2b": "c++",
        "cpp": "c++",
        "kotlin": "kotlin",
        "javascript": "javascript",
        "js": "javascript",
        "typescript": "typescript",
        "ts": "typescript",
        "c": "c",
    }

    return mapping.get(normalized)


def write_if_changed(
    path: Path,
    content: str,
) -> bool:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if path.exists():
        existing_content = path.read_text(
            encoding="utf-8"
        )

        if existing_content == content:
            return False

    path.write_text(
        content,
        encoding="utf-8",
    )

    return True


def ensure_file(
    path: Path,
    content: str = "",
) -> bool:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if path.exists():
        return False

    path.write_text(
        content,
        encoding="utf-8",
    )

    return True


def build_problem_readme(
    problem_folder_name: str,
    problem_url: str,
) -> str:
    return (
        f"# {problem_folder_name}\n\n"
        f"- 문제 링크: {problem_url}\n"
    )


def build_code_template(
    username: str,
    language: str,
) -> str:
    if language == "java":
        return ""

    if language == "swift":
        return (
            "import Foundation\n\n"
            f"// {username}\n"
        )

    if language == "python":
        return f"# {username}\n"

    if language == "c++":
        return (
            "#include <bits/stdc++.h>\n"
            "using namespace std;\n\n"
            "int main() {\n"
            "    ios::sync_with_stdio(false);\n"
            "    cin.tie(nullptr);\n"
            "    return 0;\n"
            "}\n"
        )

    if language == "c":
        return (
            "#include <stdio.stdio.h>\n\n"
            "int main(void) {\n"
            "    return 0;\n"
            "}\n"
        )

    if language == "kotlin":
        return (
            "fun main() {\n"
            "}\n"
        )

    if language in {
        "javascript",
        "typescript",
    }:
        return f"// {username}\n"

    return ""


def generate_daily_folder(
    daily_title: str,
    links: list[dict[str, str]],
    members: list[dict[str, object]],
) -> None:
    safe_title = sanitize(daily_title)

    if not safe_title:
        raise ValueError(
            "데일리 문제 제목이 비어 있습니다."
        )

    daily_directory = TARGET_ROOT / safe_title
    daily_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    daily_readme = daily_directory / "README.md"

    write_if_changed(
        daily_readme,
        build_daily_readme(daily_title, links),
    )

    for item in links:
        problem_folder_name = build_problem_folder_name(item)

        problem_directory = (
            daily_directory
            / problem_folder_name
        )

        problem_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        problem_readme = (
            problem_directory
            / "README.md"
        )

        write_if_changed(
            problem_readme,
            build_problem_readme(
                problem_folder_name,
                item["url"],
            ),
        )

        for member in members:
            username = str(member["username"])
            languages = member["languages"]

            if not isinstance(languages, list):
                continue

            for language_value in languages:
                language = str(language_value)
                extension = LANG_EXTENSIONS.get(language)

                if not extension:
                    continue

                code_file = (
                    problem_directory
                    / f"{username}.{extension}"
                )

                ensure_file(
                    code_file,
                    build_code_template(
                        username,
                        language,
                    ),
                )


def main() -> None:
    if not ROOT_README.exists():
        print("루트 README.md가 없습니다.")
        sys.exit(1)

    try:
        readme_text = ROOT_README.read_text(
            encoding="utf-8"
        )

        daily_blocks = extract_daily_blocks(
            readme_text
        )

        member_section = extract_member_section(
            readme_text
        )

        members = extract_members(
            member_section
        )

        for daily_title, daily_body in daily_blocks:
            links = extract_links(daily_body)

            generate_daily_folder(
                daily_title,
                links,
                members,
            )

    except ValueError as error:
        print(f"생성 실패: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
