import json
from django.shortcuts import render,reverse,redirect
from django.shortcuts import HttpResponse
from httpapitest.models import Project,Module,DebugTalk,TestConfig
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .utils import config_logic
import logging

logger = logging.getLogger('django')
# Create your views here.
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def project_add(request):
    if request.is_ajax():
        project = json.loads(request.body.decode('utf-8'))
        if project.get('project_name') == '':
            msg = '项目名称不能为空'
            return HttpResponse(msg)
        if project.get('responsible_name') == '':
            msg = '负责人不能为空'
            return HttpResponse(msg)
        if project.get('test_user') == '':
            msg = '测试人员不能为空'
            return HttpResponse(msg)
        if project.get('dev_user') == '':
            msg = '开发人员不能为空'
            return HttpResponse(msg)
        if project.get('publish_app') == '':
            msg = '发布应用不能为空'
            return HttpResponse(msg)
        if Project.objects.filter(project_name=project.get('project_name')):
            msg = "项目已经存在"
            return HttpResponse(msg)
        else:
            p = Project()
            p.project_name = project.get('project_name')
            p.responsible_name = project.get('responsible_name')
            p.test_user = project.get('test_user')
            p.dev_user = project.get('dev_user')
            p.publish_app = project.get('publish_app')
            p.simple_desc = project.get('simple_desc')
            p.other_desc = project.get('other_desc')
            p.save()
            d = DebugTalk()
            d.belong_project = p
            d.save()
            msg = 'ok'
        if msg == 'ok':
            return HttpResponse(reverse('project_list'))
        else:
            return HttpResponse(msg)

    if request.method == 'GET':
        return render(request, 'project_add.html')

@csrf_exempt
def project_list(request):
    if request.method == "GET":
        projects = Project.objects.all().order_by("-update_time")
        rs = Project.objects.all().order_by("-update_time")
        paginator = Paginator(rs,5)
        page = request.GET.get('page')
        objects = paginator.get_page(page)
        context_dict = {'project': objects,'all_projects': projects}
        return render(request,"project_list.html",context_dict)

    if request.method == 'POST':
        projects = Project.objects.all().order_by("-update_time")
        project_name = request.POST.get('project')
        if project_name != "All":
            rs = Project.objects.filter(project_name=project_name)
        user = request.POST.get('user')
        if user:
            rs = Project.objects.filter(responsible_name=user)
        paginator = Paginator(rs,5)
        page = request.GET.get('page')
        objects = paginator.get_page(page)
        context_dict = {'project': objects, 'all_projects': projects}
        return render(request,"project_list.html",context_dict)

@csrf_exempt
def project_edit(request):
    if request.is_ajax():
        project = json.loads(request.body.decode('utf-8'))
        if project.get('project_name') == '':
            msg = '项目名称不能为空'
            return HttpResponse(msg)
        if project.get('responsible_name') == '':
            msg = '负责人不能为空'
            return HttpResponse(msg)
        if project.get('test_user') == '':
            msg = '测试人员不能为空'
            return HttpResponse(msg)
        if project.get('dev_user') == '':
            msg = '开发人员不能为空'
            return HttpResponse(msg)
        if project.get('publish_app') == '':
            msg = '发布应用不能为空'
            return HttpResponse(msg)
        else:
            p = Project.objects.get(project_name=project.get('project_name'))
            p.responsible_name = project.get('responsible_name')
            p.test_user = project.get('test_user')
            p.dev_user = project.get('dev_user')
            p.publish_app = project.get('publish_app')
            p.simple_desc = project.get('simple_desc')
            p.other_desc = project.get('other_desc')
            p.save()
            msg = 'ok'
        if msg == 'ok':
            return HttpResponse(reverse('project_list'))
        else:
            return HttpResponse(msg)

