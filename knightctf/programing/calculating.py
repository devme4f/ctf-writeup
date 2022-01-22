# Let x = 1
# Let y = 2
# Let answer += (x * y) + xy [here xy = 12]
# Repeat this calculation till you have x = 666
# The final answer will be the flag when x = 666

x = 1
y = 2

answer = 0

while x<=666:
	answer += (x*y) + int(str(x) + str(y))
	x += 1
print(answer)