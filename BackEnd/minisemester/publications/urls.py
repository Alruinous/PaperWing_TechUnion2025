from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_publication_file_view, name="publication_upload"),
    path("create/", views.create_publication_view, name="publication_create"),
    path("comment/", views.create_publication_comment_view, name="create_publication_comment"),
    path("favour/", views.like_publication_view, name="like_publication"),
    path("get_article/", views.get_publication_detail_view, name="get_publication_detail"),
    # path('getParticipantStatus/', views.get_participant_status_view, name='get_participant_status'),
    path("comments/", views.get_publication_comments_view, name="get_publication_comments"),
    path('check_duplicate/', views.check_duplicate_view, name='check_publication_duplicate'),
    path('user-publication/', views.user_publication_view, name='user_publication'),
    path("cancelfavor/", views.cancelfavor, name="cancelfavor"),
    path('respond_claim/', views.respond_claim_view, name='respond_claim'),
    path('check_claim_ownership/', views.check_claim_ownership_view, name='check_claim_ownership'),
    path('sendemail/', views.send_email_to_followers_view, name='send_email_to_followers'),
    path('search/', views.search_publications_view, name='publication_search'),
    path('recommend/', views.get_recommended_publications_view, name='get_recommended_publications_view'),
    path('uploadFullText/', views.upload_full_text_view, name='publication_upload_full_text'),
    path('searchAI/', views.search_ai_summary_view, name='publication_search_ai'),
    path('add_reading_history/', views.add_reading_history_view, name='add_reading_history'),
]