# 第6天

## 浏览器环境
JavaScript可以获取浏览器环境提供的很多对象，并进行操作。

### window
window对象不但充当全局作用域，而且表示浏览器窗口。

window对象有innerWidth和innerHeight属性，可以获取浏览器窗口的内部宽度和高度。内部宽高是指除去菜单栏、工具栏、边框等占位元素后，用于显示网页的净宽高。

```
console.log('window inner size: ' + window.innerWidth + ' x ' + window.innerHeight);
```
对应的，还有一个outerWidth和outerHeight属性，可以获取浏览器窗口的整个宽高。

### navigator
navigator对象表示浏览器的信息，最常用的属性包括：

+ navigator.appName：浏览器名称；
+ navigator.appVersion：浏览器版本；
+ navigator.language：浏览器设置的语言；
+ navigator.platform：操作系统类型；
+ navigator.userAgent：浏览器设定的User-Agent字符串。

```
console.log('appName = ' + navigator.appName);
console.log('appVersion = ' + navigator.appVersion);
console.log('language = ' + navigator.language);
console.log('platform = ' + navigator.platform);
console.log('userAgent = ' + navigator.userAgent);

```


### screen

screen对象表示屏幕的信息，常用的属性有：

+ screen.width：屏幕宽度，以像素为单位；
+ screen.height：屏幕高度，以像素为单位；
+ screen.colorDepth：返回颜色位数，如8、16、24。
```
console.log('Screen size = ' + screen.width + ' x ' + screen.height);
```

location
location对象表示当前页面的URL信息。例如，一个完整的URL：

`http://www.example.com:8080/path/index.html?a=1&b=2#TOP`

可以用location.href获取。要获得URL各个部分的值，可以这么写：
```
location.protocol; // 'http'
location.host; // 'www.example.com'
location.port; // '8080'
location.pathname; // '/path/index.html'
location.search; // '?a=1&b=2'
location.hash; // 'TOP'
```

要加载一个新页面，可以调用location.assign()。如果要重新加载当前页面，调用location.reload()方法非常方便。
```
if (confirm('重新加载当前页' + location.href + '?')) {
    location.reload();
} else {
    location.assign('/'); // 设置一个新的URL地址
}
```

### document
document对象表示当前页面。由于HTML在浏览器中以DOM形式表示为树形结构，document对象就是整个DOM树的根节点。

document的title属性是从HTML文档中的`<title>xxx</title>`读取的，但是可以动态改变：
```
document.title = '努力学习JavaScript!';
```
请观察浏览器窗口标题的变化。

要查找DOM树的某个节点，需要从document对象开始查找。最常用的查找是根据ID和Tag Name。

我们先准备HTML数据：
```
<dl id="drink-menu" style="border:solid 1px #ccc;padding:6px;">
    <dt>摩卡</dt>
    <dd>热摩卡咖啡</dd>
    <dt>酸奶</dt>
    <dd>北京老酸奶</dd>
    <dt>果汁</dt>
    <dd>鲜榨苹果汁</dd>
</dl>
```
用document对象提供的getElementById()和getElementsByTagName()可以按ID获得一个DOM节点和按Tag名称获得一组DOM节点
```
var menu = document.getElementById('drink-menu');
var drinks = document.getElementsByTagName('dt');
var i, s;

s = '提供的饮料有:';
for (i=0; i<drinks.length; i++) {
    s = s + drinks[i].innerHTML + ',';
}
console.log(s);
```

document对象还有一个cookie属性，可以获取当前页面的Cookie。

Cookie是由服务器发送的key-value标示符。因为HTTP协议是无状态的，但是服务器要区分到底是哪个用户发过来的请求，就可以用Cookie来区分。当一个用户成功登录后，服务器发送一个Cookie给浏览器，例如user=ABC123XYZ(加密的字符串)...，此后，浏览器访问该网站时，会在请求头附上这个Cookie，服务器根据Cookie即可区分出用户。

JavaScript可以通过document.cookie读取到当前页面的Cookie：
```
document.cookie;
```

### history
history对象保存了浏览器的历史记录，JavaScript可以调用history对象的back()或forward ()，相当于用户点击了浏览器的“后退”或“前进”按钮。

## 操作dom
由于HTML文档被浏览器解析后就是一棵DOM树，要改变HTML的结构，就需要通过JavaScript来操作DOM。
![img](./Chapter-06-code/pics/pic_htmltree.gif)

始终记住DOM是一个树形结构。操作一个DOM节点实际上就是这么几个操作：

+ 更新：更新该DOM节点的内容，相当于更新了该DOM节点表示的HTML的内容；

+ 遍历：遍历该DOM节点下的子节点，以便进行进一步操作；

