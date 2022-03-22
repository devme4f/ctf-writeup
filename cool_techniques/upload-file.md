# Web shell upload via extension blacklist bypass

https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-extension-blacklist-bypass

1. Upload `.php` file --> blocked

2. Upload `.htaccess` file with content: `AddType application/x-httpd-php .l33t` to overwrite the config in upload folder

3. Upload `test.133t` with content: `H7QlufDboB9G6hSrAXj7VziSx0QyLXbb` to get the flag.

# passs

