# 第十一天

## debugtalk.py管理
每一个项目里都要有一个debugtalk.py文件用来定义一些函数，用来被配置文件引用

### 在models.py里添加 DebugTalk类

```
class DebugTalk(BaseTable):
    class Meta:
        verbose_name = '驱动py文件'
        db_table = 'DebugTalk'

    belong_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    debugtalk = models.TextField(null=True, default='#debugtalk.py')
```
执行数据迁移命令

### 修改project_add 视图
修改project_add视图，在添加project时同时添加一个与之关联的debugtalk记录
在`p.save()` 添加下面三行代码
```
            p.save()
            d = DebugTalk()
            d.belong_project = p
            d.save()
```

### 添加debugtalk_list 视图

```
def debugtalk_list(request):
    pass
```

### 添加debugtalk/list url
```
path('debugtalk/list', views.debugtalk_list, name='debugtalk_list'),
```
### 修改debugtalk_list 视图
```
def debugtalk_list(request):
    if request.method == "GET":
        rs = DebugTalk.objects.all().order_by("-update_time")
        paginator = Paginator(rs,5)
        page = request.GET.get('page')
        objects = paginator.get_page(page)
        context_dict = {'debugtalk': objects }
        return render(request,"debugtalk_list.html",context_dict)
```

### 添加debugtalk_list.html模板

[debugtalk_list.html](./Chapter-11-code/hat/templates/debugtalk_list.html)

测试,访问http://127.0.0.1:8000/httpapitest/debugtalk/list
在base.html模板中，添加debugtalk.py 的菜单


### 添加debugtalk视图
debugtalk视图用来编辑debugtalk.py内容

```
def debugtalk_edit(request, id):
    if request.method == "GET":
        d = DebugTalk.objects.get(pk=id)
        context_dict = {'debugtalk': d.debugtalk, 'id': d.id }
        return render(request, "debugtalk_edit.html",context_dict)
```

### 添加debugtalk/edit url
```
path('debugtalk/edit/<int:id>', views.debugtalk_edit, name='debugtalk_edit'),
```

### 添加debugtalk_edit 模板
[debugtalk_edit.html](./Chapter-11-code/hat/templates/debugtalk_edit.html)


在commons.js 文件中添加函数init_acs

```
function init_acs(language, theme, editor) {
    editor.setTheme("ace/theme/" + theme);
    editor.session.setMode("ace/mode/" + language);

    editor.setFontSize(17);

    editor.setReadOnly(false);

    editor.setOption("wrap", "free");

    ace.require("ace/ext/language_tools");
    editor.setOptions({
        enableBasicAutocompletion: true,
        enableSnippets: true,
        enableLiveAutocompletion: true,
        autoScrollEditorIntoView: true
    });


}
```

修改debugtalk_edit视图，用来保存提交的代码

```
@csrf_exempt
def debugtalk_edit(request, id):
    if request.method == "GET":
        d = DebugTalk.objects.get(pk=id)
        context_dict = {'debugtalk': d.debugtalk, 'id': d.id }
        return render(request, "debugtalk_edit.html",context_dict)

    if request.method == "POST":
        d = DebugTalk.objects.get(pk=id)
        debugtalk = request.POST.get('debugtalk')
        code = debugtalk.replace('new_line', '\r\n')
        d.debugtalk = code
        d.save()
        return redirect(reverse('debugtalk_list'))
```

测试，打开编辑页面修改代码然后提交

## 配置管理

### 添加配置

添加model 类TestConfig
```
class TestConfig(BaseTable):
    class Meta:
        verbose_name = '配置信息'
        db_table = 'TestConfigInfo'
    name = models.CharField('配置名称', max_length=50, null=False)
    belong_project = models.CharField('所属项目', max_length=50, null=False)
    belong_module = models.ForeignKey(Module, on_delete=models.CASCADE)
    author = models.CharField('编写人员', max_length=20, null=False)
    request = models.TextField('请求信息', null=False)
```

添加view config_add

```
def config_add(request):
    if request.method == 'GET':
        context_dict = {
            'project': Project.objects.all().values('project_name').order_by('-create_time')
        }
        return render(request, 'config_add.html', context_dict)
```

添加url 
```
path('config/add', views.config_add, name='config_add'),
```

添加模板config_add.html

[config_add.html](./Chapter-11-code/hat/templates/config_add.html)