+ 添加：在该DOM节点下新增一个子节点，相当于动态增加了一个HTML节点；

+ 删除：将该节点从HTML中删除，相当于删掉了该DOM节点的内容以及它包含的所有子节点。

在操作一个DOM节点前，我们需要通过各种方式先拿到这个DOM节点。最常用的方法是document.getElementById()和document.getElementsByTagName()，以及CSS选择器document.getElementsByClassName()。

由于ID在HTML文档中是唯一的，所以document.getElementById()可以直接定位唯一的一个DOM节点。document.getElementsByTagName()和document.getElementsByClassName()总是返回一组DOM节点。要精确地选择DOM，可以先定位父节点，再从父节点开始选择，以缩小范围。

例如:
```
<style>
.red {
    color: red;
}
</style>

<div id="test">

<table id="test-table" border=10>
  <tr class="red">
    <th>Firstname</th>
    <th>Lastname</th>
    <th>Age</th>
  </tr>
  <tr>
    <td>Jill</td>
    <td>Smith</td>
    <td>50</td>
  </tr>
  <tr>
    <td>Eve</td>
    <td>Jackson</td>
    <td>94</td>
  </tr>
</table>
</div>



// 返回ID为'test'的节点：
var test = document.getElementById('test');

// 先定位ID为'test-table'的节点，再返回其内部所有tr节点：
var trs = document.getElementById('test-table').getElementsByTagName('tr');

// 先定位ID为'test-div'的节点，再返回其内部所有class包含red的节点：
var reds = document.getElementById('test').getElementsByClassName('red');

// 获取节点test下的所有直属子节点:
var cs = test.children;

// 获取节点test下第一个、最后一个子节点：
var first = test.firstElementChild;
var last = test.lastElementChild;
```

第二种方法是使用`querySelector()`和`querySelectorAll()`，需要了解selector语法，然后使用条件来获取节点，更加方便：
```
// 通过querySelector获取ID为test的节点：
var q1 = document.querySelector('#test');

// 通过querySelectorAll获取q1节点内的符合条件的所有节点：
var ps = q1.querySelectorAll('tr.red > th');
```

### 更新DOM
拿到一个DOM节点后，我们可以对它进行更新。

可以直接修改节点的文本，方法有两种：

一种是修改innerHTML属性，这个方式非常强大，不但可以修改一个DOM节点的文本内容，还可以直接通过HTML片段修改DOM节点内部的子树：
```
<p id="p-id">innerhtml</p>

<script>
var p = document.getElementById('p-id');
// 设置文本为abc:
p.innerHTML = 'ABC'; // <p id="p-id">ABC</p>
// 设置HTML:
p.innerHTML = 'ABC <span style="color:red">RED</span> XYZ';

</script>
```

第二种是修改innerText，这样可以设置文本，防止出现`<script>`标签：
```
<p id="p-id">innerhtml</p>

<script>
// 获取<p id="p-id">...</p>
var p = document.getElementById('p-id');
// 设置文本:
p.innerText = '<p>dd</p>';
// HTML被自动编码，无法设置一个<script>节点:

</script>
```

练习
有如下的HTML结构：
```
<!-- HTML结构 -->
<div id="test-div">
  <p id="test-js">javascript</p>
  <p>Java</p>
</div>
```

获取`<p>javascript</p>`节点,修改文本为JavaScript test

答案
```
<!-- HTML结构 -->
<div id="test-div">
  <p id="test-js">javascript</p>
  <p>Java</p>
</div>

<script>

var p = document.getElementById('test-js');

p.innerText = 'JavaScript test';


</script>
```

### 插入DOM 
当我们获得了某个DOM节点，想在这个DOM节点内插入新的DOM，应该如何做？

如果这个DOM节点是空的，例如，`<div></div>`，那么，直接使用`innerHTML = '<span>child</span>'`就可以修改DOM节点的内容，相当于“插入”了新的DOM节点。

如果这个DOM节点不是空的，那就不能这么做，因为innerHTML会直接替换掉原来的所有子节点。

有两个办法可以插入新的节点。一个是使用appendChild，把一个子节点添加到父节点的最后一个子节点。例如：
```
<!-- HTML结构 -->
<p id="js">JavaScript</p>
<div id="list">
    <p id="java">Java</p>
    <p id="python">Python</p>
    <p id="scheme">Scheme</p>
</div>
```

把`<p id="js">JavaScript</p>`添加到`<div id="list">`的最后一项：
```
var js = document.getElementById('js');
var list = document.getElementById('list');
list.appendChild(js);
```

现在，HTML结构变成了这样：
```
<!-- HTML结构 -->
<div id="list">
    <p id="java">Java</p>
    <p id="python">Python</p>
    <p id="scheme">Scheme</p>
    <p id="js">JavaScript</p>
</div>
```

