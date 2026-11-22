from django.db import migrations, models
import apps.students.models


class Migration(migrations.Migration):
    dependencies = [('students', '0001_initial')]
    operations = [
        migrations.AddField(model_name='student', name='consent_at', field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name='student', name='consent_version', field=models.CharField(default='v1', max_length=20)),
        migrations.AlterField(model_name='document', name='passport', field=models.FileField(blank=True, null=True, upload_to='students/%Y/%m/%d/', validators=[apps.students.models.validate_upload])),
        migrations.AlterField(model_name='document', name='attestat', field=models.FileField(blank=True, null=True, upload_to='students/%Y/%m/%d/', validators=[apps.students.models.validate_upload])),
        migrations.AlterField(model_name='document', name='photo', field=models.ImageField(blank=True, null=True, upload_to='students/%Y/%m/%d/', validators=[apps.students.models.validate_upload])),
    ]
