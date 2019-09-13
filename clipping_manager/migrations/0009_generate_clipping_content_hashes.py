from django.db import migrations, transaction


def gen_content_hash(apps, schema_editor):
    Clipping = apps.get_model('clipping_manager', 'Clipping')
    for c in Clipping.objects.all():
        with transaction.atomic():
            c.save()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('clipping_manager', '0008_auto_20190913_0945'),
    ]

    operations = [
        migrations.RunPython(gen_content_hash),
    ]