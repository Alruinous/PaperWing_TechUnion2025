from django.urls import path
from . import views

urlpatterns = [
    path("getCollection/", views.getCollection, name="getCollection"),
    path('upload/', views.upload_document_view, name='upload_document'),
    path('check_duplicate/', views.check_duplicate_view, name='check_duplicate'),
    path('ai/', views.generate_ai_summary_view, name='ai_summary'),
    path('add_reading_history/', views.add_reading_history_view, name='add_document_reading_history'),

    # 技术速递订阅管理
    path('analysisrequest/', views.manage_subscription_view,
         name='analysis_request'),

    # 获取技术速递报告
    path('getanalysis/', views.get_analysis_report_view, name='get_analysis'),

    # 检查报告生成状态
    path('isgenerated/', views.check_report_status_view, name='is_generated'),

    # [开发用] 手动触发报告生成
    path('trigger-generation/', views.trigger_manual_report_generation_view,
         name='trigger_generation'),

     path('get_favorite_category/', views.get_favorite_category, name='get_favorite_category'),
     path('add_favorite_category/', views.add_favorite_category, name='add_favorite_category'),
     path('get_all_docs/', views.get_all_docs, name='get_all_docs'),
     path('addFavorite/', views.addFavorite, name='addFavorite'),
     path('update_category/', views.update_category, name='update_category'),
]

