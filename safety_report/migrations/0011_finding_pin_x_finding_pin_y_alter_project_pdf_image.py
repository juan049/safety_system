# Generated by Django 5.1.1 on 2024-10-11 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('safety_report', '0010_delete_image_project_pdf_image_project_pdf_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='finding',
            name='pin_x',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='finding',
            name='pin_y',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='pdf_image',
            field=models.ImageField(blank=True, null=True, upload_to='projects/pdf_images/'),
        ),
    ]
