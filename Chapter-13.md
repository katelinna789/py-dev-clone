# 第十三天

## 测试报告


1. 在modules.py 中添加 模型TestReports
```
class TestReports(BaseTable):
    class Meta:
        verbose_name = "测试报告"
        db_table = 'TestReports'

    report_name = models.CharField(max_length=40, null=False)
    start_at = models.CharField(max_length=40, null=True)
    status = models.BooleanField()
    testsRun = models.IntegerField()
    successes = models.IntegerField()
    reports = models.TextField()
```

2. 添加视图函数
```
def report_list(request):
    if request.method == "GET":
        rs = TestReports.objects.all().order_by("-update_time")
        paginator = Paginator(rs,5)
        page = request.GET.get('page')
        objects = paginator.get_page(page)
        context_dict = {'report': objects }
        return render(request,"report_list.html",context_dict)

@csrf_exempt
def report_delete(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        report_id = data.get('id')
        report = TestReports.objects.get(id=report_id)
        report.delete()
        return HttpResponse(reverse('report_list'))

def report_view(request, id):
    """
    查看报告
    :param request:
    :param id: str or int：报告名称索引
    :return:
    """
    reports = TestReports.objects.get(id=id).reports
    return render(request, 'report_view.html', {"reports": mark_safe(reports)})
```
views.py 新增导入
```
from httpapitest.models import TestReports
from django.utils.safestring import mark_safe
```

3. 添加report_list.html模板
[report_list.html](./Chapter-12-code/hat/templates/report_list.html)

4. 添加url
```
path('report/list', views.report_list, name='report_list'),
```

## 添加异步执行功能
1. 添加异步运行所需要的task.py文件

[tasks.py](./Chapter-12-code/hat/httpapitest/tasks.py)



2. 修改settings.py 添加celery相关配置
[settings.py](./Chapter-12-code/hat/hat/settings.py)
```
CELERY_BROKER_URL = 'redis://192.168.1.111:6379/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler' # 定时任务

CELERY_TASK_RESULT_EXPIRES = 7200  # celery任务执行结果的超时时间，
CELERYD_CONCURRENCY = 1 if DEBUG else 10 # celery worker的并发数 也是命令行-c指定的数目 根据服务器配置实际更改 一般25即可
CELERYD_MAX_TASKS_PER_CHILD = 100  # 每个worker执行了多少任务就会死掉
```

4. 添加异步报告函数

在utils.py 中添加
```
def add_test_reports(summary, report_name=None):
    """
    定时任务或者异步执行报告信息落地
    :param start_at: time: 开始时间
    :param report_name: str: 报告名称，为空默认时间戳命名
    :param kwargs: dict: 报告结果值
    :return:
    """
    
    separator = '\\' if platform.system() == 'Windows' else '/'

    time_stamp = int(summary["time"]["start_at"])
    summary['time']['start_at'] = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
    report_name = report_name if report_name else summary['time']['start_datetime']
    summary['html_report_name'] = report_name

    report_path = os.path.join(os.getcwd(), "reports{}{}.html".format(separator,time_stamp))
    #runner.gen_html_report(html_report_template=os.path.join(os.getcwd(), "templates{}extent_report_template.html".format(separator)))

    with open(report_path, encoding='utf-8') as stream:
        reports = stream.read()

    test_reports = {
        'report_name': report_name,
        'status': summary.get('success'),
        'successes': summary.get('stat').get('testcases').get('success'),
        'testsRun': summary.get('stat').get('testcases').get('total'),
        'start_at': summary['time']['start_at'],
        'reports': reports
    }

    TestReports.objects.create(**test_reports)
    return report_path
```

5. 在hat目录中新增celery.py 文件

[celery.py](./Chapter-13-code/hat/hat/celery.py)

该文件用来启动celery 进程

```
import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hat.settings')

app = Celery('hat')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
```

6.启动celery

`celery -A  hat  worker --loglevel=info  -P eventlet`

