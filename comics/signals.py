import os
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from comics.models import Arc, Character, Creator, Issue, Publisher, Team

@receiver(pre_delete, sender=Issue)
def model_pre_delete(sender, **kwargs):
	os.remove(kwargs['instance'].cover)

@receiver(pre_delete, sender=Publisher)
def model_pre_delete(sender, **kwargs):
	os.remove(kwargs['instance'].logo)

@receiver(pre_delete, sender=Arc)
@receiver(pre_delete, sender=Creator)
@receiver(pre_delete, sender=Team)
@receiver(pre_delete, sender=Character)
def model_pre_delete(sender, **kwargs):
	os.remove(kwargs['instance'].image)
