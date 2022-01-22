import hashlib

print('Running.......!')
for i in range(807097110, 1500000000):
	md5 = hashlib.md5(f'0e{i}'.encode()).hexdigest()
	if md5[:2] == '0e' and md5[2:].isnumeric():
		print(f'[FOUND] - 0e{i} : ' + md5)
		break