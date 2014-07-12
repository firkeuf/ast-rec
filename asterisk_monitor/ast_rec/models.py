from django.db import models
from django.conf import settings


class Cdr(models.Model):
    id = models.IntegerField(primary_key=True)
    calldate = models.DateTimeField()
    clid = models.CharField(max_length=80)
    src = models.CharField(max_length=80)
    dst = models.CharField(max_length=80)
    dcontext = models.CharField(max_length=80)
    channel = models.CharField(max_length=80)
    dstchannel = models.CharField(max_length=80)
    lastapp = models.CharField(max_length=80)
    lastdata = models.CharField(max_length=80)
    duration = models.IntegerField()
    billsec = models.IntegerField()
    disposition = models.CharField(max_length=45)
    amaflags = models.IntegerField()
    accountcode = models.CharField(max_length=20)
    uniqueid = models.CharField(max_length=32)
    peeraccount = models.CharField(max_length=20)
    linkedid = models.CharField(max_length=32)
    sequence = models.IntegerField()
    userfield = models.CharField(max_length=255)
    #import_cdr = models.IntegerField()
    #acctid = models.IntegerField()

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.channel

    class Meta:
        managed = False
        db_table = settings.DATABASES['asterisk_db']['TABLE']
        permissions = (
            ('can_listen', "Can listen call records"),
        )


class ChannelList(models.Model):
    name = models.CharField(max_length=80)
    value = models.CharField(max_length=80)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name

    def update_list(self):
        channel_qs = ChannelList.objects.order_by('-pk')
        present_channels = set()
        raw_channels = set()

        for ch in channel_qs:
            present_channels.add(ch.value)

        raw_channels_qs = Cdr.objects.using('asterisk_bd').order_by('-calldate').all()[:500]  # [:5000 * 1 / (channel_qs[0].id + 1)] #TODO: need first channel
        for call in raw_channels_qs:
            if not 'Bridge' in call.channel:
                channel = call.channel.split('-')[0].split('/')[1]
                if '@' in channel:
                    pass
                else:
                    raw_channels.add(channel)
        new_channels = raw_channels - present_channels
        for channel in sorted(new_channels):
            entry = ChannelList(name=channel, value=channel)
            entry.save()

    def get_list(self):
        self.update_list()
        result = []
        chanels_qs = ChannelList.objects.order_by('name')
        for channel in chanels_qs:
            result.append((channel.value, channel.name))
        return result

