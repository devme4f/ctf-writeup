# Find the time complexity of Algorithms.

# procedure max (a1, a2, …, an: integers)
# max := a1
# for i :=2 to n
# if max < a1 then max := ai
# {max is the largest element}
import time

start = time.time()
a = (1,2,3,4,5,6,7,8)

maxie = a[0]

for i in range(1, len(a)-1):
	if maxie < a[i]:
		maxie = a[i]
end = time.time()

print(end-start)