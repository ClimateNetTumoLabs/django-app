# Generated by Django 4.2.4 on 2023-08-12 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomePage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('par1', models.CharField(max_length=100)),
                ('par2', models.TextField()),
            ],
        ),
        migrations.DeleteModel(
            name='Page',
        ),
        migrations.AlterField(
            model_name='devicedetails',
            name='country',
            field=models.CharField(default='Armenia', max_length=100),
        ),
    ]