@csrf_exempt
def project_delete(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        project_id = data.get('id')
        project = Project.objects.get(id=project_id)
        project.delete()
        return HttpResponse(reverse('project_list'))



@csrf_exempt
def module_add(request):
    if request.method == 'GET':
        projects = Project.objects.all().order_by("-update_time")
        context_dict = {'data': projects}
        return render(request, 'module_add.html',context_dict)
    if request.is_ajax():
        module = json.loads(request.body.decode('utf-8'))
        if module.get('module_name') == '':
            msg = '模块名称不能为空'
            return HttpResponse(msg)
        if module.get('belong_project') == '请选择':
            msg = '请选择项目，没有请先添加哦'
            return HttpResponse(msg)
        if module.get('test_user') == '':
            msg = '测试人员不能为空'
            return HttpResponse(msg)
        p = Project.objects.get(project_name=module.get('belong_project'))
        if Module.objects.filter(module_name=module.get('module_name'), belong_project=p):
            msg = "项目已经存在"
            return HttpResponse(msg)
        else:
            m = Module()
            m.module_name = module.get('module_name')
            p = Project.objects.get(project_name=module.get('belong_project'))
            m.belong_project = p
            m.test_user = module.get('test_user')
            m.simple_desc = module.get('simple_desc')
            m.other_desc = module.get('other_desc')
            m.save()
            msg = 'ok'
        if msg == 'ok':
            return HttpResponse(reverse('module_list'))
        else:
            return HttpResponse(msg)

@csrf_exempt
def module_list(request):
    if request.method == 'GET':
        info = {'belong_project': 'All', 'belong_module': "请选择"}
        projects = Project.objects.all().order_by("-update_time")
        rs = Module.objects.all().order_by("-update_time")
        paginator = Paginator(rs,5)
        page = request.GET.get('page')
        objects = paginator.get_page(page)
        context_dict = {'module': objects, 'projects': projects, 'info': info}
        return render(request,"module_list.html",context_dict)
    if request.method == 'POST':
        
        projects = Project.objects.all().order_by("-update_time")
        project = request.POST.get("project")
        module = request.POST.get("module")
        user = request.POST.get("user")
        
        if project == "All":
            if user:
                rs = Module.objects.filter(test_user=user).order_by("-update_time")
               
            else:
                rs = Module.objects.all().order_by("-update_time")
        else:
            p = Project.objects.get(project_name=project)
            if module != "请选择":
                if user:
                    rs = Module.objects.filter(id=module, belong_project=p, test_user=user).order_by("-update_time")
                else:
                    rs = Module.objects.filter(id=module, belong_project=p).order_by("-update_time")
                module = Module.objects.get(id=module)
            else:
                if user:
                    rs = Module.objects.filter(belong_project=p, test_user=user).order_by("-update_time")
                else:
                    rs = Module.objects.filter(belong_project=p).order_by("-update_time")
    paginator = Paginator(rs,5)
    page = request.GET.get('page')
    objects = paginator.get_page(page)
    context_dict = {'module': objects, 'projects': projects, 'info': {'belong_project': project,'belong_module': module, 'user':user}}
    return render(request,"module_list.html",context_dict)

@csrf_exempt
def module_edit(request):
    if request.is_ajax():
        module = json.loads(request.body.decode('utf-8'))
        
        if module.get('module_name') == '':
            msg = '模块名称不能为空'
            return HttpResponse(msg)
        if module.get('belong_project') == '请选择':
            msg = '请选择项目，没有请先添加哦'
            return HttpResponse(msg)
        if module.get('test_user') == '':
            msg = '测试人员不能为空'
            return HttpResponse(msg)
        p = Project.objects.get(project_name=module.get('belong_project'))
        if Module.objects.filter(module_name=module.get('module_name'), belong_project=p):
            msg = "模块已经存在"
            return HttpResponse(msg)
        else:
            m = Module.objects.get(id=module.get('index'))
            m.module_name = module.get('module_name')
            m.belong_project = p
            m.test_user = module.get('test_user')
            m.simple_desc = module.get('simple_desc')
            m.other_desc = module.get('other_desc')
            m.save()
            msg = 'ok'
        if msg == 'ok':
            return HttpResponse(reverse('module_list'))
        else:
            return HttpResponse(msg)

@csrf_exempt
def module_delete(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        project_id = data.get('id')
        module = Module.objects.get(id=project_id)
        module.delete()
        return HttpResponse(reverse('module_list'))


@csrf_exempt
def module_search_ajax(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        if 'test' in data.keys():
            project = data["test"]["name"]["project"]
        if 'config' in data.keys():
            project = data["config"]["name"]["project"]
        if  project != "All" and project != "请选择":
            p = Project.objects.get(project_name=project)
            modules = Module.objects.filter(belong_project=p)
            modules_list = ['%d^=%s' % (m.id, m.module_name) for m in modules ]
            modules_string = 'replaceFlag'.join(modules_list)
            return HttpResponse(modules_string)
        else:
            return HttpResponse('')

def debugtalk_list(request):
    if request.method == "GET":
        rs = DebugTalk.objects.all().order_by("-update_time")
        paginator = Paginator(rs,5)
        page = request.GET.get('page')
        objects = paginator.get_page(page)
        context_dict = {'debugtalk': objects }
        return render(request,"debugtalk_list.html",context_dict)

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



@csrf_exempt
def config_delete(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        config_id = data.get('id')
        config = TestConfig.objects.get(id=config_id)
        config.delete()
        return HttpResponse(reverse('config_list'))

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




