# KCSC Recruit Members - Sum
## Description
```bash
nc -v 45.77.39.59 9005
```
**Author**: `d47`

## Solution
Kết nối netcat được responses:

``` 
Challenge 5 : Given an array of integers nums and an integer target. Count all pairs in the array whose sum is equal to the target.
Ex:
Nums = [1,2,3,4], Target = 5 => Answer = 2
Explain: 1 + 4 = 5  and 2 + 3 = 5

Nums = [5, 39, 104, 343, 20, 14], Target = 25  => Answer = 1
Explain: 5 + 20 = 25

Nums = [1,2], Target = 5 => Answer = 0

Nums = [21, 59, 27, 4, 91, 50, 102, 120, 2, 106, 68, 60, 71, 19, 19, 27]
Target = 122
Answer = 
```
Sử dụng two pointer techniques. Đề hint thế rồi vẫn không làm được thì ... [:(]
**Refrences**: `https://algodaily.com/lessons/using-the-two-pointer-technique`

**Code**:
```python
from pwn import *

hostname = '45.77.39.59'
port = 9005

# Sắp xếp mảng rồi cộng từ hai đầu(l >-< r) vào -> không sợ lặp
# Lấy được pair rút l và r(ko xài lại), bé hơn rút l else rút r
def solve(Nums, target):
    l = 0
    r = len(Nums) - 1
    cnt = 0
    Nums.sort()
    while(l < r):
        if(Nums[l] + Nums[r] == target):
            l += 1
            r -= 1
            cnt+=1
        elif(Nums[l] + Nums[r] < target):
            l+=1
        else:
            r-=1
    return cnt

def prepare(arr1, target1):
    arr2 = ((arr1[8:])[:-1]).decode().split(', ')
    target = int(target1[9:])

    arr = []
    for i in arr2:
        arr.append(int(i))

    return arr, target

s = remote(hostname, port)

tmp = s.recvlines(12)
arr, target = prepare(tmp[10], tmp[11])
level = str(solve(arr, target)).encode()
s.sendline(level)
    
try:
    while 1:
        tmp = s.recvlines(3)
        arr, target = prepare(tmp[1], tmp[2])
        level = str(solve(arr, target)).encode()
        s.sendline(level)
except:
    print(s.recvlines(2))
```

**flag**: `KCSC{Before_you_learn_hacking_you_should_learn_programming}`
