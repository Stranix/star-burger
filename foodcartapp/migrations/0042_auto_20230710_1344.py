# Generated by Django 3.2.15 on 2023-07-10 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, default='', verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('NEW', 'Новый'), ('COLLECT', 'В сборке'), ('IN_DELIVERY', 'У курьера'), ('COMPLETED', 'Завершен')], db_index=True, default='NEW', max_length=11, verbose_name='Cтатус'),
        ),
    ]
