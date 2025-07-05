from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("check-account-or-email/", views.check_account_or_email_view, name="check_account_or_email"),
    path("userinfo/", views.user_info_view, name="userinfo"),
    path("updateinfo/", views.update_user_info_view, name="updateinfo"),
    path('messages/', views.get_messages, name='get_messages'),
    path('authors/', views.get_authors, name='get_authors'),
    path("check_author_ownership/", views.check_author_ownership_view, name="check_author_ownership"),
    path('follow/', views.follow, name='follow'),
    path('unfollow/', views.unfollow, name='unfollow'),
    path('followers/', views.get_followers_view, name='followers'),
    path('same-institution/', views.get_same_institution_users_view, name='same_institution_users'),
    path('following/', views.get_following_view, name='following'),
    path('reading-history/', views.get_reading_history_view, name='reading_history'),
    path('searchScholar/', views.searchScholar, name='searchScholar'),
    path('search/', views.search_users_by_name_view, name='search_users_by_name'),
]
