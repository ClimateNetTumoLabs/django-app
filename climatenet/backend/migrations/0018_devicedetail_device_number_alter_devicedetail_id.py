# Generated by Django 4.2.5 on 2023-10-05 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0017_alter_devicedetail_latitude_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicedetail',
            name='device_number',
            field=models.CharField(default=45, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='devicedetail',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
