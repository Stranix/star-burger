# Generated by Django 3.2.15 on 2023-07-10 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_auto_20230710_1353'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('IMMEDIATE', 'Сразу'), ('BANK_CARD', 'Картой'), ('CASH', 'Наличными')], db_index=True, default='BANK_CARD', max_length=9, verbose_name='Способ оплаты'),
        ),
    ]
