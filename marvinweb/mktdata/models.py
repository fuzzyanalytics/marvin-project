from django.db import models


# Create your models here.
class Dukaeurusdtick(models.Model):
    timestamp = models.DateTimeField(primary_key=True)
    bid = models.FloatField()
    ask = models.FloatField()
    bid_volume = models.FloatField()
    ask_volume = models.FloatField()

    class Meta:
        managed = False
        db_table = 'dukaeurusdtick'
        ordering = ["timestamp"]
