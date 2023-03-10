# Generated by Django 3.2 on 2021-04-24 00:42

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='abdominal_pain',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='comorbidities',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submission',
            name='cough',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='diarrhea',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='faint',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='flu',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='hard_to_breathe',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='headache',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='muscleache',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='nausea',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='other_conditions',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submission',
            name='shiver',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='sore_throat',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Symptom',
        ),
    ]