因为我们插入的js节点已经存在于当前的文档树，因此这个节点首先会从原先的位置删除，再插入到新的位置。

更多的时候我们会从零创建一个新的节点，然后插入到指定位置：
```
var
    list = document.getElementById('list'),
    haskell = document.createElement('p');
haskell.id = 'haskell';
haskell.innerText = 'Haskell';
list.appendChild(haskell);
```
document.createElement('p')创建一个p节点
这样我们就动态添加了一个新的节点：
```
<!-- HTML结构 -->
<div id="list">
    <p id="java">Java</p>
    <p id="python">Python</p>
    <p id="scheme">Scheme</p>
    <p id="haskell">Haskell</p>
</div>
```
动态创建一个节点然后添加到DOM树中，可以实现很多功能。举个例子，下面的代码动态创建了一个`<style>`节点，然后把它添加到`<head>`节点的末尾，这样就动态地给文档添加了新的CSS定义：
```
var d = document.createElement('style');
d.setAttribute('type', 'text/css');
d.innerHTML = 'p { color: red }';
document.getElementsByTagName('head')[0].appendChild(d);
```

#### insertBefore

如果我们要把子节点插入到指定的位置怎么办？可以使用parentElement.insertBefore(newElement, referenceElement);，子节点会插入到referenceElement之前。

还是以上面的HTML为例，假定我们要把Haskell插入到Python之前：
```
<!-- HTML结构 -->
<div id="list">
    <p id="java">Java</p>
    <p id="python">Python</p>
    <p id="scheme">Scheme</p>
</div>
```

可以这么写：
```
var
    list = document.getElementById('list'),
    ref = document.getElementById('python'),
    haskell = document.createElement('p');
haskell.id = 'haskell';
haskell.innerText = 'Haskell';
list.insertBefore(haskell, ref);
```
新的HTML结构如下：
```
<!-- HTML结构 -->
<div id="list">
    <p id="java">Java</p>
    <p id="haskell">Haskell</p>
    <p id="python">Python</p>
    <p id="scheme">Scheme</p>
</div>
```

遍历子节点
```
var
    i, c,
    list = document.getElementById('list');
for (i = 0; i < list.children.length; i++) {
    c = list.children[i]; // 拿到第i个子节点
    console.log(c)
}
```

### 删除DOM
删除一个DOM节点就比插入要容易得多。

要删除一个节点，首先要获得该节点本身以及它的父节点，然后，调用父节点的removeChild把自己删掉：
```
<!-- HTML结构 -->
<div id="list">
    <p id="java">Java</p>
    <p id="python">Python</p>
    <p id="scheme">Scheme</p>
</div>

<script>

// 拿到待删除节点:
var self = document.getElementById('scheme');
// 拿到父节点:
var parent = self.parentElement;
// 删除:
var removed = parent.removeChild(self);

</script>
```

## 表单
用JavaScript操作表单和操作DOM是类似的，因为表单本身也是DOM树。

不过表单的输入框、下拉框等可以接收用户输入，所以用JavaScript来操作表单，可以获得用户输入的内容，或者对一个输入框设置新的内容。

HTML表单的输入控件主要有以下几种：
+ 文本框，对应的`<input type="text">`，用于输入文本；
+ 口令框，对应的`<input type="password">`，用于输入口令；
+ 单选框，对应的`<input type="radio">`，用于选择一项；
+ 复选框，对应的`<input type="checkbox">`，用于选择多项；
+ 下拉框，对应的`<select>`，用于选择一项；

隐藏文本，对应的`<input type="hidden">`，用户不可见，但表单提交时会把隐藏文本发送到服务器。

### 获取值
```
<!-- HTML结构 -->
<form>
<input type="text" id="user" value="jiam">
</form>

<script>
var input = document.getElementById('user');
console.log(input.value);
</script>
```

这种方式可以应用于text、password、hidden以及select。但是，对于单选框和复选框，value属性返回的永远是HTML预设的值，而我们需要获得的实际是用户是否“勾上了”选项，所以应该用checked判断：
```
<!-- HTML结构 -->
<form>
<input type="text" id="user" value="jiam">
<label>monday</label>
<input type="radio" name="weekday" id="monday" value="1"> 
<label>tuesday</label>
<input type="radio" name="weekday" id="tuesday" value="2">
</form>

<script>
var mon = document.getElementById('monday');
var tue = document.getElementById('tuesday');
mon.value; // '1'
tue.value; // '2'
mon.checked; // true或者false
tue.checked; // true或者false


</script>
```
### 设置值
设置值和获取值类似，对于text、password、hidden以及select，直接设置value就可以：
```

var input = document.getElementById('user');
input.value = 'jiaminqiang'; // 文本框的内容已更新
tue.checked = true

```
### 提交表单
```
<!-- HTML -->
<form id="test-form">
    <input type="text" name="test">
    <button type="button" onclick="doSubmitForm()">Submit</button>
</form>

<script>
function doSubmitForm() {
    var form = document.getElementById('test-form');
    // 可以在此修改form的input...
    // 提交form:
    form.submit();
}
</script>
```