打开模块列表,执行模块选择异步

## 定时任务管理

1. 使用django-celery-beat 模块

安装
`pip3 install  django-celery-beat -i https://pypi.douban.com/simple/`

在settings.py INSTALLED_APPS 中配置 django_celery_beat

```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'httpapitest',
    'django_celery_beat',
]
```

需要执行下数据迁移，django_celery_beat 包含数据表

2. 添加视图

```
@csrf_exempt
def task_add(request):
    """
    添加任务
    :param request:
    :return:
    """

    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        msg = task_logic(**kwargs)
        if msg == 'ok':
            return HttpResponse(reverse('task_list'))
        else:
            return HttpResponse(msg)
    elif request.method == 'GET':
        info = {
            'project': Project.objects.all().order_by('-create_time')
        }
        return render(request, 'task_add.html', info)

@login_check
def task_list(request):
    if request.method == 'GET':
        name = request.GET.get('name','')
        info = {'name': name}
        if name:
            rs = PeriodicTask.objects.filter(name=name).order_by('-date_changed')
        else:
            rs = PeriodicTask.objects.all().order_by('-date_changed')
        paginator = Paginator(rs,5)
        page = request.GET.get('page')
        objects = paginator.get_page(page)
        context_dict = {'task': objects, 'info': info}
        return render(request,"task_list.html",context_dict)


@csrf_exempt
def task_delete(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        task_id = data.get('id')
        task = PeriodicTask.objects.get(id=task_id)
        task.delete()
        return HttpResponse(reverse('task_list'))

@csrf_exempt
def task_set(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        task_id = data.get('id')
        mode = data.get('mode')
        task = PeriodicTask.objects.get(id=task_id)
        task.enabled = mode
        task.save()
        return HttpResponse(reverse('task_list'))

@csrf_exempt
def suite_search_ajax(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        if 'crontab' in data.keys():
            project = data["crontab"]["name"]["project"]
            
        if   project != "请选择":
            p = Project.objects.get(project_name=project)
            suites = TestSuite.objects.filter(belong_project=p)
            suite_list = ['%d^=%s' % (c.id, c.suite_name) for c in suites ]
            suite_string = 'replaceFlag'.join(suite_list)
            return HttpResponse(suite_string)
        else:
            return HttpResponse('')
```

veiws.py 新增导入

```
from django_celery_beat.models import PeriodicTask
from .utils import task_logic
```

2. utils.py 添加task_logic函数
```
def task_logic(**kwargs):
    """
    定时任务逻辑处理
    :param kwargs: dict: 定时任务数据
    :return:
    """
    
    if kwargs.get('name') is '':
        return '任务名称不可为空'
    elif kwargs.get('project') is '':
        return '请选择一个项目'
    elif kwargs.get('crontab_time') is '':
        return '定时配置不可为空'
    elif not kwargs.get('module'):
        kwargs.pop('module')

    try:
        crontab_time = kwargs.pop('crontab_time').split(' ')
        if len(crontab_time) > 5:
            return '定时配置参数格式不正确'
        crontab = {
            'day_of_week': crontab_time[-1],
            'month_of_year': crontab_time[3],  # 月份
            'day_of_month': crontab_time[2],  # 日期
            'hour': crontab_time[1],  # 小时
            'minute': crontab_time[0],  # 分钟
        }
    except Exception:
        return '定时配置参数格式不正确'
    if PeriodicTask.objects.filter(name__exact=kwargs.get('name')).count() > 0:
        return '任务名称重复，请重新命名'
    desc = " ".join(str(i) for i in crontab_time)
    name = kwargs.get('name')
    mode = kwargs.pop('mode')

    if 'module' in kwargs.keys():
        kwargs.pop('project')

        if mode == '1':
            return create_task(name, 'httpapitest.tasks.module_hrun', kwargs, crontab, desc)
        else:
            kwargs['suite'] = kwargs.pop('module')
            return create_task(name, 'httpapitest.tasks.suite_hrun', kwargs, crontab, desc)
    else:
        return create_task(name, 'httpapitest.tasks.project_hrun', kwargs, crontab, desc)
```
在utils.py 导入
`from .tasks_opt import create_task`

