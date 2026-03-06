from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_planning', '0004_alter_element_options_alter_element_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='testcase',
            name='tags',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
