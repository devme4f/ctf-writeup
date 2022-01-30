# KCSC Recruit Members - Permutation

## Description
```bash
nc -v 45.77.39.59 9004
```
**Author**: `Lilthawg`

## Solution
Kết nối netcat được responses:
``` 
Challenge 4 : (64 questions)
Ex:
S = T8P1V5ExmPLxIurhx2Sth2LwK812Uc23iYCKSwAYBDvqRrsCMce4lU7003md6P7I
answer = 1120451928826474826454528078636959577515085681054726284511017749708800000000000000

S = lethethang
answer = 453600

S = loK8Xaiuq98SKgWkl2Hx9sicEfOAOxzfNRfv5lsYpKXkeJmqHsYdQw8WhB9EMyn8
How many different strings can be generated from string S?
answer = 
```
**Refrences**: `https://vnhoctap.com/hoan-vi-lap/`

**Ờ, trông dễ thế sao \*\*o giải được**: Trước nay mình chỉ dùng python để viết tool web exploit, mặc dù đã giải ra gần đúng kết quả với sai số nhưng không 1 lần để ý thử làm tròn số trong python mà ép về *interger* bằng `int()`. Để làm tròn số khi chia ta dùng `floor division(//)`.

Lý do hay đó, thôi im lặng đưa code đây!

**Code**:

```python
from pwn import *
import math

hostname = '45.77.39.59'
port = 9004

def count(S):
    tu = len(S)
    mau = 1
    count = 0

    for c in set(S): # set to remove duplicate characters
        count = S.count(c)
        if count > 1:
            mau *= math.factorial(count)
    return int(math.factorial(tu)//mau)

s = remote(hostname, port)

tmp = s.recvlines(10)

S = (tmp[8])[4:].decode()
level = str(count(S)).encode()
s.sendline(level)

try:
    while 1:
        tmp = s.recvlines(3)
        S = (tmp[1])[4:].decode()
        level = str(count(S)).encode()
        s.sendline(level)
except:
    print(s.recvlines(2))
```

**flag**: `KCSC{Amazingg ! Were you good at math in high school?}`
