class Solution {
	
	static int N, cnt;
	static int[][] coms;
	static boolean[] isVisited;
	
    public int solution(int n, int[][] computers) {
        N =n;
    	coms = computers;
        isVisited = new boolean[n];
        
        for (int i = 0; i < n; i++) {
			if(!isVisited[i]) {
				dfs(i);
				cnt++;
			}
		}
        
        return cnt;
    }

	private void dfs(int cur) {
		isVisited[cur] = true;
		for (int next = 0; next < N; next++) {
			if(coms[cur][next] == 1 && !isVisited[next]) {
				dfs(next);
			}
		}
		
	}
}
