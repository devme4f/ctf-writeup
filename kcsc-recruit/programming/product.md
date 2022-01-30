# KCSC Recruit Members - Product
## Description
```bash
nc -v 45.77.39.59 9002
```
**Author**: `Lilthawg`

## Solution

Kết nối netcat được response:
```
Challenge 2 : Calculate the product of the numbers in the array, answer them all correctly and you will get a flag(64 questions)
Ex:
arr = [30, 8, 43, 11, 43, 14, 30, 48, 29, 26, 15, 50, 4, 62, 53, 5] => answer = 3657307948310016000000

arr = [52, 31, 31, 60, 12, 8, 39, 56, 62, 2, 12, 19, 29, 44, 30, 44]
answer = 
```

Đề cho 1 array và answer, answer số to thế chắc là phần tử array nhân nhau, thử thì đúng thế thật.

**Code**:

```python
from pwn import *

hostname = '45.77.39.59'
port = 9002

# Tính toán
def cal(arr):
    result = 1
    for i in arr:
        result *= i
    return result

# Cắt gọt đề bài
def prepare(raw):
    cutted = ((raw.decode())[7:])[:-1].split(', ')
    arr = []
    for i in cutted:
        arr.append(int(i))

    return arr

s = remote(hostname, port)

# Lấy đề bài, lần đầu có ví dụ nên tách ra như này
tmp = s.recvlines(5)
staged = prepare(tmp[4])
level = str(cal(staged)).encode()
s.sendline(level)

# Lấy đề bài lỗi thì chắc flag về rồi!
try:
    while 1:
        tmp = s.recvlines(2)
        staged = prepare(tmp[1])
        level = str(cal(staged)).encode()
        s.sendline(level)
except:
	print(tmp)
```

**flag**: `KCSC{y0u_s0_G0od_at_ProGraMm1n9}`
