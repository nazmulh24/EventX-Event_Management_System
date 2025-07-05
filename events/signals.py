from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import User
from events.models import Event
from django.conf import settings


# -----> Sending Email
@receiver(m2m_changed, sender=Event.participants.through)
def notify_users_on_task_creation(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        new_users = User.objects.filter(pk__in=pk_set)

        for user in new_users:
            send_mail(
                subject="Confirmation Mail",
                message=f"Hello {user.first_name},\n\nYou have successfully perticipate the event : {instance.name}.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