## 修改css
修改CSS也是经常需要的操作。DOM节点的style属性对应所有的CSS，可以直接获取或设置。因为CSS允许font-size这样的名称，但它并非JavaScript有效的属性名，所以需要在JavaScript中改写为驼峰式命名fontSize：

```
<!-- HTML -->
<p id="p-id">修改css</p>

<script>

var p = document.getElementById('p-id');
// 设置CSS:
p.style.color = '#ff0000';
p.style.fontSize = '20px';
p.style.paddingTop = '2em';
</script>
```



## 事件
因为JavaScript在浏览器中以单线程模式运行，页面加载后，一旦页面上所有的JavaScript代码被执行完后，就只能依赖触发事件来执行JavaScript代码。

浏览器在接收到用户的鼠标，会自动在对应的DOM节点上触发相应的事件。如果该节点已经绑定了对应的JavaScript处理函数，该函数就会自动调用。

常见的HTML事件
下面是一些常见的HTML事件的列表:
```
onchange	HTML 元素改变
onclick	用户点击 HTML 元素
onmouseover	用户在一个HTML元素上移动鼠标
onmouseout	用户从一个HTML元素上移开鼠标
onkeydown	用户按下键盘按键
onload	浏览器已完成页面的加载
```



## ajax
AJAX是Asynchronous JavaScript and XML的缩写，意思就是用JavaScript执行异步网络请求。

如果仔细观察一个Form的提交，你就会发现，一旦用户点击“Submit”按钮，表单开始提交，浏览器就会刷新页面，然后在新页面里告诉你操作是成功了还是失败了。如果不幸由于网络太慢或者其他原因，就会得到一个404页面。

这就是Web的运作原理：一次HTTP请求对应一个页面。

如果要让用户留在当前页面中，同时发出新的HTTP请求，就必须用JavaScript发送这个新请求，接收到数据后，再用JavaScript更新页面，这样一来，用户就感觉自己仍然停留在当前页面，但是数据却可以不断地更新。

在浏览器上写AJAX主要依靠XMLHttpRequest对象：

```
var request = new XMLHttpRequest();
request.open("GET", "/")
request.send()
```




发功一个post请求
```
function encodeFormData(o){
   var s="";
    for (var item in o) {
       s = s + item +"=" + o[item] +"&"     
}
    return  s.substring(0,s.length-1)
}

function callback(request) {
     console.log(request.status)
}

function postData(url, data, callback) {
    var request = new XMLHttpRequest();
    request.open("post", url);
    request.onreadystatechange = function(){
        if ((request.readyState === 4) && callback)
            callback(request);
    };
    request.setRequestHeader("Content-Type",
        "application/x-www-form-urlencode");
    request.send(encodeFormData(data));
}

data = {name:"jia", age:"20"}
url = '/'
postData(url, data ,callback)
```

发送一个带参数的get请求
```
function encodeFormData(o){
   var s="";
    for (var item in o) {
       s = s + item +"=" + o[item] +"&"     
}
    return  s.substring(0,s.length-1)
}

function callback(request) {
     console.log(request.status)
}

function getData(url, data, callback) {
    var request = new XMLHttpRequest();
    request.open("GET", url + "?" + encodeFormData(data));
    request.onreadystatechange = function() {
        if ((request.readyState === 4) && callback)
            callback(request);
    }
    request.send()
}

data = {name:"jia", age:"20"}
url = '/'
getData(url, data, callback)
```
成功处理，失败处理 
```
function success(text) {
    console.log(text)
}

function fail(code) {
   console.log(code)
}

var request = new XMLHttpRequest(); // 新建XMLHttpRequest对象

request.onreadystatechange = function () { // 状态发生变化时，函数被回调
    if (request.readyState === 4) { // 成功完成
        // 判断响应结果:
        if (request.status === 200) {
            // 成功，通过responseText拿到响应的文本:
            return success(request.responseText);
        } else {
            // 失败，根据响应码判断失败原因:
            return fail(request.status);
        }
    } else {
        // HTTP请求还在继续...
    }
}

// 发送请求:
request.open('GET', '/ddd');
request.send();
```

## jquery

