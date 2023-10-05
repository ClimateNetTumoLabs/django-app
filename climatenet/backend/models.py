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

class DeviceDetail(models.Model):
    name = models.CharField(max_length=200)
    parent_name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=18, decimal_places=15)
    longitude = models.DecimalField(max_digits=18, decimal_places=15)

    def __str__(self):
        return f"{self.id}"

class About(models.Model):
    title = models.TextField()
    mission = models.TextField()
    who_we_are = models.TextField()
    what_we_do = models.TextField()
    collaborate_text = models.TextField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.title}"

class Footer(models.Model):
    address = models.CharField(max_length=200, verbose_name="Map Icon")
    phone = models.CharField(max_length=20, verbose_name="Phone Icon")
    email = models.EmailField(verbose_name="Email Icon")

    def __str__(self):
        return "Footer Information"

class ContactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.email}"