3. 在httpapitest目录下添加tasks_opt.py
```
import json

from django_celery_beat import models as celery_models


def create_task(name, task, task_args, crontab_time, desc):
    '''
    新增定时任务
    :param name: 定时任务名称
    :param task: 对应tasks里已有的task
    :param task_args: list 参数
    :param crontab_time: 时间配置
    :param desc: 定时任务描述
    :return: ok
    '''
    # task任务， created是否定时创建
    task, created = celery_models.PeriodicTask.objects.get_or_create(name=name, task=task)
    # 获取 crontab
    crontab = celery_models.CrontabSchedule.objects.filter(**crontab_time).first()
    if crontab is None:
        # 如果没有就创建，有的话就继续复用之前的crontab
        crontab = celery_models.CrontabSchedule.objects.create(**crontab_time)
    task.crontab = crontab  # 设置crontab
    task.enabled = True  # 开启task
    task.kwargs = json.dumps(task_args, ensure_ascii=False)  # 传入task参数
    task.description = desc
    task.save()
    return 'ok'


def change_task_status(name, mode):
    '''
    任务状态切换：open or close
    :param name: 任务名称
    :param mode: 模式
    :return: ok or error
    '''
    try:
        task = celery_models.PeriodicTask.objects.get(name=name)
        task.enabled = mode
        task.save()
        return 'ok'
    except celery_models.PeriodicTask.DoesNotExist:
        return 'error'


def delete_task(name):
    '''
    根据任务名称删除任务
    :param name: task name
    :return: ok or error
    '''
    try:
        task = celery_models.PeriodicTask.objects.get(name=name)
        task.enabled = False  # 设置关闭
        task.delete()
        return 'ok'
    except celery_models.PeriodicTask.DoesNotExist:
        return 'error'

```

2. 更改module_search_ajax 视图
```
@csrf_exempt
@login_check
def module_search_ajax(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        if 'test' in data.keys():
            project = data["test"]["name"]["project"]
        if 'config' in data.keys():
            project = data["config"]["name"]["project"]
        if 'case' in data.keys():
            project = data["case"]["name"]["project"]
        if 'upload' in data.keys():
            project = data["upload"]["name"]["project"]
        if 'crontab' in data.keys():
            project = data["crontab"]["name"]["project"]
        if  project != "All" and project != "请选择":
            p = Project.objects.get(project_name=project)
            modules = Module.objects.filter(belong_project=p)
            modules_list = ['%d^=%s' % (m.id, m.module_name) for m in modules ]
            modules_string = 'replaceFlag'.join(modules_list)
            return HttpResponse(modules_string)
        else:
            return HttpResponse('')
```
添加内容为
```
        if 'crontab' in data.keys():
            project = data["crontab"]["name"]["project"]
```