使用jQuery只需要在页面的`<head>`引入jQuery文件即可：
```
<html>
<head>
    <script src="http://code.jquery.com/jquery-1.11.3.min.js"></script>
</head>
<body>
</body>
</html>

<script>
console.log('jQuery版本：' + $.fn.jquery);
</script>
```

### $符号


`$`是著名的jQuery符号。实际上，jQuery把所有功能全部封装在一个全局变量jQuery中，而$也是一个合法的变量名，它是变量jQuery的别名：
```
window.jQuery; // jQuery(selector, context)
window.$; // jQuery(selector, context)
$ === jQuery; // true
typeof($); // 'function'
```

$本质上就是一个函数，但是函数也是对象，于是$除了可以直接调用外，也可以有很多其他属性。

注意，你看到的$函数名可能不是jQuery(selector, context)，
```
$ = 1
$ === jQuery;
```


### 选择器



如果某个DOM节点有id属性，利用jQuery查找如下：

```
<html>
<head>
    <script src="http://code.jquery.com/jquery-1.11.3.min.js"></script>
</head>
<body>
<div id="abc">
<p> jquery id </p>
<p> jquery id </p>
</div>
</body>
</html>

<script>
// 查找<div id="abc">:
var div = $('#abc');
div[0]
</script>
```

注意，#abc以#开头。返回的对象是jQuery对象。
什么是jQuery对象？jQuery对象类似数组，它的每个元素都是一个引用了DOM节点的对象。

以上面的查找为例，如果id为abc的<div>存在，返回的jQuery对象如下：
```
m.fn.init [div#abc, context: document, selector: "#abc"]
```
如果id为abc的<div>不存在，返回的jQuery对象如下：
`m.fn.init {context: document, selector: "#d"}`

按tag查找只需要写上tag名称就可以了：
```
var ps = $('p'); // 返回所有<p>节点
ps.length; // 数一数页面有多少个<p>节点
ps[0]
```

按class查找注意在class名称前加一个.：
html
```
<html>
<head>
    <script src="http://code.jquery.com/jquery-1.11.3.min.js"></script>
    <style>
    .red {
          color: red
     }
    </style>
</head>
<body>
<div id="abc">
<p class='red'> jquery id </p>
<p> jquery id </p>
</div>
</body>
</html>
```
script
```
var a = $('.red'); // 所有节点包含`class="red"`都将返回
a[0]
```



一个DOM节点除了id和class外还可以有很多属性
html
```
<html>
<head>
    <script src="http://code.jquery.com/jquery-1.11.3.min.js"></script>
    <style>
    .red {
          color: red
     }
    </style>
</head>
<body>
<form>
<input type="text" id="user" name="user" value="jiam">
<label>monday</label>
<input type="radio" name="weekday" id="monday" value="1"> 
<label>tuesday</label>
<input type="radio" name="weekday" id="tuesday" value="2">
</form>
</body>
</html>
```
javascript
```
var user = $('[name=user]'); 
user[0];
var password = $('[type=password]'); 
password[0];
```

#### 组合查找
如果我们查找`$('[name=user]')`，很可能把表单外的`<div name="user">`也找出来，但我们只希望查找`<input>`，就可以这么写：
html
```
<html>
<head>
    <script src="http://code.jquery.com/jquery-1.11.3.min.js"></script>
    <style>
    .red {
          color: red
     }
    </style>
</head>
<body>
<div name="user">
<form>
<input type="text" id="user" name="user" value="jiam">
<input type="password" id="pasword" name="password" value="1111">
</form>
</div>
</body>
</html>


```
javascript
```
var userInput = $('input[name=user]'); 
userInput[0]
```

同样的，根据tag和class来组合查找也很常见：
```
<html>
<head>
    <script src="http://code.jquery.com/jquery-1.11.3.min.js"></script>
    <style>
    .red {
          color: red
     }
    .green {
          color:  green
     }
    </style>
</head>
<body>


<div id="test">

<table id="test-table">
  <tr class="red">
    <th>Firstname</th>
    <th>Lastname</th>
    <th>Age</th>
  </tr>
  <tr class="green">
    <td>Jill</td>
    <td>Smith</td>
    <td>50</td>
  </tr>
  <tr>
    <td>Eve</td>
    <td>Jackson</td>
    <td>94</td>
  </tr>
</table>
</div>

</body>
</html>


```

javascipt
```
var tr = $('tr.red'); // 找出<tr class="red ...">...</tr>
```
#### 多项选择器
多项选择器就是把多个选择器用,组合起来一块选：
html 同上例
```
$('tr,div'); // 把<tr>和<div>都选出来
$('tr.red,tr.green'); // 把<tr class="red">和<tr class="green">都选出来
```


