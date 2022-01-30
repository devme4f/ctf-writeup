# KCSC Recruit Member - Fibonacchi

## Description
```bash
nc -v 45.77.39.59 9001
```
**Author**: `d47`

## Solution

Mình không nghĩ/muốn/lười cần đi sâu vào thuật toán fibonacchi, mấu chốt bài này có lẽ chỉ là cắt gọt đề tính toán rồi gửi trả.

**Code**:
  
```python
from pwn import *

hostname = '45.77.39.59'
port = 9001

def fibonacci(n):
    f0 = 0;
    f1 = 1;
    fn = 1;
 
    if (n < 0):
        return -1;
    elif (n == 0 or n == 1):
        return n;
    else:
        for i in range(2, n):
            f0 = f1;
            f1 = fn;
            fn = f0 + f1;
        return fn;

# Cắt gọt đề bài rồi trả về để tính toán
def prepare(staged):
    return int((staged.decode())[4:])

s = remote(hostname, port)

# Lần đầu đề kèm ví dụ nên tách ra như này
tmp = s.recvlines(6)
staged = prepare(tmp[5])
level = str(fibonacci(staged)).encode()
s.sendline(level)

# Đến khi lấy đề bài bị lỗi thì tức flag đã về!
try:
	while 1:
		tmp = s.recvlines(2)
		staged = prepare(tmp[1])
		level = str(fibonacci(int(staged))).encode()
		s.sendline(level)
except:
	print(tmp)
```

**flag**: `KCSC{Old_buT_g0ld}`
