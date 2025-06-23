from django.urls import path

from events.views import (
    # home_view,
    create_event,
    join_event,
    dashboard_view,
    view_detail_dash,
    edit_event,
    delete_event,
    view_event,
    view_detail,
    view_category,
    add_category,
    edit_category,
    delete_category,
    view_participant,
    add_participant,
    edit_participant,
    delate_participant,
    about_us,
)


urlpatterns = [
    # path("home/", home_view, name="home"),
    path("create-event/", create_event, name="create_event"),
    path("join-event/<int:id>/", join_event, name="join_event"),  # --> Join Event...
    #
    path("dashboard/", dashboard_view, name="dashboard"),
    path("event-dash/<int:id>/", view_detail_dash, name="eDetails_D"),
    path("edit-event/<int:id>/", edit_event, name="edit_event"),
    path("event-delate/<int:id>/", delete_event, name="delete_event"),
    #
    path("view-event/", view_event, name="event"),
    path("event/<int:id>/", view_detail, name="eDetails"),
    #
    path("view-category/", view_category, name="category"),
    path("add-category/", add_category, name="add_category"),
    path("edit-category/<int:id>/", edit_category, name="edit_category"),
    path("delete-category/<int:id>/", delete_category, name="delete_category"),
    #
    path("view-participant/", view_participant, name="participant"),
    path("add-participant/", add_participant, name="add_participant"),
    path("edit-participant/<int:id>/", edit_participant, name="edit_participant"),
    path("delate-participant/<int:id>/", delate_participant, name="delate_participant"),
    #
    path("about-us/", about_us, name="about_us"),
]