#### 层级选择器（Descendant Selector）
如果两个DOM元素具有层级关系，就可以用$('ancestor descendant')来选择，层级之间用空格隔开。例如：
```
<html>
<head>
    <script src="http://code.jquery.com/jquery-1.11.3.min.js"></script>
    <style>
    .lang {
          color: red
     }
    .lang-javascript {
          color:  green
     }
    .lang-python{
           color: yellow
     }
    .lang-lua{
           color:  blue
     }
    </style>
</head>
<body>


<div class="testing">
    <ul class="lang">
        <li class="lang-javascript">JavaScript</li>
        <li class="lang-python">Python</li>
        <li class="lang-lua">Lua</li>
    </ul>
</div>

</body>
</html>


```

要选出JavaScript，可以用层级选择器：
```
$('ul.lang li.lang-javascript'); 
$('div.testing li.lang-javascript'); 

```
要选择所有的`<li>`节点，用：
```
$('ul.lang li');
```
#### 子选择器（Child Selector）
子选择器$('parent>child')类似层级选择器，但是限定了层级关系必须是父子关系，就是<child>节点必须是<parent>节点的直属子节点。还是以上面的例子：
```
$('ul.lang>li.lang-javascript'); // 可以选出[<li class="lang-javascript">JavaScript</li>]
$('div.testing>li.lang-javascript'); // [], 无法选出，因为<div>和<li>不构成父子关系
```

#### 过滤器（Filter）
过滤器一般不单独使用，它通常附加在选择器上，帮助我们更精确地定位元素。观察过滤器的效果：
```
$('ul.lang li'); // 选出JavaScript、Python和Lua 3个节点

$('ul.lang li:first-child'); // 仅选出JavaScript
$('ul.lang li:last-child'); // 仅选出Lua
$('ul.lang li:nth-child(2)'); // 选出第N个元素，N从1开始
$('ul.lang li:nth-child(even)'); // 选出序号为偶数的元素
$('ul.lang li:nth-child(odd)'); // 选出序号为奇数的元素
```




### 修改CSS
```
<html>
<head>
    <script src="http://code.jquery.com/jquery-1.11.3.min.js"></script>
    <style>
    .lang {
          color: red
     }
    .lang-javascript {
          color:  green
     }
    .lang-python{
           color: yellow
     }
    .lang-lua{
           color:  blue
     }
    </style>
</head>
<body>
<ul id="test-css">
    <li class="lang"><span>JavaScript</span></li>
    <li class="lang"><span>Java</span></li>
    <li class="lang"><span>Python</span></li>
    <li class="lang"><span>Swift</span></li>
    <li class="lang"><span>Scheme</span></li>
</ul>
</body>
</html>
```

要高亮显示动态语言，调用jQuery对象的css('name', 'value')方法，我们用一行语句实现：
```
$('#test-css li.lang>span').css('background-color', '#ffd351').css('color', 'green');
```
注意，jQuery对象的所有方法都返回一个jQuery对象（可能是新的也可能是自身），这样我们可以进行链式调用，非常方便。

jQuery对象的css()方法可以这么用：
```
var li = $('li');
li.css('color'); // '#000033', 获取CSS属性
```

如果要修改class属性，可以用jQuery提供的下列方法：
```
var div = $('#test-div');
div.hasClass('highlight'); // false， class是否包含highlight
div.addClass('highlight'); // 添加highlight这个class
div.removeClass('highlight'); // 删除highlight这个class
```

## 操作dom
### 修改Text和HTML
jQuery对象的text()和html()方法分别获取节点的文本和原始HTML文本，例如，如下的HTML结构：
```
<html>
<head>
    <script src="http://code.jquery.com/jquery-1.11.3.min.js"></script>
 
</head>
<body>


<div id="test-div" name="test">
<ul id="test-ul">
    <li class="js">JavaScript</li>
    <li name="book">Java &amp; JavaScript</li>
</ul>
</div>
</body>
</html>


```

分别获取文本和HTML：
```
$('#test-ul li[name=book]').text(); // 'Java & JavaScript'
$('#test-ul li[name=book]').html(); // 'Java &amp; JavaScript'
```

设置
```
$('#test-ul li').text('JS'); // 是不是两个节点都变成了JS？
```

### 显示和隐藏DOM
要隐藏一个DOM，我们可以设置CSS的display属性为none，利用css()方法就可以实现。不过，要显示这个DOM就需要恢复原有的display属性，这就得先记下来原有的display属性到底是block还是inline还是别的值。

考虑到显示和隐藏DOM元素使用非常普遍，jQuery直接提供show()和hide()方法，我们不用关心它是如何修改display属性的，总之它能正常工作：

```
var li = $('li');
li.hide(); // 隐藏
li.show(); // 显示
```

