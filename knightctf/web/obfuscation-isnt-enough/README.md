# Knight CTF - Obsfuscation Isn't Enough

A login form that validate by javascript being obfuscation:

format: ([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[+[]]+(+[![]]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])[+!+[]+[+!+[

--> `JSFuck`

auto deobfuscator online tool: https://www.dcode.fr/javascript-unobfuscator

**result**:
```javascript
function validate() {
	if (document.forms[0].username.value == "83fe2a837a4d4eec61bd47368d86afd6" && document.forms[0].password.value == "a3fa67479e47116a4d6439120400b057") document.location = "150484514b6eeb1d99da836d95f6671d.php"
	}
```
path: http://159.223.166.39:20002/150484514b6eeb1d99da836d95f6671d.php

**flag**: KCTF{0bfuscat3d_J4v4Scr1pt_aka_JSFuck}
