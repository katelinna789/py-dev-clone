# 第十二天

## 用例管理


1. 添加model 类TestCase
```
class TestCase(BaseTable):
    class Meta:
        verbose_name = '用例信息'
        db_table = 'TestCaseInfo'
    name = models.CharField('用例名称', max_length=50, null=False)
    belong_project = models.CharField('所属项目', max_length=50, null=False)
    belong_module = models.ForeignKey(Module, on_delete=models.CASCADE)
    include = models.CharField('前置config/test', max_length=1024, null=True)
    author = models.CharField('创建者', max_length=20, null=False)
    request = models.TextField('请求信息', null=False)
    objects = TestCaseManager()

执行数据库迁移命令

2. 添加用例

添加视图函数 

```
@csrf_exempt
def case_add(request):
    if request.method == 'GET':
        context_dict = {
            'project': Project.objects.all().values('project_name').order_by('-create_time')
        }
        return render(request, 'case_add.html', context_dict)
    if request.is_ajax():
        testcase = json.loads(request.body.decode('utf-8'))
        msg = case_logic(**testcase)
        if msg == 'ok':
            return HttpResponse(reverse('case_list'))
        else:
            return HttpResponse(msg)


@csrf_exempt
def case_search_ajax(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        if 'case' in data.keys():
            project = data["case"]["name"]["project"]
            module = data["case"]["name"]["module"]
        if   project != "请选择" and module != "请选择":
            m = Module.objects.get(id=module)
            cases = TestCase.objects.filter(belong_project=project, belong_module=m)
            case_list = ['%d^=%s' % (c.id, c.name) for c in cases ]
            case_string = 'replaceFlag'.join(case_list)
            return HttpResponse(case_string)
        else:
            return HttpResponse('')

@csrf_exempt
def config_search_ajax(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        if 'case' in data.keys():
            project = data["case"]["name"]["project"]
            module = data["case"]["name"]["module"]
        if   project != "请选择" and module != "请选择":
            m = Module.objects.get(id=module)
            configs = TestConfig.objects.filter(belong_project=project, belong_module=m)
            config_list = ['%d^=%s' % (c.id, c.name) for c in configs ]
            config_string = 'replaceFlag'.join(config_list)
            return HttpResponse(config_string)
        else:
            return HttpResponse('')

def case_list(request):
    pass


def case_edit(request):
    pass

def case_delete(request):
    pass

def cae_copy(request):
    pass
```

在utils.py 中添加case_logic， add_case_data update_include 函数

[utils.py](./Chapter-12-code/hat/httpapitest/utils.py)


在managers.py 添加 TestCaseManager 类

[managers.py](./Chapter-12-code/hat/httpapitest/managers.py)

修改models.py 给TestCase类添加属性`objects = TestCaseManager()`

添加模板文件 case_add.html

[case_add.html](./Chapter-12-code/hat/templates/case_add.html)

templatetags/custom_tags.py添加自定义过滤器 convert_eval id_del
[custom_tags.py](./Chapter-12-code/hat/httpapitest/templatetags/custom_tags.py)

在commons.js中添加函数case_ajax

[commons.js](./Chapter-12-code/hat/static/assets/js/commons.js)

在urls.py 中添加
```
    path('case/add', views.case_add, name='case_add'),
    path('case/search/ajax', views.case_search_ajax, name='case_search_ajax'),
    path('config/search/ajax', views.config_search_ajax, name='config_search_ajax'),
    path('case/edit/<int:id>', views.case_edit, name='case_edit'),
    path('case/list', views.case_list, name='case_list'),
    path('case/delete', views.case_delete, name='case_delete'),
    path('case/copy', views.case_copy, name='case_copy'),
```


3. 用例列表 

更新case_list 视图

```
@csrf_exempt
def case_list(request):
    if request.method == 'GET':
        info = {'belong_project': 'All', 'belong_module': "请选择"}
        projects = Project.objects.all().order_by("-update_time")
        rs = TestCase.objects.all().order_by("-update_time")
        paginator = Paginator(rs,5)
        page = request.GET.get('page')
        objects = paginator.get_page(page)
        context_dict = {'case': objects, 'projects': projects, 'info': info}
        return render(request,"case_list.html",context_dict)
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
                module = m
                logger.info(module)
                
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


添加模板case_list.html
[case_list.html](./Chapter-12-code/hat/templates/case_list.html)

4. 编辑功能
更新case_edit 视图
```
@csrf_exempt
def case_edit(request, id):
    if request.method == 'GET':
        case = TestCase.objects.get(id=id)
        case_request = eval(case.request)
        case_include = eval(case.include)
        context_dict = {
            'project': Project.objects.all().values('project_name').order_by('-create_time'),
            'info': case,
            'request': case_request['test'],
            'include': case_include
        }
        return render(request, 'case_edit.html', context_dict)

    if request.is_ajax():
        case_list = json.loads(request.body.decode('utf-8'))
        msg = case_logic(type=False, **case_list)
        if msg == 'ok':
            return HttpResponse(reverse('case_list'))
        else:
            return HttpResponse(msg)
```
5. 修改功能
添加case_edit.html模板

[case_edit.html](./Chapter-12-code/hat/templates/case_edit.html)
测试编辑功能

6. 删除功能
修改case_delete视图
```
@csrf_exempt
def case_delete(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        case_id = data.get('id')
        case = TestCase.objects.get(id=case_id)
        case.delete()
        return HttpResponse(reverse('case_list'))
```

测试删除功能

7. 拷贝功能
```
@csrf_exempt
def case_copy(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        config_id = data['data']['index']
        name = data['data']['name']
        case = TestCase.objects.get(id=config_id)
        belong_module = case.belong_module
        if TestCase.objects.filter(name=name, belong_module=belong_module).count() > 0:
            return HttpResponse("用例名称重复")
        else:
            case.name = name
            case.id = None
            case.save()
            return HttpResponse(reverse('case_list'))
```

测试拷贝功能

## 用例运行
添加视图函数test_run
```
@csrf_exempt
def test_run(request):
    """
    运行用例
    :param request:
    :return:
    """

    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        id = kwargs.pop('id')
        base_url = kwargs.pop('env_name')
        type = kwargs.pop('type')
        run_test_by_type(id, base_url, testcase_dir_path, type)
        report_name = kwargs.get('report_name', None)
        main_hrun.delay(testcase_dir_path, report_name)
        return HttpResponse('用例执行中，请稍后查看报告即可,默认时间戳命名报告')
    else:
        id = request.POST.get('id')
        base_url = request.POST.get('env_name')
        type = request.POST.get('type', 'test')

        run_test_by_type(id, base_url, testcase_dir_path, type)
        runner.run(testcase_dir_path)
        shutil.rmtree(testcase_dir_path)
        summary = timestamp_to_datetime(runner._summary, type=False)
        print(summary)

        return render(request,'report_template.html', summary)

```

views.py 导入函数
```
from .utils import  get_time_stamp,timestamp_to_datetime
from httprunner.api import HttpRunner
from .runner import run_test_by_type,run_by_single
import logging
import os,shutil
```

在utils.py 文件中添加dump_yaml_file，dump_python_file，get_time_stamp，timestamp_to_datetime
```
def dump_yaml_file(yaml_file, data):
    """ load yaml file and check file content format
    """
    with io.open(yaml_file, 'w', encoding='utf-8') as stream:
        yaml.dump(data, stream, indent=4, default_flow_style=False, encoding='utf-8')


def dump_python_file(python_file, data):
    with io.open(python_file, 'w', encoding='utf-8') as stream:
        stream.write(data)

def get_time_stamp():
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%Y-%m-%d %H-%M-%S", local_time)
    data_secs = (ct - int(ct)) * 1000
    time_stamp = "%s-%03d" % (data_head, data_secs)
    return time_stamp


def timestamp_to_datetime(summary, type=True):
    if not type:
        time_stamp = int(summary["time"]["start_at"])
        summary['time']['start_datetime'] = datetime.datetime. \
            fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')

    for detail in summary['details']:
        try:
            time_stamp = int(detail['time']['start_at'])
            detail['time']['start_at'] = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            pass

        for record in detail['records']:
            try:
                time_stamp = int(record['meta_data']['request']['start_timestamp'])
                record['meta_data']['request']['start_timestamp'] = \
                    datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass
    return summary
```

在httpapitest添加runer.py文件
```
```

添加模板文件

[report_tempalte.html](./Chapter-12-code/hat/templates/report_template.html)

测试用例运行

## 批量运行

```
@csrf_exempt
def test_batch_run(request):
    """
    批量运行用例
    :param request:
    :return:
    """

    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        test_list = kwargs.pop('id')
        base_url = kwargs.pop('env_name')
        type = kwargs.pop('type')
        report_name = kwargs.get('report_name', None)
        run_by_batch(test_list, base_url, testcase_dir_path, type=type)
        main_hrun.delay(testcase_dir_path, report_name)
        return HttpResponse('用例执行中，请稍后查看报告即可,默认时间戳命名报告')
    else:
        type = request.POST.get('type', None)
        base_url = request.POST.get('env_name')
        test_list = request.body.decode('utf-8').split('&')
        if type:
            run_by_batch(test_list, base_url, testcase_dir_path, type=type, mode=True)
        else:
            run_by_batch(test_list, base_url, testcase_dir_path)

        runner.run(testcase_dir_path)

        shutil.rmtree(testcase_dir_path)
        summary = timestamp_to_datetime(runner._summary, type=False)
        print(summary)
        return render(request,'report_template.html', summary)
```
