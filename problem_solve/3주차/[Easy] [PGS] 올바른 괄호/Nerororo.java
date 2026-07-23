import java.util.Deque;
import java.util.ArrayDeque;

class Solution {
    boolean solution(String s) {
        boolean answer = true;
        Deque<Character> stack = new ArrayDeque<>();

        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '(') stack.offer('(');
            else {
                if (stack.isEmpty()) {
                    answer = false;
                    break;
                }
                stack.pollLast();
            }
        }
        if (!stack.isEmpty()) answer = false;
        return answer;
    }
}