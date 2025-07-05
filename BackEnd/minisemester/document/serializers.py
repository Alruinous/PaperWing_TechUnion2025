from rest_framework import serializers
from users.models import User
from .models import Document

class DocumentUploadSerializer(serializers.Serializer):
    """
    用于验证文献上传请求参数的序列化器。
    """
    userId = serializers.IntegerField()
    title = serializers.CharField(max_length=500, trim_whitespace=True)
    authors = serializers.CharField(trim_whitespace=True)
    localFilePath = serializers.CharField(source='local_file_path', max_length=500)
    
    # 可选字段
    journal = serializers.CharField(max_length=200, required=False, allow_blank=True, allow_null=True)
    year = serializers.IntegerField(required=False, allow_null=True)
    abstract = serializers.CharField(required=False, allow_blank=True, allow_null=True, style={'base_template': 'textarea.html'})
    keywords = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    research_fields = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    def validate_userId(self, value):
        """验证上传用户是否存在。"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的用户不存在。")
        return value

    def validate_title(self, value):
        """确保标题不为空。"""
        if not value:
            raise serializers.ValidationError("文献标题不能为空。")
        return value

    def validate_authors(self, value):
        """确保作者不为空。"""
        if not value:
            raise serializers.ValidationError("作者列表不能为空。")
        return value
    
class DocumentDuplicateCheckSerializer(serializers.Serializer):
    """
    用于验证文献查重请求参数的序列化器。
    """
    title = serializers.CharField(max_length=500, required=True, allow_blank=False, trim_whitespace=True)


class AISummarySerializer(serializers.Serializer):
    summary = serializers.CharField()


class DocumentReadingHistoryCreateSerializer(serializers.Serializer):
    """
    用于验证创建文献阅读历史请求的序列化器。
    """
    userId = serializers.IntegerField()
    documentId = serializers.IntegerField()

    def validate_documentId(self, value):
        """验证文献是否存在。"""
        if not Document.objects.filter(doc_id=value).exists():
            raise serializers.ValidationError("指定的文献不存在。")
        return value

    def validate_userId(self, value):
        """验证用户是否存在。"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的用户不存在。")
        return value


class AnalysisSubscriptionSerializer(serializers.Serializer):
    """
    用于创建或更新技术速递订阅的序列化器。
    """
    userId = serializers.IntegerField()
    keyword = serializers.CharField(max_length=255)
    frequency = serializers.CharField(max_length=50)


class AnalysisReportSerializer(serializers.Serializer):
    """
    用于序列化完整的技术速递报告。
    """
    report = serializers.CharField()
    wordCloudData = serializers.ListField(child=serializers.DictField())
    years = serializers.ListField(child=serializers.CharField())
    topics = serializers.ListField(child=serializers.CharField())
    heatmapData = serializers.ListField(child=serializers.ListField())
    mindMapData = serializers.DictField(required=False)  # 新增思维导图数据字段