在commons.js中添加 config_ajax

```
function config_ajax(type) {
    var dataType = $("#config_data_type").serializeJSON();
    var caseInfo = $("#form_config").serializeJSON();
    var variables = $("#config_variables").serializeJSON();
    var parameters = $('#config_params').serializeJSON();
    var hooks = $('#config_hooks').serializeJSON();
    var request_data = null;
    if (dataType.DataType === 'json') {
        try {
            request_data = eval('(' + editor.session.getValue() + ')');
        }
        catch (err) {
            myAlert('Json格式输入有误！');
            return
        }
    } else {
        request_data = $("#config_request_data").serializeJSON();
    }
    var headers = $("#config_request_headers").serializeJSON();

    const config = {
        "config": {
            "name": caseInfo,
            "variables": variables,
            "parameters": parameters,
            "request": {
                "headers": headers,
                "type": dataType.DataType,
                "request_data": request_data
            },
            "hooks": hooks,

        }
    };
    if (type === 'edit') {
        url = '#';
    } else {
        url = '/httpapitest/config/add';
    }
    $.ajax({
        type: 'post',
        url: url,
        data: JSON.stringify(config),
        contentType: "application/json",
        success: function (data) {
            if (data === 'session invalid') {
                window.location.href = "/httpapitest/login/";
            } else {
                if (data.indexOf('/httpapitest') != -1) {
                    window.location.href = data;
                } else {
                    myAlert(data);
                }
            }
        },
        error: function () {
            myAlert('Sorry，服务器可能开小差啦, 请重试!');
        }
    });
}


function del_row(id) {
    var attribute = id;
    var chkObj = document.getElementsByName(attribute);
    var tabObj = document.getElementById(id);
    for (var k = 0; k < chkObj.length; k++) {
        if (chkObj[k].checked) {
            tabObj.deleteRow(k + 1);
            k = -1;
        }
    }
}


function add_row(id) {
    var tabObj = document.getElementById(id);//获取添加数据的表格
    var rowsNum = tabObj.rows.length;  //获取当前行数
    var style = 'width:100%; border: none';
    var cell_check = "<input type='checkbox' name='" + id + "' style='width:55px' />";
    var cell_key = "<input type='text' name='test[][key]'  value='' style='" + style + "' />";
    var cell_value = "<input type='text' name='test[][value]'  value='' style='" + style + "' />";
    var cell_type = "<select name='test[][type]' class='form-control' style='height: 25px; font-size: 15px; " +
        "padding-top: 0px; padding-left: 0px; border: none'> " +
        "<option>string</option><option>int</option><option>float</option><option>boolean</option></select>";
    var cell_comparator = "<select name='test[][comparator]' class='form-control' style='height: 25px; font-size: 15px; " +
        "padding-top: 0px; padding-left: 0px; border: none'> " +
        "<option>equals</option> <option>contains</option> <option>startswith</option> <option>endswith</option> <option>regex_match</option> <option>type_match</option> <option>contained_by</option> <option>less_than</option> <option>less_than_or_equals</option> <option>greater_than</option> <option>greater_than_or_equals</option> <option>not_equals</option> <option>string_equals</option> <option>length_equals</option> <option>length_greater_than</option> <option>length_greater_than_or_equals</option> <option>length_less_than</option> <option>length_less_than_or_equals</option></select>";

    var myNewRow = tabObj.insertRow(rowsNum);
    var newTdObj0 = myNewRow.insertCell(0);
    var newTdObj1 = myNewRow.insertCell(1);
    var newTdObj2 = myNewRow.insertCell(2);


    newTdObj0.innerHTML = cell_check
    newTdObj1.innerHTML = cell_key;
    if (id === 'variables' || id === 'data') {
        var newTdObj3 = myNewRow.insertCell(3);
        newTdObj2.innerHTML = cell_type;
        newTdObj3.innerHTML = cell_value;
    } else if (id === 'validate') {
        var newTdObj3 = myNewRow.insertCell(3);
        newTdObj2.innerHTML = cell_comparator;
        newTdObj3.innerHTML = cell_type;
        var newTdObj4 = myNewRow.insertCell(4);
        newTdObj4.innerHTML = cell_value;
    } else {
        newTdObj2.innerHTML = cell_value;
    }
}

function add_params(id) {
    var tabObj = document.getElementById(id);//获取添加数据的表格
    var rowsNum = tabObj.rows.length;  //获取当前行数
    var style = 'width:100%; border: none';
    var check = "<input type='checkbox' name='" + id + "' style='width:55px' />";
    var placeholder = '单个:["value1", "value2],  多个:[["name1", "pwd1"],["name2","pwd2"]]';
    var key = "<textarea  name='test[][key]'  placeholder='单个:key, 多个:key1-key2'  style='" + style + "' />";
    var value = "<textarea  name='test[][value]'  placeholder='" + placeholder + "' style='" + style + "' />";
    var myNewRow = tabObj.insertRow(rowsNum);
    var newTdObj0 = myNewRow.insertCell(0);
    var newTdObj1 = myNewRow.insertCell(1);
    var newTdObj2 = myNewRow.insertCell(2);
    newTdObj0.innerHTML = check;
    newTdObj1.innerHTML = key;
    newTdObj2.innerHTML = value;
}
```

修改commons.js的auto_load函数
```
function auto_load(id, url, target, type) {
    var data = $(id).serializeJSON();
    if (id === '#pro_filter') {
        data = {
            "test": {
                "name": data,
                "type": type
            }
        }
    } else if (id === '#form_config') {
        data = {
            "config": {
                "name": data,
                "type": type
            }
        }
    }
    $.ajax({
        type: 'post',
        url: url,
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function (data) {
        
                show_module(data, target)
        }
        ,
        error: function () {
            myAlert('Sorry，服务器可能开小差啦, 请重试!');
        }
    });

}

```

修改视图函数 module_search_ajax

```
@csrf_exempt
def module_search_ajax(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        if 'test' in data.keys():
            project = data["test"]["name"]["project"]
        if 'config' in data.keys():
            project = data["config"]["name"]["project"]
        if  project != "All":
            p = Project.objects.get(project_name=project)
            modules = Module.objects.filter(belong_project=p)
            modules_list = ['%d^=%s' % (m.id, m.module_name) for m in modules ]
            modules_string = 'replaceFlag'.join(modules_list)
            return HttpResponse(modules_string)
        else:
            return HttpResponse('')
```
测试config_add.html 模板功能

修改视图函数config_add

```
@csrf_exempt
def config_add(request):
    if request.method == 'GET':
        context_dict = {
            'project': Project.objects.all().values('project_name').order_by('-create_time')
        }
        return render(request, 'config_add.html', context_dict)
    if request.is_ajax():
        testconfig = json.loads(request.body.decode('utf-8'))
        msg = config_logic(**testconfig)
        if msg == 'ok':
            return HttpResponse(reverse('config_list'))
        else:
            return HttpResponse(msg)
```
注意这里使用了函数config_logic，我们会在utils.py中定义，在创建utils.py前，我们先配置下日志

配置django日志
在settings.py 添加以下日志配置，并在static统一目录创建logs目录

```
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'}
        # 日志格式
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/all.log'),
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 5,
            'formatter': 'standard',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['default',],
            'level': 'INFO',
            'propagate': True
        }
    }
}
```

