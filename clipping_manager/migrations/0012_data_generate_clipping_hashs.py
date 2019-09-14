from django.db import migrations, transaction



def gen_content_hash(apps, schema_editor):
    from clipping_manager.models import Clipping
    # Clipping = apps.get_model('clipping_manager', 'Clipping')
    for c in Clipping.objects.all():
        c.save()


class Migration(migrations.Migration):
    # atomic = False

    dependencies = [
        ('clipping_manager', '0011_auto_20190914_0519'),
    ]

    operations = [
        migrations.RunPython(gen_content_hash, migrations.RunPython.noop),
    ]
