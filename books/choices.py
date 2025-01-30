from django.db import models
from django.utils.translation import gettext_lazy as _

class DeliverChoices(models.TextChoices):
    PICK_UP = 'pick_up', _('Ready to Pick Up')
    DELIVER = 'delivering', _('Can Be DElivered')