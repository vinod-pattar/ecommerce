# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Cart
from django.core.mail import send_mail

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Create a Profile for the new user
        Profile.objects.create(user=instance,)

        Cart.objects.create(user=instance)

        # Send a welcome email
        # subject = "Welcome to Our Platform!"
        # message = f"Hi {instance.username},\n\nThank you for signing up! We are excited to have you on board."
        # from_email = "ecommerce@example.com"
        # recipient_list = [instance.email]
        
        # send_mail(subject, message, from_email, recipient_list)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    # Save the profile whenever the user is saved (in case the user profile is updated)
    instance.profile.save()