注意，隐藏DOM节点并未改变DOM树的结构，它只影响DOM节点的显示。这和删除DOM节点是不同的。

获取DOM信息
利用jQuery对象的若干方法，我们直接可以获取DOM的高宽等信息，而无需针对不同浏览器编写特定代码
```
// 浏览器可视窗口大小:
$(window).width(); // 800
$(window).height(); // 600

// HTML文档大小:
$(document).width(); // 800
$(document).height(); // 3500

// 某个div的大小:
var div = $('#test-div');
div.width(); // 600
div.height(); // 300
div.width(400); // 设置CSS属性 width: 400px，是否生效要看CSS是否有效
div.height('200px'); // 设置CSS属性 height: 200px，是否生效要看CSS是否有效
```

attr()和removeAttr()方法用于操作DOM节点的属性：
···
// <div id="test-div" name="Test" >...</div>
var div = $('#test-div');
div.attr('data'); // undefined, 属性不存在
div.attr('name'); // 'Test'
div.attr('name', 'Hello'); // div的name属性变为'Hello'
div.removeAttr('name'); // 删除name属性
div.attr('name'); // undefined
···

### 操作表单
对于表单元素，jQuery对象统一提供val()方法获取和设置对应的value属性：
```
/*
    <input id="test-input" name="email" value="">
    <select id="test-select" name="city">
        <option value="BJ" selected>Beijing</option>
        <option value="SH">Shanghai</option>
        <option value="SZ">Shenzhen</option>
    </select>
    <textarea id="test-textarea">Hello</textarea>
*/
var
    input = $('#test-input'),
    select = $('#test-select'),
    textarea = $('#test-textarea');

input.val(); // 'test'
input.val('abc@example.com'); // 文本框的内容已变为abc@example.com

select.val(); // 'BJ'
select.val('SH'); // 选择框已变为Shanghai

textarea.val(); // 'Hello'
textarea.val('Hi'); // 文本区域已更新为'Hi'
```

可见，一个val()就统一了各种输入框的取值和赋值的问题。

### 添加节点
要添加新的DOM节点，除了通过jQuery的html()这种暴力方法外，还可以用append()方法，例如：
```
<html>
<head>
    <script src="http://code.jquery.com/jquery-1.11.3.min.js"></script>
 
</head>
<body>


 <div id="test-div">
    <ul>
        <li><span>JavaScript</span></li>
        <li><span>Python</span></li>
        <li><span>Swift</span></li>
    </ul>
</div>
</body>
</html>

```

如何向列表新增一个语言？首先要拿到`<ul>`节点：

`var ul = $('#test-div>ul');`

然后，调用append()传入HTML片段：

`ul.append('<li><span>Haskell</span></li>');`

### 删除节点
要删除DOM节点，拿到jQuery对象后直接调用remove()方法就可以了。如果jQuery对象包含若干DOM节点，实际上可以一次删除多个DOM节点：
```
var li = $('#test-div>ul>li');
li.remove(); // 所有<li>全被删除
```

## 事件
jquery 绑定事件
举个例子，假设要在用户点击了超链接时弹出提示框，我们用jQuery这样绑定一个click事件：

```
<html>
<head>
    <script src="http://code.jquery.com/jquery-1.11.3.min.js"></script>
 
</head>
<body>


 <a id="test-link" href="#0">点我试试</a>
</body>
</html>


```
javascript
```
// 获取超链接的jQuery对象:
var a = $('#test-link');
a.on('click', function () {
    alert('Hello!');
});
```

on方法用来绑定一个事件，我们需要传入事件名称和对应的处理函数。

另一种更简化的写法是直接调用click()方法：
```
a.click(function () {
    alert('Hello!');
});
```

## AJAX
ajax
jQuery在全局对象jQuery（也就是$）绑定了ajax()函数，可以处理AJAX请求。ajax(url, settings)函数需要接收一个URL和一个可选的settings对象，常用的选项如下：

+ async：是否异步执行AJAX请求，默认为true，千万不要指定为false；

+ method：发送的Method，缺省为'GET'，可指定为'POST'、'PUT'等；

+ contentType：发送POST请求的格式，默认值为'application/x-www-form-urlencoded; charset=UTF-8'，也可以指定为text/plain、application/json；

+ data：发送的数据，可以是字符串、数组或object。如果是GET请求，data将被转换成query附加到URL上，如果是POST请求，根据contentType把data序列化成合适的格式；

+ headers：发送的额外的HTTP头，必须是一个object；

+ dataType：接收的数据格式，可以指定为'html'、'xml'、'json'、'text'等，缺省情况下根据响应的Content-Type猜测。

发送一个get请求
```
var jqxhr = $.ajax('/');
// 请求已经发送了
```

