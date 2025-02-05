# Generated by Django 3.2.15 on 2023-07-10 12:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_order_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(blank=True, help_text='ресторан выполнения заказа', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='foodcartapp.restaurant', verbose_name='ресторан'),
        ),
        migrations.AlterField(
            model_name='orderelement',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_in_order', to='foodcartapp.order', verbose_name='Заказ'),
        ),
    ]
