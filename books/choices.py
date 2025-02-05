from django.db import models
from django.utils.translation import gettext_lazy as _

class DeliverChoices(models.TextChoices):
    PICK_UP = 'pick_up', _('Готов до видачі')
    DELIVER = 'delivering', _('Може бути доставлений')