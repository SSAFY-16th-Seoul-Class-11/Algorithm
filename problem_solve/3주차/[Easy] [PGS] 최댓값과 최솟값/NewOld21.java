import java.util.*;
class Solution {
    public String solution(String s) {
        
        StringTokenizer st = new StringTokenizer(s);
        int mn = Integer.MAX_VALUE;
        int mx = Integer.MIN_VALUE;
        
        while (st.hasMoreTokens()){
            int str = Integer.parseInt(st.nextToken());
            mn = Math.min(mn, str);
            mx = Math.max(mx, str);
        }
        
        
        return mn + " " + mx;
    }
}