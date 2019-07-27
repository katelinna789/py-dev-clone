# 第十三天

## 测试报告
异步执行生成报告存入数据库

1. 在modules.py 中添加 模型TestReports
···
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
···

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
```
需要导入 TestReports类

3. 添加report_list.html模板
[report_list.html](./Chapter-12-code/hat/templates/report_list.html)

4. 添加url
```
path('report/list', views.report_list, name='report_list'),
```

## 添加异步执行能
1. 添加异步运行所需要的task.py文件

[tasks.py](./Chapter-12-code/hat/httpapitest/tasks.py)

2. 在settings.py 所在目录添加cerlery.py 文件
[celery.py](./Chapter-12-code/hat/hat/celery.py)

3. 修改settings.py 添加celery相关配置
[settings.py](./Chapter-12-code/hat/hat/settings.py)
```
CELERY_BROKER_URL = 'redis://192.168.1.5:6379/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

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







