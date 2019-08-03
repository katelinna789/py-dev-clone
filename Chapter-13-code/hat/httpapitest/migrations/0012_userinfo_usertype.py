# Generated by Django 2.2.2 on 2019-08-03 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('httpapitest', '0011_auto_20190801_2233'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('username', models.CharField(max_length=20, unique=True, verbose_name='用户名')),
                ('password', models.CharField(max_length=20, verbose_name='密码')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='邮箱')),
                ('status', models.IntegerField(default=1, verbose_name='有效/无效')),
            ],
            options={
                'verbose_name': '用户信息',
                'db_table': 'UserInfo',
            },
        ),
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('type_name', models.CharField(max_length=20)),
                ('type_desc', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': '用户类型',
                'db_table': 'UserType',
            },
        ),
    ]
