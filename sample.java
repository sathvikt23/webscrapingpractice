import java.util.*;

public class sample {
    public static HashSet<Integer> set = new HashSet<>();
    public static void  find (Map<Integer,List<Integer>> map ,ArrayList<Integer> temp ,int visited [], int p , int n){

        if (p==n){
           set.addAll(temp);
           return ;
        }

        
        //boolean temp []= new boolean [1];
        for (int i=0 ; i<map.get(p).size();i++ ){
            
            if (visited[map.get(p).get(i)]==0){
            visited[map.get(p).get(i)]=1;
            temp.add(map.get(p).get(i));

            find(map,temp,visited,map.get(p).get(i),n);
            visited[map.get(p).get(i)]=0;
            temp.remove(temp.size()-1);
            }

            
        }
        return ;
        
        
    }
    public static void main (String args []){
        Map<Integer, List<Integer>> graph = new HashMap<>();
        graph.put(1, Arrays.asList(2, 3));    // 1 connected to 2 and 3
        graph.put(2, Arrays.asList(1, 4));    // 2 connected to 1 and 4
        graph.put(3, Arrays.asList(1));       // 3 connected to 1
        graph.put(4, Arrays.asList(2, 5));    // 4 connected to 2 and 5
        graph.put(5, Arrays.asList(4));     
        int visited[] = new int [6];
        find(graph, new ArrayList<>(),visited , 2, 5);
        System.out.println(set.size()-1);

    }
}