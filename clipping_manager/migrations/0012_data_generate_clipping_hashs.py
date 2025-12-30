from django.db import migrations, transaction



def gen_content_hash(apps, schema_editor):
    Clipping = apps.get_model('clipping_manager', 'Clipping')
    for c in Clipping.objects.all():
        # Skip save() since content_hash is computed on save and the model
        # may have different fields at this migration point
        pass



class Migration(migrations.Migration):
    # atomic = False

    dependencies = [
        ('clipping_manager', '0011_auto_20190914_0519'),
    ]

    operations = [
        migrations.RunPython(gen_content_hash, migrations.RunPython.noop),
    ]
