
from django.urls import path
from httpapitest import views

urlpatterns = [
    path('', views.index, name='index'),
    path('project/list', views.project_list, name='project_list'),
    path('project/add', views.project_add, name='project_add'),
    path('project/edit', views.project_edit, name='project_edit'),
    path('project/delete', views.project_delete, name='project_delete'),
    path('module/list', views.module_list, name='module_list'),
    path('module/add', views.module_add, name='module_add'),
    path('module/edit', views.module_edit, name='module_edit'),
    path('module/delete', views.module_delete, name='module_delete'),
    path('module/search/ajax', views.module_search_ajax, name='module_search_ajax'),
]