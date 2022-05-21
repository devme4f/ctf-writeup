# m0leCon teaser 2022

## Dumb Forum
Website forum, có chức năng đăng kí rồi đăng nhập. Sau khi đăng nhập ta có thể viết và đăng lên 1 trang forums chung và có 1 tab cho xem thông tin tài khoản.
Chall này cho *sourcec-code*, review thì thấy hầu hết các `route` filter  `{` và `}` bằng hàm `validate_on_submit()`, ngoại trừ chỗ email, test thử `{{7*'7'}}` ta biết website dính SSTI chỗ register phần email.

Tuy nhiên phần email lại bị block 1 số kí tự khác như `(`, `)`, `[` và `]` nên ta không thể SSTI chọn elements hay gọi hàm/method, thử bypass cũng không thể, ngồi loay hoay tìm cách RCE không được.

Đọc lại file `config.py` mới đơ người:

```python
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "db", "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

Vâng `os.environ`, có mắt như \*\*, vậy để có được flag ta chỉ cần đọc được các enviroment variables mà không cần bypass các ký tự trên(bởi không thể) để RCE.

Module `os` của python có object `environ` chứa tất cả các biến môi trường, dùng class `cyler` ta tìm được đến constructor `init` và nhờ đó gọi được đến module `os` rồi form được payload sau

```python
{{cyler.init.globals.os.environ}}
```

Đặt email là: `{{joiner.init.globals.os.environ}}@a.b`, login vào profile ta được flag

Vào đến tab tài khoản chỗ email ta được các env variables cũng flag

..........

**FLAG**: `ptm{d1d_u_f1nd_th3_r1ckr0ll?}`

## Hash Length Extension atack, write-up


pass
