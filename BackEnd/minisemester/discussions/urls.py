from django.urls import path
from . import views

urlpatterns = [
    # 根据您的接口文档，路径为 /create_conversation
    path('create_conversation/', views.create_conversation_view, name='create_conversation'),
    path("sendMessages/", views.send_message_view, name="send_message"),
    path("getMessages/", views.get_messages_view, name="get_messages"),
    path("createProjectOrQuestion/", views.create_project_or_question, name="create_project_or_question"),
    path('getCreatedProjects/', views.get_created_projects_view, name='get_created_projects'),
    path('getParticipantStatus/', views.get_participant_status_view, name='get_participant_status'),
    path('projectdetail/', views.get_project_detail_view, name='get_project_detail'),
    path('respondInvitation/', views.respond_invitation_view, name='respond_invitation'),
    path('joined/', views.joined_projects_view, name='joined_projects'),
    path('postreply/', views.post_reply_view, name='post_reply'),
    path('projectreplies/', views.project_replies_view, name='project_replies'),
    path('questionreplies/', views.question_replies_view, name='question_replies'),
    path('questiondetail/', views.question_detail_view, name='question_detail'),
    path('forum/', views.get_forum, name='get_forum'),
    path('followQuestion/', views.followQuestion, name='followQuestion'),
    path('unfollowQuestion/', views.unfollowQuestion, name='unfollowQuestion'),
    path('projectAI/', views.project_ai_summary_view, name='project_ai_summary'),
    path('deleteMembers/', views.delete_member_view, name='delete_member'),
]
