import java.util.*;

class Solution {
    public int solution(int N, int[][] computers) {
        int answer = 0;
        int [] net = new int[N];
        
        Queue<Integer> q = new LinkedList<>();
        for(int i=0; i<N; i++){
            if(net[i] == 0){
                answer++;
                q.add(i);
                while(!q.isEmpty()){
                    int idx = q.remove();
                    if(net[idx] == 0){
                        net[idx] = 1;
                        for(int j=0; j<N; j++){
                            if(computers[idx][j]==1 && net[j]==0){
                                q.add(j);
                            }
                        }    
                    }
                }
            }
        }
        
        return answer;
    }
}