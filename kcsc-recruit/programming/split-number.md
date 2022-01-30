# KCSC Recruit Members - Split Number

## Description
```bash
nc -v 45.77.39.59 9003
```
**Author**: `Lilthawg`

## Solution
Kết nối netcat được responses:
``` 
Challenge 3 : Find the rule of the sequence of numbers and decrypt it(64 questions)
ciphertext = 71111116116973210997107101321211111173211711010010111411511697110100
plaintext = 
```

Nhìn mắt thường chả ra octal cũng chả phải hex, từ tên đề bài là *split* rồi nhìn kĩ mỡi thấy chỉ là `ascii numeber` viết liền nhau, tách ra thử thì đúng thật. Mình cho rằng các chữ cái cũng sẽ chỉ thuộc khoảng 32(space) đến 126(~) thế nên khi tách, lấy khoảng 2 số cho đủ lớn hơn 32, chưa đủ lấy đến 3 số.

**Code**:
```python
from pwn import *

hostname = '45.77.39.59'
port = 9003

def decrypt(cipher):
	sequences = []
	plain = ''
	c = ''

	for i in range(len(cipher)):
		c += cipher[i]
		
		if int(c) >= 32:
			sequences.append(int(c))
			c = ''
	
	plain = [chr(sequences[i]) for i in range(len(sequences))]
	plain = ''.join(plain)

	return plain

s = remote(hostname, port)

try:
	while 1:
		tmp = s.recvlines(2)
		stage = (tmp[1])[13:].decode()
		level = str(decrypt(stage)).encode()
		s.sendline(level)
except:
	print(tmp)
```

**flag**: `KCSC{Fact : It's RickRoll's lyrics}`
