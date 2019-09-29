
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
    path('debugtalk/list', views.debugtalk_list, name='debugtalk_list'),
    path('debugtalk/edit/<int:id>', views.debugtalk_edit, name='debugtalk_edit'),
    path('config/add', views.config_add, name='config_add'),
    path('config/list', views.config_list, name='config_list'),
    path('config/copy', views.config_copy, name='config_copy'),
    path('config/delete', views.config_delete, name='config_delete'),
    path('config/edit/<int:id>', views.config_edit, name='config_edit'),
]