# RCE khi upload file chỉ cho phép image extension
**References**: https://onestepcode.com/injecting-php-code-to-jpg/

1. Inject php code vào meta information của image, save as image.jpg

*Tools*: exiftool, jhead,..

```bash
jhead -ce file.jpg # The -ce option of jhead will launch a text editor to edit the comment section of the metadata.
# <?php system('find / | grep flag'); __halt_compiler(); ?>
```

2. Khi đọc file thì tất nhiên php code sẽ không được executed bởi file này được xem là jpg. Ở đây cần lợi dụng thêm lỗ hổng nào đó như LFI  để include file này hoặc dựa vào missconfiguration,...

# SQL injection ở websocket

**References**: https://www.notion.so/KMACTF-Web-Challenges-f57e36c0ae244624a32983cbc8462b29

1. Tạo 1 proxy websocket để forward socket requests

2. Dùng sqlmap đục lấy shell như thường

# SSRF2RCE thông qua gopher

**References**: https://www.notion.so/KMACTF-Web-Challenges-f57e36c0ae244624a32983cbc8462b29

Trang web cho phép request tới server bên ngoài và trả về response

1. Fuzz với `Content-Type: application/xml` thì được resp khác (fuzz, enumeration, i know right)

2. Dùng XXE đọc `index.php` file(XML SYSTEM + base64-encode)

3. localhost dạng int(hacktricks)

RCE khi có SSRF hãy nghĩ ngay đến gopherus

4. TCP FastCGI RCE, Do server chạy php với webserver nginx nên thể nghĩ tới việc ssrf tới FastCGI ở port 9000.
