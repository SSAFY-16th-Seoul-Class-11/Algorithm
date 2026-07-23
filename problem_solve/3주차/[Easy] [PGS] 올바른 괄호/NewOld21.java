class Solution {
    boolean solution(String s) {
        boolean answer = false;
        int cnt = 0;
        for(int i=0; i<s.length(); i++){
            char c = s.charAt(i);
            if(cnt < 0)
                break;
            if(c=='(')
                cnt++;
            else
                cnt--;
        }
        if(cnt==0)
            answer = true;
        return answer;
    }
}