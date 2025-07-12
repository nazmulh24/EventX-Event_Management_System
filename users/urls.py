from django.urls import path
from users.views import (
    group_list,
    create_group,
    organizer_dashboard,
    host_event_request,
    change_password,
    password_change_done,
    #
    SignUp,
    ActivateUser,
    CustomLogIN,
    AdminDashboard,
    ViewRole,
    AssignRoleView,
)
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path("sign-up/", SignUp.as_view(), name="sign-up"),
    path(
        "activate/<int:user_id>/<str:token>/",
        ActivateUser.as_view(),
        name="activate-user",
    ),
    path("sign-in/", CustomLogIN.as_view(), name="sign-in"),
    path("sign-out/", LogoutView.as_view(), name="sign-out"),
    path("admin/dashboard/", AdminDashboard.as_view(), name="admin-dashboard"),
    path("admin/view-role/", ViewRole.as_view(), name="view-role"),
    path(
        "admin/<int:user_id>/assign-role/", AssignRoleView.as_view(), name="assign-role"
    ),
    #
    path("admin/group-list/", group_list, name="group-list"),
    path("admin/create-group/", create_group, name="create-group"),
    path("organizer/dashboard/", organizer_dashboard, name="organizer-dashboard"),
    path("host-event/", host_event_request, name="host-event"),
    #
    path("change-password/", change_password, name="change_password"),
    path("password-changed/", password_change_done, name="password_change_done"),
]
