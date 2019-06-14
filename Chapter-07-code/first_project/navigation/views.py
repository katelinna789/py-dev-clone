from django.http import HttpResponse
from django.shortcuts import render
def index(request):
    # 构建一个字典，作为上下文传给模板引擎
    # 注意， boldmessage 键对应于模板中的 {{ boldmessage }}
    context_dict = {'boldmessage': "女神, 屌丝, pythoner"}
    # 返回一个渲染后的响应发给客户端
    # 为了方便，我们使用的是 render 函数的简短形式
    # 注意，第二个参数是我们想使用的模板
    return render(request, 'navigation/index.html', context=context_dict)

def about(request):
    #return HttpResponse("龙腾测试！！！ <a href='/navigation/'>首页</a>")
    return render(request, 'navigation/about.html')