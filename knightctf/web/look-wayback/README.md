# Knight CTF - Sometime you need to look wayback

Inspect web-page from chrome, we found a link to the source-code:
<!--Test Bot Source Code: https://github.com/KCTF202x/repo101-->

hint: look wayback --> ok -->  let Viewing the Commit History
```bash
# clone it to our machine
git clone https://github.com/KCTF202x/repo101.git
git log
# commit 74bf8c5679108c685d4c52dd18c191d605b53977
# Author: KCTF202x <knightsquad.knight.vii@gmail.com>
# Date:   Tue Dec 28 03:42:56 2021 +0600

#     KCTF{version_control_is_awesome}
```
**flag**: KCTF{version_control_is_awesome}