from django.urls import path
from users.views import (
    sign_up,
    sign_in,
    sign_out,
    activate_user,
    admin_dashboard,
    group_list,
    create_group,
    assign_role,
    view_role,
    organizer_dashboard,
    host_event_request,
    change_password,
    password_change_done,
)

urlpatterns = [
    path("sign-up/", sign_up, name="sign-up"),
    path("sign-in/", sign_in, name="sign-in"),
    path("sign-out/", sign_out, name="sign-out"),
    path("activate/<int:user_id>/<str:token>/", activate_user, name="activate"),
    path("admin/dashboard/", admin_dashboard, name="admin-dashboard"),
    path("admin/group-list/", group_list, name="group-list"),
    path("admin/create-group/", create_group, name="create-group"),
    path("admin/<int:user_id>/assign-role/", assign_role, name="assign-role"),
    path("admin/view-role/", view_role, name="view-role"),
    path("organizer/dashboard/", organizer_dashboard, name="organizer-dashboard"),
    path("host-event/", host_event_request, name="host-event"),
    #
    path("change-password/", change_password, name="change_password"),
    path("password-changed/", password_change_done, name="password_change_done"),
]
