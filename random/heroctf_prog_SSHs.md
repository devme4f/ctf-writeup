# HeroCTF - SSHs

**Description**: Một bài programing, cho username và password để SSH vào challenge(bắt đầu với user1), sau khi login vào thì nó cho `private_key` của `user2`.

Hướng giải đơn giản thôi, tạo script ssh vào từng user cho đến user thứ 250 là nó chứa flag(trong description).

**Search keyword**: `python ssh socket` tìm được đoạn code rồi edit tí là được: https://0xbharath.github.io/python-network-programming/protocols/ssh/index.html

```python
#!/usr/bin/env python3
import paramiko, sys, getpass

hostname = "chall.heroctf.fr"
username = "user{}"
password = "password123"
port = 10172
key = ''


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
client.connect(hostname, username=username.format(1), password=password, port=port)

stdin, stdout, stderr = client.exec_command('./getSSHKey')
stdin.close()	

out = stdout.readlines()
for line in out:
	key += line

with open('id_rsa', 'w') as f:
	f.write(key)

stdout.close()
stderr.close()
client.close()

for i in range(2, 249):
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
	client.connect(hostname, username=username.format(248), key_filename='./id_rsa', port=port)
	key = ''

	stdin, stdout, stderr = client.exec_command('cat *')
	stdin.close()	

	out = stdout.readlines()
	for line in out:
		key += line

	with open('id_rsa', 'w') as f:
		f.write(key)
	stdout.close()
	stderr.close()
	client.close()
	if i % 10 == 0:
		print(key)
		print()

print(key)
```
**flag**: `Hero{Th47_w3RE_4_l0t_Of_uS3rS} `
