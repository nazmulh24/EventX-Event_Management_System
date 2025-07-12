from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from events.models import Event
from django.conf import settings
from users.models import HostEventRequest

from django.contrib.auth import get_user_model

User = get_user_model()


# -----> Sending Email
@receiver(m2m_changed, sender=Event.participants.through)
def notify_users_on_task_creation(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        new_users = User.objects.filter(pk__in=pk_set)

        for user in new_users:
            send_mail(
                subject="Confirmation Mail",
                message=f"Hello {user.first_name},\n\nYou have successfully perticipate the event : {instance.username}.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )


@receiver(post_save, sender=HostEventRequest)
def send_host_request_email(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        full_name = f"{user.first_name} {user.last_name}".strip()
        subject = "Organizer Role Request"
        message = f"""
        📢 New Organizer Request

        🧑 Username : {user.username}
        📧 Email : {user.email}
        🪪 Full Name : {full_name}
        📝 Motivation :
        {instance.motivation}
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )
