# 第十一天

## debugtalk.py管理
每一个项目里都要有一个debugtalk.py文件用来定义一些函数，用来被配置文件引用

### 在models.py里添加 DebugTalk类

```
class DebugTalk(BaseTable):
    class Meta:
        verbose_name = '驱动py文件'
        db_table = 'DebugTalk'

    belong_project = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
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
def config_add(requests):
    if request.method == 'GET':
        context_dict = {
            'project': Project.objects.all().values('project_name').order_by('-create_time')
        }
        return render(requests, 'config_add.html', context_dict)
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
        url = '/httpapitest/config/edit';
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
在settings.py 添加以下日志配置，并在static统计目录创建logs目录

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
                        value['expected'] = msg
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
            if name != config_opt.get_case_by_id(index, type=False) \
                    and config_opt.get_case_name(name, module, project) > 0:
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
path('config/copy', views.config_list, name='config_copy'),
path('config/delete', views.config_list, name='config_delete'),
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
更新base.html 添加配置管理菜单的链接
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





