from django.db import models


class AboutUs(models.Model):
    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=200)
    body = models.TextField()

    class Meta:
        db_table = 'aboutUs'
        verbose_name = 'Про нас'
        verbose_name_plural = 'Про нас'
    
    def __str__(self):
        return self.title

