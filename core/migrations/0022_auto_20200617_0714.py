# Generated by Django 3.0.7 on 2020-06-17 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_coupon_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='being_delivered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='received',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='refund_granted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='refund_request',
            field=models.BooleanField(default=False),
        ),
    ]
