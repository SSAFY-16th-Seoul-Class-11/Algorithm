import java.util.*;

class Solution {
    boolean solution(String s) {
        boolean answer = true;
        
        Stack<Object> stack = new Stack();
        
        char[] input = s.toCharArray();
        for (char c : input) {
			if(c=='(') {
				stack.push(null);
			}
			else {
				if(stack.isEmpty()) {
					answer = false;
					return false;
				}
				stack.pop();
			}
		}
        answer = stack.isEmpty();
        return answer;
    }
}