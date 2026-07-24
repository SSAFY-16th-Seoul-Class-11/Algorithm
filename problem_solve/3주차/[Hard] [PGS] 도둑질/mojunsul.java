class Solution {
		
    public int solution(int[] money) {
    	int N = money.length;
        int[][] dp = new int[2][N];

        dp[0][0] = 0;
        dp[0][1] = money[1];
        dp[1][0] = money[0];
        dp[1][1] = money[0];

        for(int idx=2; idx<N; idx++) {
        	for(int isFirstRobbed=0; isFirstRobbed<2; isFirstRobbed++) {
        		dp[isFirstRobbed][idx] = Math.max(dp[isFirstRobbed][idx-2] + money[idx], dp[isFirstRobbed][idx-1]);
        	}
        }
        
        return Math.max(dp[0][N-1], dp[1][N-1]);
    }
}