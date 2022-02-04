# KCSC Recruit Memmbers - Encrypted-boizzz

## Description
```
IP
```

**Author**: `nhienit`

# Solution
Nguồn: https://github.com/d47sec/CTF-Writeups/tree/main/EnCryptBoizzz mình viết lại nhằm mục đích cá nhân là note các ý mình chưa hiểu, lưu trữ và ghi nhớ.

At 3 bytes tang 1 block

At 19 bytes tang them 1 block --> Cứ mỗi 16 bytes tăng 1 block--> `16 bytes encryption`


```python
params = {
    'name': 'A' * 32,
}
```
`result`:
```
5673760b1cc65c36 5e93fa8f4317a2c4
16 bytes 'A'    | auth_key + padding    
5673760b1cc65c36 5e93fa8f4317a2c4
16 bytes 'A'    | auth_key + padding
ddef00dfaf0fc11d ed05777122bec5c5
5fec0e7366a611d0 6db4ea75b91cedc3
```
**References**: https://zachgrace.com/posts/attacking-ecb/

1234567891234567 1234567891234567

AAAAAAAAAAAAAAAs cretkeyPPPPPPPPP
               ^
        brute-force this!! --> so sánh với block trước

**Tool exploit**:
```python
import requests
import re # for practice
import string

characters = string.digits + string.ascii_letters # characters for auth key

url = 'http://localhost:2010'
s = requests.Session()

cookies = {
    'PHPSESSID': '3da7886124215d24e99cc58c90072051'
}

def check():
    params = {
        'file': '/tmp/sess_3da7886124215d24e99cc58c90072051'
    }
    r = s.get(url, cookies=cookies, params=params)
    cipher = re.findall('"(.*)"', r.text)[0] # capture group(return)

    return cipher[:16] == cipher[32:48]

auth_key = ''
for i in range(15, -1, -1):
    for c in characters:
        params = {
            'name': 'a' * i + auth_key + c + 'a' * i
        }

        r = s.get(url, cookies=cookies, params=params)

        if check():
            auth_key += c
            print('[+] FOUND: ' + auth_key)
            break
        else:
            print('[-] FAILED at ' + str(i) + ': ' + c)

# AuthKey4N00b3r
```
**Auth key**: `AuthKey4N00b3r`

**flag**: `KCSC{Hello hacker! Hello new member ! Hello our talent <3}`
