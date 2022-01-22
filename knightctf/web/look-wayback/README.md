# Knight CTF - Sometime you need to look wayback

View source-code, we found a comment, which is a link to the github source-code of the web app:
```
Test Bot Source Code: https://github.com/KCTF202x/repo101
```

**hints**: look wayback --> ok -->  let Viewing the Commit History
```bash
# clone it to our machine
git clone https://github.com/KCTF202x/repo101.git
git log --all
# commit 74bf8c5679108c685d4c52dd18c191d605b53977
# Author: KCTF202x <knightsquad.knight.vii@gmail.com>
# Date:   Tue Dec 28 03:42:56 2021 +0600
```

**flag**: `KCTF{version_control_is_awesome}`
