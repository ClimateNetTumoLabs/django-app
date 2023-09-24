from django.db import models

class Device(models.Model):
    time = models.DateTimeField()
    light = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    pm1 = models.FloatField(null=True, blank=True)
    pm2_5 = models.FloatField(null=True, blank=True)
    pm10 = models.FloatField(null=True, blank=True)
    co2 = models.FloatField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    rain = models.FloatField(null=True, blank=True)
    direction = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Device {self.id}"

