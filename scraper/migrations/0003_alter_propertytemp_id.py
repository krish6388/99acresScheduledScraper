# Generated by Django 4.1.11 on 2023-09-16 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0002_alter_property_id_alter_propertybkp_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propertytemp',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
