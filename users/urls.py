from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordChangeDoneView
from users.views import (
    group_list,
    create_group,
    organizer_dashboard,
    host_event_request,
    #
    SignUp,
    ActivateUser,
    CustomLogIN,
    AdminDashboard,
    ViewRole,
    AssignRoleView,
    #
    ProfileView,
    UpdateProfile,
    ChangePassword,
)


urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("edit-profile/", UpdateProfile.as_view(), name="edit-profile"),
    path("password-change/", ChangePassword.as_view(), name="password-change"),
    path(
        "password-change/done/",
        PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html"
        ),
        name="password_change_done",
    ),
    #
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
]
