import logging
from .models import TestConfig, Module
from django.db import DataError
from django.core.exceptions import ObjectDoesNotExist

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
                        value['expect'] = msg
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
            if name != TestConfig.objects.get(id=index).name \
                    and config_opt.get_config_name(name, module, project) > 0:
                return '用例或配置已在该模块中存在，请重新命名'
            config_opt.update_config(belong_module, **kwargs)
            logger.info('{name}配置更新成功: {kwargs}'.format(name=name, kwargs=kwargs))
    except DataError:
        logger.error('{name}配置信息过长：{kwargs}'.format(name=name, kwargs=kwargs))
        return '字段长度超长，请重新编辑'
    return 'ok'




