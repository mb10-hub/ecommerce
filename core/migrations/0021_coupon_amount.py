# Generated by Django 3.0.7 on 2020-06-17 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_order_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='amount',
            field=models.FloatField(default=5),
            preserve_default=False,
        ),
    ]