重启开发服务器，会在log目录下看到一个all.log的日志文件
[django日志配置](https://docs.djangoproject.com/zh-hans/2.1/topics/logging/)

在httpapitest目录下添加新文件utils.py


```
import logging
from .models import TestConfig, Module
from django.db import DataError

logger = logging.getLogger('django')


def type_change(type, value):
    """
    数据类型转换
    :param type: str: 类型
    :param value: object: 待转换的值
    :return: ok or error
    """
    try:
        if type == 'float':
            value = float(value)
        elif type == 'int':
            value = int(value)
    except ValueError:
        logger.error('{value}转换{type}失败'.format(value=value, type=type))
        return 'exception'
    if type == 'boolean':
        if value == 'False':
            value = False
        elif value == 'True':
            value = True
        else:
            return 'exception'
    return value


def key_value_list(keyword, **kwargs):
    """
    dict change to list
    :param keyword: str: 关键字标识
    :param kwargs: dict: 待转换的字典
    :return: ok or tips
    """
    if not isinstance(kwargs, dict) or not kwargs:
        return None
    else:
        lists = []
        test = kwargs.pop('test')
        for value in test:
            if keyword == 'setup_hooks':
                if value.get('key') != '':
                    lists.append(value.get('key'))
            elif keyword == 'teardown_hooks':
                if value.get('value') != '':
                    lists.append(value.get('value'))
            else:
                key = value.pop('key')
                val = value.pop('value')
                if 'type' in value.keys():
                    type = value.pop('type')
                else:
                    type = 'str'
                tips = '{keyword}: {val}格式错误,不是{type}类型'.format(keyword=keyword, val=val, type=type)
                if key != '':
                    if keyword == 'validate':
                        value['check'] = key
                        msg = type_change(type, val)
                        if msg == 'exception':
                            return tips
                        value['expect'] = msg
                    elif keyword == 'extract':
                        value[key] = val
                    elif keyword == 'variables':
                        msg = type_change(type, val)
                        if msg == 'exception':
                            return tips
                        value[key] = msg
                    elif keyword == 'parameters':
                        try:
                            if not isinstance(eval(val), list):
                                return '{keyword}: {val}格式错误'.format(keyword=keyword, val=val)
                            value[key] = eval(val)
                        except Exception:
                            logging.error('{val}->eval 异常'.format(val=val))
                            return '{keyword}: {val}格式错误'.format(keyword=keyword, val=val)

                lists.append(value)
        return lists


def key_value_dict(keyword, **kwargs):
    """
    字典二次处理
    :param keyword: str: 关键字标识
    :param kwargs: dict: 原字典值
    :return: ok or tips
    """
    if not isinstance(kwargs, dict) or not kwargs:
        return None
    else:
        dicts = {}
        test = kwargs.pop('test')
        for value in test:
            key = value.pop('key')
            val = value.pop('value')
            if 'type' in value.keys():
                type = value.pop('type')
            else:
                type = 'str'

            if key != '':
                if keyword == 'headers':
                    value[key] = val
                elif keyword == 'data':
                    msg = type_change(type, val)
                    if msg == 'exception':
                        return '{keyword}: {val}格式错误,不是{type}类型'.format(keyword=keyword, val=val, type=type)
                    value[key] = msg
                dicts.update(value)
        return dicts


def config_logic(type=True, **kwargs):
    """
    模块信息逻辑处理及数据处理
    :param type: boolean: True 默认新增 False：更新数据
    :param kwargs: dict: 模块信息
    :return: ok or tips
    """
    config = kwargs.pop('config')

    logging.debug('配置原始信息: {kwargs}'.format(kwargs=kwargs))
    if config.get('name').get('config_name') is '':
        return '配置名称不可为空'
    if config.get('name').get('author') is '':
        return '创建者不能为空'
    if config.get('name').get('project') == '请选择':
        return '请选择项目'
    if config.get('name').get('module') == '请选择':
        return '请选择或者添加模块'
    if config.get('name').get('project') == '':
        return '请先添加项目'
    if config.get('name').get('module') == '':
        return '请添加模块'
    name = config.pop('name')
    config.setdefault('name', name.pop('config_name'))
    config.setdefault('config_info', name)
    request_data = config.get('request').pop('request_data')
    data_type = config.get('request').pop('type')
    if request_data and data_type:
        if data_type == 'json':
            config.get('request').setdefault(data_type, request_data)
        else:
            data_dict = key_value_dict('data', **request_data)
            if not isinstance(data_dict, dict):
                return data_dict
            config.get('request').setdefault(data_type, data_dict)
    headers = config.get('request').pop('headers')
    if headers:
        config.get('request').setdefault('headers', key_value_dict('headers', **headers))
    variables = config.pop('variables')
    if variables:
        variables_list = key_value_list('variables', **variables)
        if not isinstance(variables_list, list):
            return variables_list
        config.setdefault('variables', variables_list)
    parameters = config.pop('parameters')
    if parameters:
        params_list = key_value_list('parameters', **parameters)
        if not isinstance(params_list, list):
            return params_list
        config.setdefault('parameters', params_list)
    hooks = config.pop('hooks')
    if hooks:
        setup_hooks_list = key_value_list('setup_hooks', **hooks)
        if not isinstance(setup_hooks_list, list):
            return setup_hooks_list
        config.setdefault('setup_hooks', setup_hooks_list)
        teardown_hooks_list = key_value_list('teardown_hooks', **hooks)
        if not isinstance(teardown_hooks_list, list):
            return teardown_hooks_list
        config.setdefault('teardown_hooks', teardown_hooks_list)
    kwargs.setdefault('config', config)
    return add_config_data(type, **kwargs)

def add_config_data(type, **kwargs):
    """
    配置信息落地
    :param type: boolean: true: 添加新配置， fasle: 更新配置
    :param kwargs: dict
    :return: ok or tips
    """
    config_opt = TestConfig.objects
    config_info = kwargs.get('config').get('config_info')
    name = kwargs.get('config').get('name')
    module = config_info.get('module')
    project = config_info.get('project')
    belong_module = Module.objects.get(id=int(module))

    try:
        if type:
            if config_opt.get_config_name(name, module, project) < 1:
                config_opt.insert_config(belong_module, **kwargs)
                logger.info('{name}配置添加成功: {kwargs}'.format(name=name, kwargs=kwargs))
            else:
                return '用例或配置已存在，请重新编辑'
        else:
            index = config_info.get('test_index')
            if name != TestConfig.objects.get(id=index).name \
                    and config_opt.get_config_name(name, module, project) > 0:
                return '用例或配置已在该模块中存在，请重新命名'
            config_opt.update_config(belong_module, **kwargs)
            logger.info('{name}配置更新成功: {kwargs}'.format(name=name, kwargs=kwargs))
    except DataError:
        logger.error('{name}配置信息过长：{kwargs}'.format(name=name, kwargs=kwargs))
        return '字段长度超长，请重新编辑'
    return 'ok'

```
创建views.py 同一目录创建managers.py文件
```
from django.db import models

class TestConfigManager(models.Manager):
    def insert_config(self, belong_module, **kwargs):
        config_info = kwargs.get('config').pop('config_info')
        self.create(name=kwargs.get('config').get('name'), belong_project=config_info.pop('project'),
                    belong_module=belong_module,
                    author=config_info.pop('author'), request=kwargs)

    def update_config(self, belong_module, **kwargs):
        config_info = kwargs.get('config').pop('config_info')
        obj = self.get(id=config_info.pop('test_index'))
        obj.belong_module = belong_module
        obj.belong_project = config_info.pop('project')
        obj.name = kwargs.get('config').get('name')
        obj.author = config_info.pop('author')
        obj.request = kwargs
        obj.save()

    def get_config_name(self, name, module_name, belong_project):
        return self.filter(belong_module__id=module_name).filter(name__exact=name).filter(
            belong_project__exact=belong_project).count()
```
managers.py 文件用来对提供model类的方法

更新modles.py 中的
```
class TestConfig(BaseTable):
    class Meta:
        verbose_name = '配置信息'
        db_table = 'TestConfigInfo'
    name = models.CharField('配置名称', max_length=50, null=False)
    belong_project = models.CharField('所属项目', max_length=50, null=False)
    belong_module = models.ForeignKey(Module, on_delete=models.CASCADE)
    author = models.CharField('编写人员', max_length=20, null=False)
    request = models.TextField('请求信息', null=False)
    objects = TestConfigManager()
```
注意添加了一行'objects = TestConfigManager()',objects  是一个管理类的实例，用来定义操作数据库的方法。

在 views.py中导入utils模块

`from .utils import config_logic`

测试添加一条config

### 配置列表

1. 定义视图函数config_list

```
@csrf_exempt
def config_list(request):
    if request.method == 'GET':
        info = {'belong_project': 'All', 'belong_module': "请选择"}
        projects = Project.objects.all().order_by("-update_time")
        rs = TestConfig.objects.all().order_by("-update_time")
        paginator = Paginator(rs,5)
        page = request.GET.get('page')
        objects = paginator.get_page(page)
        context_dict = {'config': objects, 'projects': projects, 'info': info}
        return render(request,"config_list.html",context_dict)
    if request.method == 'POST':
        projects = Project.objects.all().order_by("-update_time")
        project = request.POST.get("project")
        module = request.POST.get("module")
        name = request.POST.get("name")
        user = request.POST.get("user")
        
        if project == "All":
            if name:
                rs = TestConfig.objects.filter(name=name)
            elif user:
                rs = TestConfig.objects.filter(author=user).order_by("-update_time")
            else:
                rs = TestConfig.objects.all().order_by("-update_time")
        else:
            if module != "请选择":
                m = Module.objects.get(id=module)
                if name:
                    rs = TestConfig.objects.filter(belong_module=m, belong_project=project, name=name)
                elif user:
                    rs = TestConfig.objects.filter(belong_project=project,author=user).order_by("-update_time")
                else:
                    rs = TestConfig.objects.filter(belong_module=m, belong_project=project).order_by("-update_time")
                
            else:
                if name:
                    rs = TestConfig.objects.filter(belong_project=project, name=name)
                elif user:
                    rs = TestConfig.objects.filter(belong_project=project, author=user).order_by("-update_time")
                else:
                    rs = TestConfig.objects.filter(belong_project=project).order_by("-update_time")
                
    paginator = Paginator(rs,5)
    page = request.GET.get('page')
    objects = paginator.get_page(page)
    context_dict = {'config': objects, 'projects': projects, 'info': {'belong_project': project,'belong_module': module, 'user':user}}
    return render(request,"config_list.html",context_dict)
```
需要导入models.py 中TestConfig 类

2. 配置 url

```
path('config/list', views.config_list, name='config_list'),
path('config/copy', views.config_copy, name='config_copy'),
path('config/delete', views.config_delete, name='config_delete'),
path('config/edit/<int:id>', views.config_edit, name='config_edit'),
```

3. 添加config_copy,config_delete,config_edit 视图
```

def config_delete(request):
    pass


def config_copy(request):
    pass

def config_edit(request):
    pass

```

4. 添加config_list.html模板

[config_list.html](./Chapter-11-code/hat/templates/config_list.html)
注意模板中的搜索，复制，删除，编辑相关的功能

在commons.js 中添加copy_data_ajax
[commons.js](./Chapter-11-code/hat/static/assets/js/commons.js)


测试列表功能，输入http://127.0.0.1:8000/httpapitest/config/list


5. 删除功能
修改config_delete 视图函数
```
@csrf_exempt
def config_delete(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        config_id = data.get('id')
        config = TestConfig.objects.get(id=config_id)
        config.delete()
        return HttpResponse(reverse('config_list'))

```
点击删除按钮测试删除共能


6. 复制功能
修改config_copy 视图函数

```
@csrf_exempt
def config_copy(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        config_id = data['data']['index']
        name = data['data']['name']
        config = TestConfig.objects.get(id=config_id)
        belong_module = config.belong_module
        if TestConfig.objects.filter(name=name, belong_module=belong_module).count() > 0:
            return HttpResponse("配置名称重复")
        else:
            config.name = name
            config.id = None
            config.save()
            return HttpResponse(reverse('config_list'))
```

点击复制，测试复制功能

更新base.html 添加配置列表菜单的链接
7. 编辑功能

修改config_edit视图

 ```
@csrf_exempt
def config_edit(request,id):
    if request.method == 'GET':
        config = TestConfig.objects.get(id=id)
        config_request = eval(config.request)
        context_dict = {
            'project': Project.objects.all().values('project_name').order_by('-create_time'),
            'info': config,
            'request': config_request['config']
        }
        return render(request, 'config_edit.html', context_dict)

    if request.is_ajax():
        testconfig = json.loads(request.body.decode('utf-8'))
        msg = config_logic(type=False, **testconfig)
        if msg == 'ok':
            return HttpResponse(reverse('config_list'))
        else:
            return HttpResponse(msg)

 ```

添加config_edit.html 模板
[config_edit.html](./Chapter-11-code/hat/templates/config_edit.html)

这里使用到django模板的高级用法，[自定义模板的过滤器](https://docs.djangoproject.com/zh-hans/2.2/howto/custom-template-tags/)
在httapitest目录下创建一个templatetags包
创建文件 custom_tags.py

```
import json

from django import template

register = template.Library()



@register.filter(name='data_type')
def data_type(value):
    """
    返回数据类型 自建filter
    :param value:
    :return: the type of value
    """
    return str(type(value).__name__)




@register.filter(name='json_dumps')
def json_dumps(value):
    return json.dumps(value, indent=4, separators=(',', ': '), ensure_ascii=False)


@register.filter(name='is_del')
def id_del(value):
    if value.endswith('已删除'):
        return True
    else:
        return False
```

## locust性能测试
Locust 是一个易于使用的分布式用户负载测试工具。它用于对Web站点（或其他系统）进行负载测试，并计算出一个系统可以处理多少并发用户。Locust 完全基于事件，因此可以在一台机器上支持数千个并发用户。与许多其他基于事件的应用程序相比，它不使用回调，而是使用基于 gevent 的轻量级进程。每个 Locust 都在自己的进程中运行（正确的说法是greenlet）。这允许你用Python编写非常有表现力的场景，而不用使用回调使代码复杂化。


[locuts](https://www.locust.io/)

### 安装
`pip install locustio -i https://pypi.douban.com/simple/`

### 功能
1. 使用纯Python代码编写用户测试场景

不需要笨重的UI或臃肿的XML—只需要像通常那样编写代码即可。基于协程而不是回调，您的代码看起来和行为都像正常的Python代码。

2. 分布式和可伸缩-支持成千上万的用户

Locust 支持在多台机器上运行负载测试。由于基于事件，即使一个 Locust 节点也可以在一个进程中处理数千个用户。这背后的部分原因是，即使您模拟了那么多用户，也不是所有用户都在积极地攻击您的系统。通常，用户都在无所事事地考虑下一步该做什么。使得每秒请求数不等于在线用户数。

3. 基于Web的UI

Locust 有一个简洁的由 HTML+JS 生成的用户界面，可以实时显示相关的测试细节。由于UI是基于Web的，所以它是跨平台的，并且易于扩展。

4. 可以测试任何系统

尽管 Locust 是面向Web的，但它几乎可以用于测试任何系统。无论你想测试什么，只要编写一个客户端，然后让它像蝗虫一样成群结队！这是超级简单的！


### 快速开始

新建locustfile.py 文件

```
from locust import HttpLocust, TaskSet

def login(l):
    l.client.post("/login", {"username":"ellen_key", "password":"education"})

def logout(l):
    l.client.post("/logout", {"username":"ellen_key", "password":"education"})

def index(l):
    l.client.get("/")

def profile(l):
    l.client.get("/profile")

class UserBehavior(TaskSet):
    tasks = {index: 2, profile: 1}

    def on_start(self):
        login(self)

    def on_stop(self):
        logout(self)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
```
在这里，我们定义了许多 Locust 任务，这些任务是普通的Python可调用函数，它们只接受一个参数(一个 Locust 类实例)。这些 Locust 任务集中在 TaskSet 类的子类的 tasks 属性中。然后我们定义了一个 HttpLocust 类的子类，它代表一个用户。在这个类中，我们定义了一个模拟用户在执行任务之间应该等待多长时间，以及哪个TaskSet类定义了用户的“行为”。其中，TaskSet 类可以嵌套



启动locust
locustfile.py 位于当前目录

`locust --host=http://127.0.0.1  --web-host="127.0.0.1"`

+ --host 目标主机
+ --web-host locust web端口

如果 Locust 文件位于一个子目录或者使用了其他的名称，那么可以使用 -f 参数来指定

`locust -f ./locustfile.py --host=http://127.0.0.1  --web-host="127.0.0.1" `

要运行分布在多个进程中的 Locust，我们可以通过 --master 参数来指定并启动一个主进程：

`locust -f ./locustfile.py --master --host=http://127.0.0.1  --web-host="127.0.0.1"`

然后，我们就可以启动任意数量的从属进程了：
`locust -f ./locustfile.py --slave --host=http://127.0.0.1`

如果我们想在多台机器上运行 Locust，我们还必须在启动从机时指定主机，将下面的masterip替换为master机器的ip
`locust -f ./locustfile.py --slave  --master-host=masterip --host=http://127.0.0.1`


### 编写一个locustfile
locustfile 是一个普通的Python文件。惟一的要求在这个文件中必须至少定义一个继承自 Locust 类（我们称它为locust类）的类。


1. task_set 属性
task_set 属性应该指向一个定义了用户行为的 TaskSet 类，下面将对其进行更详细的描述。

2. min_wait 和 max_wait 属性
除了 task_set 属性外，通常还需要声明 min_wait 和 max_wait 属性。这些分别是模拟用户在执行每个任务之间等待的最小时间和最大时间，单位为毫秒。min_wait 和 max_wait 默认值均为1000，因此，如果没有声明 min_wait 和 max_wait，则 locust 将在每个任务之间始终等待1秒。

```
class UserBehavior(TaskSet):
    tasks = {index: 2, profile: 1}

    def on_start(self):
        login(self)

    def on_stop(self):
        logout(self)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
```

上面的locustfile.py 还可以写为
```
from locust import HttpLocust, TaskSet, task

class UserBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.login()

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """
        self.logout()

    def login(self):
        self.client.post("/login", {"username":"ellen_key", "password":"education"})

    def logout(self):
        self.client.post("/logout", {"username":"ellen_key", "password":"education"})

    @task(2)
    def index(self):
        self.client.get("/")

    @task(1)
    def profile(self):
        self.client.get("/profile")

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
```
使用@task 装饰器来声明任务

### TaskSet 类

TaskSet 就像它的名字一样，是一组任务，这些任务都是普通的Python可调用对象。如果我们对一个拍卖的网站进行负载测试，那么可以执行诸如 “加载其实页面”、“搜索某些产品” 和 “出价” 等操作。

当启动负载测试时，派生的 Locust 类的每个实例将开始执行它们的 TaskSet。然后，每个 TaskSet 将选择一个任务并执行。之后等待若干毫秒，这个等待时间是均匀分布在 Locust 类的 min_wait 和 max_wait 属性值之间的一个随机数（如果 TaskSet 设置了自己的 min_wait 和 max_wait 属性，则将使用它自己设置的值）。然后它将再次选择要执行的任务，再次等待。以此类推。


### 定义任务
定义 TaakSet 的 tasks 的典型方式是使用 @task 装饰器

```
    @task(2)
    def index(self):
        self.client.get("/")

    @task(1)
    def profile(self):
        self.client.get("/profile")
```

也可以通过设置 tasks 属性来定义TaskSet 的任务

```
def index(l):
    l.client.get("/")

def profile(l):
    l.client.get("/profile")

class UserBehavior(TaskSet):
    tasks = {index: 2, profile: 1}
```

### on_start 和 on_stop 方法
TaskSet 类可以声明 on_start 方法或 on_stop 方法。on_start 方法在虚拟用户开始执行 TaskSet 类时调用，而on_stop （locust.core.TaskSet.on_stop()）方法在 TaskSet 停止时调用

### 发起HTTP请求

为了对系统进行真是的负载测试，我们需要发出HTTP请求,使用HttpLocust 类的

```
class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
```

### 发起xml-rpc 请求
locustxmlfile.py

```
import time
from xmlrpc import client

from locust import Locust, TaskSet, events, task


class XmlRpcClient(client.ServerProxy):
    """
    Simple, sample XML RPC client implementation that wraps xmlrpclib.ServerProxy and 
    fires locust events on request_success and request_failure, so that all requests 
    gets tracked in locust's statistics.
    """
    def __getattr__(self, name):
        func = client.ServerProxy.__getattr__(self, name)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                total_time = int((time.time() - start_time) * 1000)
                events.request_failure.fire(request_type="xmlrpc", name=name, response_time=total_time, exception=e)
            else:
                total_time = int((time.time() - start_time) * 1000)
                events.request_success.fire(request_type="xmlrpc", name=name, response_time=total_time, response_length=0)
                # In this example, I've hardcoded response_length=0. If we would want the response length to be 
                # reported correctly in the statistics, we would probably need to hook in at a lower level
        
        return wrapper


class XmlRpcLocust(Locust):
    """
    This is the abstract Locust class which should be subclassed. It provides an XML-RPC client
    that can be used to make XML-RPC requests that will be tracked in Locust's statistics.
    """
    def __init__(self, *args, **kwargs):
        super(XmlRpcLocust, self).__init__(*args, **kwargs)
        self.client = XmlRpcClient(self.host)


class ApiUser(XmlRpcLocust):
    
    host = "http://127.0.0.1:8877"
    min_wait = 100
    max_wait = 1000
    
    class task_set(TaskSet):
        @task(10)
        def get_time(self):
            self.client.get_time()
        
        @task(5)
        def get_random_number(self):
            self.client.get_random_number(0, 100)


```

服务端代码

```
import random
import time
from xmlrpc.server import SimpleXMLRPCServer


def get_time():
    time.sleep(random.random())
    return time.time()

def get_random_number(low, high):
    time.sleep(random.random())
    return random.randint(low, high)

server = SimpleXMLRPCServer(("localhost", 8877))
print("Listening on port 8877...")
server.register_function(get_time, "get_time")
server.register_function(get_random_number, "get_random_number")
server.serve_forever()
```

启动被测服务段

python server.py


启动locust

 locust -f ./locustxmlfile.py   --web-host="127.0.0.1" 
