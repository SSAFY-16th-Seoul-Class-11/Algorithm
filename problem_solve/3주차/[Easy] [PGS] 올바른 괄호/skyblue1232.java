import java.util.*;

public class Main {

    public static void main(String[] args) {
        Solution sol = new Solution();

        System.out.println(sol.solution("()()"));    // true
        System.out.println(sol.solution("(())()"));  // true
        System.out.println(sol.solution(")()("));    // false
        System.out.println(sol.solution("(()("));    // false
    }
}

class Solution {

    boolean solution(String s) {
        boolean answer = true;

        Deque<Character> stack = new ArrayDeque<>();
        
        for(int i=0; i<s.length(); i++) {
        	char c = s.charAt(i);
        	
        	if(c=='(') {
        		stack.push(c);
        	} else {
        		
        		if(stack.isEmpty()) {
        			return false;
        		}
        		
        		stack.pop();
        	}
        }

        return stack.isEmpty();
    }
}
