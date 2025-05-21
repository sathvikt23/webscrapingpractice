
def binarysearch(data , target ):
    start = 0 
    end = len(data)
    mid =(start+end)//2

    while (start<end ):
        mid =(start+end)//2
        if (data[mid]==target):
            return mid 
        if (target>data[mid]):
            start=mid+1
        else :
            end=mid
    return -1 

data=[0,1,2,3,4,5,6]

print(binarysearch(data,4))

