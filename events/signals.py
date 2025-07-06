from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import User
from events.models import Event
from django.conf import settings
from users.models import HostEventRequest


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


# @receiver(post_save, sender=User)
# def send_user_registration_email(sender, instance, created, **kwargs):
#     if created:
#         user = instance

#         # Get assigned group
#         group = user.groups.first()
#         role = group.name if group else "No Role"

#         # Get assigned events if reverse relation is set
#         try:
#             events = user.joined_events.all()
#             event_names = ", ".join([e.name for e in events]) if events else "None"
#         except:
#             event_names = "N/A"

#         # Build password reset link
#         current_site = get_current_site(
#             None
#         )  # Only works if SITE ID is set OR passed manually
#         domain = current_site.domain if current_site else "127.0.0.1:8000"
#         reset_url = reverse("password_reset")
#         full_link = f"http://{domain}{reset_url}"

#         subject = "🎉 Welcome to EventX - Your Participant Account Info"
#         message = f"""
#         Hi {user.first_name},

#         You have been registered successfully as a participant.

#         🧾 Your Details:
#         - Username: {user.username}
#         - Email: {user.email}
#         - Name: {user.first_name} {user.last_name}
#         - Role: {role}
#         - Events: {event_names}

#         🔐 Please change your password here:
#         {full_link}

#         Best,
#         EventX Team
#         """.strip()

#         send_mail(
#             subject,
#             message,
#             None,  # Uses DEFAULT_FROM_EMAIL
#             [user.email],
#             fail_silently=False,
#         )


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
