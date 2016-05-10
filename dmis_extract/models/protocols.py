from django.db import models


class Protocol(models.Model):

    """
    Example to import from dataframe

    from .db import Db

    db = Db('BHPLAB', 'bhplab')
    data = db.protocol[db.protocol['identifier'].str.startswith('BHP')]
    for item in data.itertuples():
        options = item._asdict()
        del options['Index']
        Protocol.objects.create(**options)

    """

    identifier = models.CharField(max_length=25)

    title = models.CharField(max_length=250)

    category = models.CharField(max_length=50)

    class Meta:
        app_label = 'dmis_extract'


class DictionaryList(models.Model):

    """DMIS ref"""

    identifier = models.CharField(max_length=10)

    title = models.CharField(max_length=150)

    protocol = models.CharField(max_length=10)

    form_version = models.CharField(max_length=10)

    category = models.CharField(max_length=25, null=True)

    dmis_id = models.CharField(max_length=25, null=True)

    class Meta:
        app_label = 'dmis_extract'
