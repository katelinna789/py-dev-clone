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



class TestCaseManager(models.Manager):
    def insert_case(self, belong_module, **kwargs):
        case_info = kwargs.get('test').pop('case_info')
        self.create(name=kwargs.get('test').get('name'), belong_project=case_info.pop('project'),
                    belong_module=belong_module,
                    author=case_info.pop('author'), include=case_info.pop('include'), request=kwargs)

    def update_case(self, belong_module, **kwargs):
        case_info = kwargs.get('test').pop('case_info')
        obj = self.get(id=case_info.pop('test_index'))
        obj.belong_project = case_info.pop('project')
        obj.belong_module = belong_module
        obj.name = kwargs.get('test').get('name')
        obj.author = case_info.pop('author')
        obj.include = case_info.pop('include')
        obj.request = kwargs
        obj.save()

    def get_case_name(self, name, module_name, belong_project):
        return self.filter(belong_module__id=module_name).filter(name__exact=name).filter(
            belong_project__exact=belong_project).count()

class EnvManager(models.Manager):
    def insert_env(self, **kwargs):
        self.create(**kwargs)

    def update_env(self, index, **kwargs):
        obj = self.get(id=index)
        obj.env_name = kwargs.pop('env_name')
        obj.base_url = kwargs.pop('base_url')
        obj.simple_desc = kwargs.pop('simple_desc')
        obj.save()

    def get_env_name(self, index):
        return self.get(id=index).env_name

    def delete_env(self, index):
        self.get(id=index).delete()



class UserInfoManager(models.Manager):
    def insert_user(self, username, password, email, object):
        self.create(username=username, password=password, email=email, user_type=object)

    def query_user(self, username, password):
        return self.filter(username__exact=username, password__exact=password).count()