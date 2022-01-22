# Have you ever heard the term "The sum of two squares"?

# It's like the following :

# 4 = 0^2 + 2^2
# 8 = 2^2 + 2^2
# 16 = 0^2 + 4^2
# ----------------------------
# 5002 = 39^2 + 59^2 => 49^2 + 51^2 => 51^2 + 49^2 => 59^2 + 39^2
# And so on. In the example of 16, if we add the square of 0 & 4 we get 16. So here we are getting two values 0 & 4. So that's the answer.

# So write a program & find out the two values of 25000. Conditions are the following :

# * Remove the duplicates
# * Pick the third one

x = 25000 # 1 2 4 8 16


for i in range(500):
	for j in range(500):
		if i**2 + j**2 == x:
			print(f"{i}**2 + {j}**2 == {x}")

# Third one: 90**2 + 130**2 == 25000 --> KCTF{90,130}