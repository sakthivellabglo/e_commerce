# Generated by Django 4.1.2 on 2022-11-25 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_remove_order_tax_remove_order_total_product_cost_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_price',
            field=models.IntegerField(default=12345),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='total_price',
            field=models.IntegerField(default=43421),
            preserve_default=False,
        ),
    ]