

def knapsack(weights,values , start ,capacity):

    if (capacity<=0 or start>=len(values)):
        return 0
    if(dp[start][capacity]!=-1):
       return dp[start][capacity]
    skip =knapsack(weights,values,start+1,capacity)
    take=0
    if weights[start]<=capacity:
     take =knapsack(weights,values,start+1,capacity-weights[start])+values[start]
    dp[start][capacity]=max(skip,take)
    return max(skip,take)
weights=[2, 3, 4, 5]

values= [3, 4, 5, 6]
capacity=5
dp=[[-1 for i in range(capacity+1)] for j in range(len(values)+1) ]
print(knapsack(weights,values,0,capacity))