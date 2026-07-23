import java.util.*;
import java.io.*;

class Solution {
    public String solution(String s) {
        StringTokenizer st = new StringTokenizer(s);
        
        List<Integer> list = new ArrayList<>();
        
        while(st.hasMoreTokens()){
            list.add(Integer.parseInt(st.nextToken()));
        }
        
        int min = Integer.MAX_VALUE;
        int max = Integer.MIN_VALUE;
        for (Integer i : list) {
			min = Math.min(min, i);
			max = Math.max(max, i);
		}        
        
        
        return (min + " " + max);
    }
}