对常用的AJAX操作，jQuery提供了一些辅助方法。由于GET请求最常见，所以jQuery提供了get()方法，可以这么写：
```
var jqxhr = $.get('/path/to/resource', {
    name: 'Bob Lee',
    check: 1
});
```

第二个参数如果是object，jQuery自动把它变成query string然后加到URL后面，实际的URL是：

/path/to/resource?name=Bob%20Lee&check=1
这样我们就不用关心如何用URL编码并构造一个query string了。

post
post()和get()类似，但是传入的第二个参数默认被序列化为application/x-www-form-urlencoded：
```
var jqxhr = $.post('/path/to/resource', {
    name: 'Bob Lee',
    check: 1
});
```
实际构造的数据name=Bob%20Lee&check=1作为POST的body被发送。


## 作业
1. 有如下html
```
<div id="test-div">
  <p id="test-js">javascript</p>
  <p>Java</p>
</div>
```
+ 获取`<p>javascript</p>`
+ 修改文本为JavaScript
+ 修改CSS为: color: #ff0000, font-weight: bold

注： 使用javascript 和jquery实现

2. 有如下html
```
<ul id="test-list">
    <li>JavaScript</li>
    <li>Swift</li>
    <li>HTML</li>
    <li>ANSI C</li>
    <li>CSS</li>
    <li>DirectX</li>
</ul>
```
+ 把与Web开发技术不相关的节点删掉
注： 使用javascript和jquery实现

3. 有如下html
```
<div class="test-selector">
    <ul class="test-lang">
        <li class="lang-javascript">JavaScript</li>
        <li class="lang-python">Python</li>
        <li class="lang-lua">Lua</li>
    </ul>
    <ol class="test-lang">
        <li class="lang-swift">Swift</li>
        <li class="lang-java">Java</li>
        <li class="lang-c">C</li>
    </ol>
</div>
```

分别选择所有语言，所有动态语言，所有静态语言
注：  使用javascript和jquery实现

4. 有如下html
```
<form id="test-form" action="#0" onsubmit="return false;">
    <p><label>Name: <input name="name"></label></p>
    <p><label>Email: <input name="email"></label></p>
    <p><label>Password: <input name="password" type="password"></label></p>
    <p>Gender: <label><input name="gender" type="radio" value="m" checked> Male</label> <label><input name="gender" type="radio" value="f"> Female</label></p>
    <p><label>City: <select name="city">
    	<option value="BJ" selected>Beijing</option>
    	<option value="SH">Shanghai</option>
    	<option value="CD">Chengdu</option>
    	<option value="XM">Xiamen</option>
    </select></label></p>
    <p><button type="submit">Submit</button></p>
</form>
```

输入值后，用jQuery获取表单的JSON字符串，key和value分别对应每个输入的name和相应的value，例如：{"name":"Michael","email":...}

5. 有如下html
```
<form id="test-register" action="#" target="_blank" onsubmit="checkRegisterForm()">
    <p id="test-error" style="color:red"></p>
    <p>
        用户名: <input type="text" id="username" name="username">
    </p>
    <p>
        口令: <input type="password" id="password" name="password">
    </p>
    <p>
        重复口令: <input type="password" id="password-2">
    </p>
    <p>
        <button type="submit">提交</button> <button type="reset">重置</button>
    </p>
</form>
```
利用JavaScript检查用户注册信息是否正确，在以下情况不满足时报错并阻止提交表单：

+ 用户名必须是3-10位英文字母或数字；

+ 口令必须是6-20位；

+ 两次输入口令必须一致。

提示: 编写checkRegisterForm() 函数, 当函数返回值为ture 是表单提交，返回值为false表单不提交
检查失败时调用alert() 弹窗 并返回false

6. 有如下html：
```
<!-- HTML结构 -->
<form id="test-form" action="test">
    <legend>请选择想要学习的编程语言：</legend>
    <fieldset>
        <p><label class="selectAll"><input type="checkbox"> <span class="selectAll">全选</span><span class="deselectAll">全不选</span></label> 
        <p><label><input type="checkbox" name="lang" value="javascript"> JavaScript</label></p>
        <p><label><input type="checkbox" name="lang" value="python"> Python</label></p>
        <p><label><input type="checkbox" name="lang" value="ruby"> Ruby</label></p>
        <p><label><input type="checkbox" name="lang" value="haskell"> Haskell</label></p>
        <p><label><input type="checkbox" name="lang" value="scheme"> Scheme</label></p>
		<p><button type="submit">Submit</button></p>
    </fieldset>
</form>
```

1. 当用户勾上“全选”时，自动选中所有语言，并把“全选”变成“全不选”；

2. 当用户去掉“全不选”时，自动不选中所有语言；