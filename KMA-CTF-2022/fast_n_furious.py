from pwn import *

hostname = '103.28.172.12'
port = 1111

def prepare(result):
	raw = ((result.decode())[1:])[:-1].split(' ')
	sortable = [int(i) for i in raw]
	level_sorted = sorted(sortable)
	level = '['
	for i in level_sorted:
	    level += str(i) + ' '
	level = level[:-1] + ']'

	return level.encode()

s = remote(hostname, port)

level2 = prepare((s.recvlines(8))[7])
s.sendline(level2)

try:
	while 1:
		level = prepare((s.recvlines(3))[2])
		s.sendline(level)
except:
	print(s.recvlines(1))

# Done, here is your flag: KMACTF{F4st_n_Fur10us_BigInt}
