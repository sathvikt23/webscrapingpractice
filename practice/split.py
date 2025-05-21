
import copy


a=[23]

b=copy.copy(a)
b=[30]
c=copy.deepcopy(a)
c=[25]
print(a)
print(c)


def split_array(arr, n):
    size = len(arr) // n
    ans =[]
    c=0
    temp=[]
    for i in range(len(arr)):
        if (c==size):
            ans.append(copy.copy(temp))
            temp=[]
            c=0
        c+=1
        temp.append(arr[i])
    print(ans)
def splitt(arr,ans,start,classes,size):
    if (start>=len(arr)):
        return 
    if (classes==size):
        print(ans)
        return 
    temp=[]
    for i in range(start,len(arr)):
        temp.append(arr[i])
        ans.append(copy.copy(temp))
        splitt(arr,ans,i+1,classes+1,size)
        ans.pop(len(ans)-1)


# Example
arr = [1, 2, 3, 4, 5, 6]
n = 3
splitt(arr,[], 0,0,2)

