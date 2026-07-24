import java.util.ArrayDeque;
import java.util.Queue;

class Main {
    public static void main(String[] args) throws Exception {

    }

    class Solution {
        public int solution(int n, int[][] computers) {
            Queue<Integer> queue = new ArrayDeque<>();
            boolean[] visited = new boolean[n];
            int answer = 0;

            for (int i = 0; i < n; i++) {
                if (!visited[i]) {
                    queue.offer(i);
                    visited[i] = true;

                    while (!queue.isEmpty()) {
                        int curr = queue.poll();
                        for (int j = 0; j < n; j++) {
                            if (computers[curr][j] == 1 && !visited[j]) {
                                queue.offer(j);
                                visited[j] = true;
                            }
                        }
                    }
                    answer++;
                }
            }

            return answer;
        }
    }
}
