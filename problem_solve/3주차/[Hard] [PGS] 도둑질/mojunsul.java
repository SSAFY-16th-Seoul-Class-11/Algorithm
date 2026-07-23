class Solution {
	
	static int[] dp1;
	static int[] dp2;
	static int N;
	static int[] money;
	
    public int solution(int[] input) {
    	money = input;
        N = money.length;
        dp1 = new int[N]; // [idx까지 확인했을 때][0: 안털림, 1: 털림][시작점 털림 유무]
        dp2 = new int[N];
        
        //시작 안턺
        int sum = 0;
        for(int i=1; i<N; i++) {
        	dp1[i] = Math.max(dp1[i-1], dp2[i-1]);
        	dp2[i] = dp1[i-1] + money[i];
        }
        int ans = Math.max(dp1[N-1], dp2[N-1]);
        
        //시작 턺
        dp1 = new int[N];
        dp2 = new int[N];
        dp2[0] = money[0];
        sum = 0;
        for(int i=1; i<N-1; i++) {
        	dp1[i] = Math.max(dp1[i-1], dp2[i-1]);
        	dp2[i] = dp1[i-1] + money[i];
        }
        ans = Math.max(ans, Math.max(dp1[N-2], dp2[N-2]));
        return ans;
    }
}