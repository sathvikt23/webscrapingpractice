"""input : "aaaabbbcca"
output : [("a",5),("b",3),("c",2)]"""
"""output :[{"a":5},]"""
import copy
ans ={}
data="aaaabbbcca"
cord={}
ans2=[]
c=0
for i in range(len(data)):
    
        if (data[i] in cord ):
            temp=ans2[cord[data[i]]]
            temp[1]+=1
            ans2[cord[data[i]]]=temp
        else :
          cord[data[i]]=c
          ans2.append([data[i],1])
          c+=1
    
    
print(ans2)

