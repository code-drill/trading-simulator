from django.db import models

# Create your models here.

class Market(models.Model):
    code = models.CharField(max_length=20, unique=True, primary_key=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Market"
        verbose_name_plural = "Markets"