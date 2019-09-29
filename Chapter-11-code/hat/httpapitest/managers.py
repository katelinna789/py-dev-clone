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