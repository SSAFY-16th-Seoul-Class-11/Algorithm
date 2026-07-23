
class Solution {
    public String solution(String s) {
        StringTokenizer st = new StringTokenizer(s);
        int min = Integer.MAX_VALUE;
        int max = Integer.MIN_VALUE;

        int len = st.countTokens();
        for (int i = 0; i < len; i++) {
            int num = Integer.parseInt(st.nextToken());
            min = Math.min(min, num);
            max = Math.max(max, num);
        }

        String answer = min + " " + max;
        return answer;
    }
}