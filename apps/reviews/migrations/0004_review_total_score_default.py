# Generated migration for adding default value to total_score

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_review_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='total_score',
            field=models.PositiveSmallIntegerField(default=0, editable=False, verbose_name='Итоговый балл'),
        ),
    ]
