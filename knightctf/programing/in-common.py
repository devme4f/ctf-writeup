# Find the GCD of the following numbers and add up the all integers of that GCD and multiply with 1234.
# Number 1: 21525625
# Number 2: 30135875

# Example: The GCD of 50 & 75 is 25.
# Here, 2 + 5 = 7
# So, the flag will be 7 x 1234 = 8638.

x = 21525625
y = 30135875
lon_hon = max(x,y)

# for i in range(int(lon_hon/2)+1, 1, -1):
# 	if x % i == 0 and y % i == 0:
# 		print(i)
# 		break
gcd = 4305125

hello = list(str(gcd))

answer = 0
for i in hello:
	answer += int(i) 

print(answer*1234)