3. 修改commons.js auto_load函数
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
    } else if (id === '#belong_message' || id === '#form_message') {
        data = {
            "case": {
                "name": data,
                "type": type
            }
        }
    } else if (id === '#upload_project_info'){
        data = {
            "upload": {
                "name": data,
                "type": type
            }
        }
    } else if (id ==='#project') {
        data = {
            "crontab": {
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
增加内容为
```
    else if (id === '#upload_project_info'){
        data = {
            "upload": {
                "name": data,
                "type": type
            }
        }
    } else if (id ==='#project') {
        data = {
            "crontab": {
                "name": data,
                "type": type
            }
        }
    }

```
注： uplaod 暂时不用

4. 添加模板

[task_add.html](./Chapter-13-code/hat/templates/task_add.html)
[task_list.html](./Chapter-13-code/hat/templates/task_list.html)

5. 添加url
```
    path('task/add', views.task_add, name='task_add'),
    path('task/list',views.task_list, name='task_list'),
    path('task/delete', views.task_delete, name="task_delete"),
    path('task/set', views.task_set, name="task_set"),
```
6. 启动celery定时任务
`celery -A  hat  beat  --loglevel=info`
7. 测试添加任务


## 用例个数统计功能

1. 在templatetags 目录下的caustom_tags.py中添加
```
@register.filter(name='project_sum')
def project_sum(pro_name):
   
    module_count = str(Module.objects.filter(belong_project__project_name__exact=pro_name).count())
    suite_count = str(TestSuite.objects.filter(belong_project__project_name__exact=pro_name).count())
    test_count = str(TestCase.objects.filter(belong_project__exact=pro_name).count())
    config_count = str(TestConfig.objects.filter(belong_project__exact=pro_name).count())
    sum = module_count + '/ ' + suite_count + '/' + test_count + '/ ' + config_count
    return sum


@register.filter(name='module_sum')
def module_sum(id):
    module = Module.objects.get(id=id)
    test_count = str(TestCase.objects.filter(belong_module=module).count())
    config_count = str(TestConfig.objects.filter(belong_module=module).count())
    sum = test_count + '/ ' + config_count
    return sum
```

2. 将project_list.html 中的0/0/0/0 修改为 `{{ foo.project_name | project_sum }}`
3. 将module_list.html中的0/0 修改为`{{ foo.id | module_sum }}`

## 导入httprunner配置

1. 添加视图

```
@csrf_exempt
def upload_file(request):
    
    if request.method == 'POST':
        try:
            project_name = request.POST.get('project')
            module_name = request.POST.get('module')
        except KeyError as e:
            return JsonResponse({"status": e})

        if project_name == '请选择' or module_name == '请选择':
            return JsonResponse({"status": '项目或模块不能为空'})

        upload_path = os.path.join(os.getcwd(),"upload")

        if os.path.exists(upload_path):
            shutil.rmtree(upload_path)

        os.mkdir(upload_path)

        upload_obj = request.FILES.getlist('upload')
        file_list = []
        for i in range(len(upload_obj)):
            temp_path = os.path.join(upload_path,upload_obj[i].name)
            file_list.append(temp_path)
            try:
                with open(temp_path, 'wb') as data:
                    for line in upload_obj[i].chunks():
                        data.write(line)
            except IOError as e:
                return JsonResponse({"status": e})

        upload_file_logic(file_list, project_name, module_name, 'test')

        return JsonResponse({'status': '/httpapitest/case/list'})
```

在views.py 中导入
```
from .utils import upload_file_logic
from django.http import JsonResponse
```

2. 在utils.py 添加upload_file_logic函数
```
def upload_file_logic(files, project, module, account):
    """
    解析yaml或者json用例
    :param files:
    :param project:
    :param module:
    :param account:
    :return:
    """

    for file in files:
        file_suffix = os.path.splitext(file)[1].lower()
        if file_suffix == '.json':
            with io.open(file, encoding='utf-8') as data_file:
                try:
                    content = json.load(data_file)
                except JSONDecodeError:
                    err_msg = u"JSONDecodeError: JSON file format error: {}".format(file)
                    logging.error(err_msg)

        elif file_suffix in ['.yaml', '.yml']:
            with io.open(file, 'r', encoding='utf-8') as stream:
                content = yaml.load(stream)

        for test_case in content:
            test_dict = {
                'project': project,
                'module': module,
                'author': account,
                'include': []
            }
            if 'config' in test_case.keys():
                test_case.get('config')['config_info'] = test_dict
                variables = test_case.get('config')['variables']
                variables_list = [ {item:variables[item]} for item in variables]
                test_case.get('config')['variables'] = variables_list

                add_config_data(type=True, **test_case)

            if 'test' in test_case.keys():  # 忽略config
                test_case.get('test')['case_info'] = test_dict
                variables = test_case.get('test')['variables']
                variables_list = [ {item:variables[item]} for item in variables]
                test_case.get('test')['variables'] = variables_list

                if 'validate' in test_case.get('test').keys():  # 适配validate两种格式
                    validate = test_case.get('test').pop('validate')
                    new_validate = []
                    for check in validate:
                        if 'comparator' not in check.keys():
                            for key, value in check.items():
                                tmp_check = {"check": value[0], "comparator": key, "expected": value[1]}
                                new_validate.append(tmp_check)

                    test_case.get('test')['validate'] = new_validate

                add_case_data(type=True, **test_case)
```

3. 在project_list.html `{% block content %}` 语句下增加下面代码

```
<form enctype="multipart/form-data" id="upload_project_info">
    <div class="modal fade" id="bulk_uploadcase" tabindex="-1" role="dialog" aria-labelledby="myModalLabel"
         aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                    <h4 class="modal-title" id="myModalLabel">HAT</h4>
                </div>
                <div class="modal-body">
                    <input name="upload" id="uploadfile" type="file" class="file" multiple/>
                    <div id="kartik-file-errors"></div>
                </div>
                <div class="form-group">
                    <div class="input-group col-md-8" style="margin-left: 15px">
                        <div class="input-group-addon" style="color: #0a628f">所属项目</div>
                        <select id='project' name="project" class="form-control"
                                onchange="auto_load('#upload_project_info', '{% url 'module_search_ajax' %}', '#upload_belong_module_id', 'module')">
                            <option value="请选择">请选择</option>
                            {% for foo in project %}
                                <option value="{{ foo.project_name }}">{{ foo.project_name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <div class="input-group col-md-8" style="margin-left: 15px">
                        <div class="input-group-addon" style="color: #0a628f">所属模块</div>
                        <select id="upload_belong_module_id" name="module" class="form-control">
                        </select>
                    </div>
                </div>
            </div><!-- /.modal-content -->
        </div><!-- /.modal -->
    </div>
</form>
```

在project_list.html的javascript部分增加如下js代码

```
        function initFileInput(ctrlName) {
            var control = $('#' + ctrlName);
            control.fileinput({
                resizeImage: true,
                resizePreference: 'width',
                uploadAsync: false,                             //采用同步上传
                language: 'zh', //设置语言
                uploadUrl: '/httpapitest/project/uploadfile',
                allowedFileExtensions: ['yml', 'yaml', 'json'],//接收的文件后缀
                showUpload: true, //是否显示上传按钮
                showRemove: false,
                showCaption: true,//是否显示标题
                browseClass: "btn btn-primary", //按钮样式
                previewFileIcon: "<i class='glyphicon glyphicon-king'></i>",
                maxFileCount: 10,
                msgFilesTooMany: "选择文件超过了最大数量",
                maxFileSize: 2000,
                uploadExtraData:
                    function () {     //上传时要传输的其他参数
                        project_name = $('#project option:selected').val();//选中的文本
                        module_name = $('#upload_belong_module_id option:selected').val();//选中的文本
                        return {"project": project_name, "module": module_name};
                    },
                showClose: false,//显示右上角X关闭
                overwriteInitial: false, //是否显示预览
                dropZoneEnabled: false,//是否显示拖拽区域
            });
            control.on('fileerror', function (event, data, msg) {
                myAlert(msg)
            });
            control.on("filebatchuploadsuccess", function (event, data) {
                var obj = data.response;
                $("#bulk_uploadcase").trigger('click');
                if (obj.status.indexOf('/httpapitest/') !== -1) {
                    window.location.href = obj.status;
                } else {
                    myAlert(obj.status);
                }
            });
        }

        initFileInput("uploadfile");
```

测试代码导入功能


## dashboard

1. 修改index的模板
index.html修改为以下链接中的内容

[index.html](./Chapter-13-code/hat/templates/index.html)


2. 修改index视图
```
def index(request):
    """
    首页
    :param request:
    :return:
    """
    project_length = Project.objects.count()
    module_length = Module.objects.count()
    test_length = TestCase.objects.count()
    suite_length = TestSuite.objects.count()
    

    total = get_total_values()
    manage_info = {
        'project_length': project_length,
        'module_length': module_length,
        'test_length': test_length,
        'suite_length': suite_length,
        'total': total
    }

    
    return render(request, 'index.html', manage_info)
```

## 登录，注册，退出功能
1. 在添加models.py 中添加类
```
class UserInfo(BaseTable):
    class Meta:
        verbose_name = '用户信息'
        db_table = 'UserInfo'

    username = models.CharField('用户名', max_length=20, unique=True, null=False)
    password = models.CharField('密码', max_length=20, null=False)
    email = models.EmailField('邮箱', null=False, unique=True)
    status = models.IntegerField('有效/无效', default=1)
    objects = UserInfoManager()
```
在models.py中导入
`from .managers import UserInfoManager`
2. 在managers.py 中添加类
```
class UserInfoManager(models.Manager):
    def insert_user(self, username, password, email, object):
        self.create(username=username, password=password, email=email, user_type=object)

    def query_user(self, username, password):
        return self.filter(username__exact=username, password__exact=password).count()
```

3. 添加视图函数
```
def login(request):
    """
    登录
    :param request:
    :return:
    """
    if request.method == 'POST':
        username = request.POST.get('account')
        password = request.POST.get('password')

        if UserInfo.objects.filter(username__exact=username).filter(password__exact=password).count() == 1:
            logger.info('{username} 登录成功'.format(username=username))
            request.session["login_status"] = True
            request.session["now_account"] = username
            return redirect('index')
        else:
            logger.info('{username} 登录失败, 请检查用户名或者密码'.format(username=username))
            return render(request, 'login.html', {'msg': '账号或密码不正确'})
    elif request.method == 'GET':
        return render(request, 'login.html')

@csrf_exempt
def register(request):
    """
    注册
    :param request:
    :return:
    """
    if request.is_ajax():
        user_info = json.loads(request.body.decode('utf-8'))
        try:
            username = user_info.get('account')
            password = user_info.get('password')
            email = user_info.get('email')
    
            if UserInfo.objects.filter(username__exact=username).filter(status=1).count() > 0:
                logger.debug('{username} 已被其他用户注册'.format(username=username))
                msg = '该用户名已被注册，请更换用户名'
            if UserInfo.objects.filter(email__exact=email).filter(status=1).count() > 0:
                logger.debug('{email} 昵称已被其他用户注册'.format(email=email))
                msg = '邮箱已被其他用户注册，请更换邮箱'
            else:
                UserInfo.obj
                ects.create(username=username, password=password, email=email)
                logger.info('新增用户：{user_info}'.format(user_info=user_info))
                msg =  'ok'
        except Exception as e:
            logger.error('信息输入有误：{user_info}'.format(user_info=user_info))
            msg =  e
        if msg == 'ok':
            return HttpResponse('恭喜您，账号已成功注册')
        else:
            return HttpResponse(msg)
    elif request.method == 'GET':
        return render(request, "register.html")


def logout(request):
    """
    注销登录
    :param request:
    :return:
    """
    if request.method == 'GET':
        logger.info('{username}退出'.format(username=request.session['now_account']))
        del request.session['now_account']
        del request.session['login_status']
        return redirect(login)
```


4. 添加模板

[login.html](./Chapter-13-code/hat/templates/login.html)
[register.html](./Chapter-13-code/hat/templates/register.html)

修改base.html
注销关联的url
 `href='{% url 'logout' %}'>注 销</a>`

 修改登录账号xxx 为`{{ request.session.now_account }}`


## 权限限制
1. 在views.py 导入语句的下面添加 login_check 装饰器

```
def login_check(func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('login_status'):
            return redirect(login)
        return func(request, *args, **kwargs)

    return wrapper
```
 5. 在所有视图函数上添加 `@login_check` login和register函数除外,因为这两个不需要登录



