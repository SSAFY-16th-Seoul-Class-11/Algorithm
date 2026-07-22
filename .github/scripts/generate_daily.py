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
    r"^###\s*🟨\s*(?P<title>.+?)\s*문제\s*$"
    r"(?P<body>[\s\S]*?)"
    r"(?=^###\s|^##\s|\Z)",
    re.MULTILINE,
)

MARKDOWN_LINK_PATTERN = re.compile(
    r"^(?:[-*]\s*)?\[(?P<title>.+?)]\((?P<url>.+?)\)\s*$"
)


def sanitize(name: str) -> str:
    # 파일/폴더 시스템에서 허용되지 않는 특수문자 제거 (대괄호 [] 는 유지)
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
            "'### 🟨 {주차} 문제' 형식의 블록을 찾지 못했습니다."
        )

    return blocks


def clean_problem_title(title: str) -> str:
    # 기존에 붙어있던 [Easy], [Normal], [Hard] 등의 난이도 태그를 정제
    return re.sub(r"^\[(Easy|Normal|Hard|Level\s*\d+)\]\s*", "", title).strip()


def extract_links(body: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []

    for line in body.splitlines():
        match = MARKDOWN_LINK_PATTERN.match(line.strip())

        if not match:
            continue

        problem_title = clean_problem_title(match.group("title"))
        problem_url = match.group("url").strip()

        links.append((problem_title, problem_url))

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
    links: Iterable[tuple[str, str]],
) -> str:
    levels = ["Easy", "Normal", "Hard"]
    lines = [
        f"# {title} 문제",
        "",
        "## 문제 목록",
        "",
    ]

    for idx, (problem_title, problem_url) in enumerate(links):
        level_tag = levels[idx] if idx < len(levels) else f"Level {idx + 1}"
        lines.append(f"- [{level_tag}] [{problem_title}]({problem_url})")

    lines.append("")
    return "\n".join(lines)


def build_problem_folder_name(
    problem_title: str,
    problem_url: str,
    idx: int,
) -> str:
    levels = ["Easy", "Normal", "Hard"]
    level_tag = levels[idx] if idx < len(levels) else f"Level {idx + 1}"
    platform_tag = detect_platform_tag(problem_url)

    # 폴더명 형식: [PGS] [Easy] 네트워크1
    return sanitize(f"[{platform_tag}] [{level_tag}] {problem_title}")


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
        return (
            "import java.io.*;\n"
            "import java.util.*;\n\n"
            "class Main {\n"
            "    public static void main(String[] args) "
            "throws Exception {\n"
            "        BufferedReader br = new BufferedReader(\n"
            "            new InputStreamReader(System.in)\n"
            "        );\n"
            "    }\n"
            "}\n"
        )

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
            "#include <stdio.h>\n\n"
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


def update_root_readme_with_levels(readme_text: str) -> tuple[str, bool]:
    levels = ["Easy", "Normal", "Hard"]

    def replace_block(match: re.Match) -> str:
        title = match.group("title")
        body = match.group("body")

        new_body_lines = []
        link_idx = 0

        for line in body.splitlines():
            link_match = MARKDOWN_LINK_PATTERN.match(line.strip())
            if link_match:
                prob_title = clean_problem_title(link_match.group("title"))
                prob_url = link_match.group("url").strip()

                level_tag = levels[link_idx] if link_idx < len(levels) else f"Level {link_idx + 1}"
                link_idx += 1

                new_line = f"[{level_tag}] [{prob_title}]({prob_url})  "
                new_body_lines.append(new_line)
            else:
                new_body_lines.append(line)

        return f"### 🟨 {title} 문제\n" + "\n".join(new_body_lines) + "\n\n"

    updated_text = DAILY_BLOCK_PATTERN.sub(replace_block, readme_text)
    is_changed = updated_text != readme_text
    return updated_text, is_changed


def generate_daily_folder(
    daily_title: str,
    links: list[tuple[str, str]],
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

    for idx, (problem_title, problem_url) in enumerate(links):
        problem_folder_name = build_problem_folder_name(
            problem_title,
            problem_url,
            idx,
        )

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
                problem_url,
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

        updated_readme_text, is_changed = update_root_readme_with_levels(readme_text)
        if is_changed:
            ROOT_README.write_text(updated_readme_text, encoding="utf-8")
            readme_text = updated_readme_text

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
