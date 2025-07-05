from rest_framework import serializers
from .models import (
    Publication, 
    PublicationUser,
    PublicationKeyword,
    PublicationLike,
    PublicationComment,
    ReadingHistory
)

from users.models import User

class PublicationCreateSerializer(serializers.Serializer):
    """
    用于创建科研成果的序列化器。
    接收前端所有必要字段，包括 created_by。
    """
    title = serializers.CharField(max_length=500, required=True, error_messages={
        'required': '成果标题(title)是必填项。',
        'blank': '成果标题(title)不能为空。'
    })
    type = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)
    authors = serializers.CharField(required=True, error_messages={
        'required': '作者列表(authors)是必填项。',
        'blank': '作者列表(authors)不能为空。'
    })
    journal = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    volume = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)
    issue = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)
    year = serializers.IntegerField(required=False, allow_null=True)
    abstract = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    keywords = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    external_url = serializers.URLField(max_length=255, required=False, allow_null=True, allow_blank=True)
    local_file_path = serializers.CharField(max_length=500, required=False, allow_null=True, allow_blank=True)
    research_fields = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # ✅ 新增：接收 created_by（用户 id），并验证用户是否存在
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        error_messages={
            'required': '创建者(created_by)是必填项。',
            'does_not_exist': '指定的用户不存在。',
            'incorrect_type': 'created_by 类型应为用户ID（整数）。'
        }
    )


class PublicationUserSerializer(serializers.Serializer):
    """
    成果与用户关联的序列化器
    """
    publication_id = serializers.IntegerField(required=True, error_messages={
        'required': '成果ID(publication_id)是必填项。',
        'invalid': '无效的成果ID。'
    })
    user_id = serializers.IntegerField(required=True, error_messages={
        'required': '用户ID(user_id)是必填项。',
        'invalid': '无效的用户ID。'
    })


class PublicationKeywordSerializer(serializers.Serializer):
    """
    成果关键词的序列化器
    """
    publication_id = serializers.IntegerField(required=True, error_messages={
        'required': '成果ID(publication_id)是必填项。',
        'invalid': '无效的成果ID。'
    })
    keyword = serializers.CharField(max_length=100, required=True, error_messages={
        'required': '关键词(keyword)是必填项。',
        'blank': '关键词(keyword)不能为空。',
        'max_length': '关键词长度不能超过100个字符。'
    })


class PublicationLikeSerializer(serializers.Serializer):
    """
    成果点赞的序列化器
    """
    pub_id = serializers.IntegerField(required=True, error_messages={
        'required': '成果ID(publication_id)是必填项。',
        'invalid': '无效的成果ID。'
    })
    user_id = serializers.IntegerField(required=True, error_messages={
        'required': '用户ID(user_id)是必填项。',
        'invalid': '无效的用户ID。'
    })


class PublicationCommentCreateSerializer(serializers.Serializer):
    """
    创建成果评论的序列化器
    """
    pub_id = serializers.IntegerField(required=True, error_messages={
        'required': '成果ID(pub_id)是必填项。',
        'invalid': '无效的成果ID。'
    })
    comment = serializers.CharField(required=True, error_messages={
        'required': '评论内容(content)是必填项。',
        'blank': '评论内容(content)不能为空。'
    })
    user_id = serializers.IntegerField(required=True, error_messages={
        'required': '用户ID(user_id)是必填项。',
        'invalid': '无效的用户ID。'
    })

class ReadingHistorySerializer(serializers.Serializer):
    """
    阅读记录的序列化器
    """
    pub_id = serializers.IntegerField(required=True, error_messages={
        'required': '成果ID(pub_id)是必填项。',
        'invalid': '无效的成果ID。'
    })
    user_id = serializers.IntegerField(required=True, error_messages={
        'required': '用户ID(user_id)是必填项。',
        'invalid': '无效的用户ID。'
    })


class AuthorDetailSerializer(serializers.Serializer):
    """用于成果详情中作者列表的序列化器"""
    name = serializers.CharField()
    user_id = serializers.IntegerField(allow_null=True)
    avatar = serializers.CharField(allow_blank=True, required=False)


# class PublicationDetailSerializer(serializers.Serializer):
#     """科研成果详情序列化器"""
#     title = serializers.CharField()
#     type = serializers.CharField(allow_null=True)
#     authors = serializers.CharField(allow_null=True)
#     journal = serializers.CharField(allow_null=True)
#     volume = serializers.CharField(allow_null=True)
#     issue = serializers.CharField(allow_null=True)
#     year = serializers.CharField(allow_null=True)
#     abstract = serializers.CharField(allow_null=True)
#     keywords = serializers.CharField(allow_null=True)
#     created_by = serializers.IntegerField()
#     isFavour = serializers.BooleanField()

class PublicationDetailSerializer(serializers.Serializer):
    """科研成果详情序列化器（修正版）"""
    title = serializers.CharField()
    type = serializers.CharField(allow_null=True, allow_blank=True)

    # --- 修正 1: 使用嵌套序列化器处理作者列表 ---
    authors = AuthorDetailSerializer(many=True)

    journal = serializers.CharField(allow_null=True, allow_blank=True)
    volume = serializers.CharField(allow_null=True, allow_blank=True)
    issue = serializers.CharField(allow_null=True, allow_blank=True)
    year = serializers.CharField(allow_null=True, allow_blank=True)
    abstract = serializers.CharField(allow_null=True, allow_blank=True)
    keywords = serializers.CharField(allow_null=True, allow_blank=True)
    created_by = serializers.IntegerField()
    isFavour = serializers.BooleanField()
    external_url = serializers.CharField(allow_blank=True, required=False)
    # --- 修正 2: 补上缺失的字段 ---
    likes = serializers.IntegerField()
    download = serializers.CharField(allow_blank=True, required=False) # --- 新增：下载链接字段 ---
    research_fields = serializers.ListField(
        child=serializers.CharField(), allow_empty=True
    )

class CommentSerializer(serializers.Serializer):
    content=serializers.CharField()
    user_account=serializers.CharField(source='user.name', read_only=True)
    user_avatar=serializers.CharField(source='user.avatar_url', read_only=True)
    user_id=serializers.CharField(source='user.id', read_only=True)

    class Meta:
        model=PublicationComment
        fields=['content', 'user_account', 'user_avatar', 'user_id']


class PublicationDuplicateCheckSerializer(serializers.Serializer):
    """
    用于验证文献重复性检查请求参数的序列化器。
    """
    title = serializers.CharField(required=True, allow_blank=False, error_messages={
        'required': '标题 (title) 是必填项。',
        'blank': '标题 (title) 不能为空。'
    })
    created_by = serializers.IntegerField(required=True, error_messages={
        'required': '用户ID (created_by) 是必填项。'
    })

    def validate_created_by(self, value):
        """验证用户是否存在。"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的用户 (created_by) 不存在。")
        return value
    
class UserPublicationRequestSerializer(serializers.Serializer):
    userId = serializers.IntegerField()

class PublicationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = [
            "pub_id", "title", "type", "authors", "journal", "volume", "issue",
            "year", "abstract", "keywords", "external_url", "local_file_path", "created_by"
        ]

class RespondClaimSerializer(serializers.Serializer):
    publicationId = serializers.IntegerField()
    claimerId = serializers.IntegerField()
    approverId = serializers.IntegerField()
    messageId = serializers.IntegerField()
    response = serializers.ChoiceField(choices=['accept', 'decline'])

class ClaimOwnershipCheckSerializer(serializers.Serializer):
    """
    用于验证成果认领归属检查请求的序列化器。
    """
    publicationId = serializers.IntegerField()
    userId = serializers.IntegerField()

    def validate_publicationId(self, value):
        """验证成果是否存在。"""
        if not Publication.objects.filter(pub_id=value).exists():
            raise serializers.ValidationError("指定的成果不存在。")
        return value

    def validate_userId(self, value):
        """验证用户是否存在。"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的用户不存在。")
        return value
    

class PublicationNotificationSerializer(serializers.Serializer):
    """
    用于验证新成果邮件通知请求的序列化器。
    """
    userId = serializers.IntegerField()
    type = serializers.ChoiceField(choices=[0, 1]) # 0:单个, 1:批量
    number = serializers.IntegerField(min_value=1)

    def validate_userId(self, value):
        """验证发布者用户是否存在。"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的发布者用户不存在。")
        return value
    
class ReadingHistoryCreateSerializer(serializers.Serializer):
    """
    用于验证创建阅读历史请求的序列化器。
    """
    userId = serializers.IntegerField()
    publicationId = serializers.IntegerField()

    def validate_publicationId(self, value):
        """验证成果是否存在。"""
        if not Publication.objects.filter(pub_id=value).exists():
            raise serializers.ValidationError("指定的成果不存在。")
        return value

    def validate_userId(self, value):
        """验证用户是否存在。"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的用户不存在。")
        return value
    

class SearchQuerySerializer(serializers.Serializer):
    """
    用于验证搜索接口查询参数的序列化器。
    """
    user_id = serializers.IntegerField(required=False)
    condition = serializers.CharField(required=False, allow_blank=True)
    type = serializers.CharField(required=False, allow_blank=True)


class PublicationSearchResultSerializer(serializers.Serializer):
    """
    用于序列化单条搜索结果的序列化器。
    """
    pub_id = serializers.IntegerField()
    title = serializers.CharField()
    journal = serializers.CharField(allow_null=True)
    authors = AuthorDetailSerializer(many=True)
    year = serializers.CharField(allow_null=True)
    abstract = serializers.CharField(allow_null=True)
    keywords = serializers.ListField(child=serializers.CharField())
    external_url = serializers.URLField(allow_null=True)
    local_file_path = serializers.CharField(allow_null=True)
    created_by = serializers.IntegerField()
    favor_count = serializers.IntegerField()
    is_favor = serializers.BooleanField()

# --- 新增序列化器 ---
class PublicationUploadFullTextSerializer(serializers.Serializer):
    """
    用于验证全文链接上传请求的序列化器。
    """
    pub_id = serializers.IntegerField(required=True, error_messages={
        'required': '成果ID (pub_id) 是必填项。'
    })
    url = serializers.CharField(max_length=500, required=True, allow_blank=False, error_messages={
        'required': '文件路径 (url) 是必填项。',
        'blank': '文件路径 (url) 不能为空。'
    })

    def validate_pub_id(self, value):
        """验证成果是否存在。"""
        if not Publication.objects.filter(pub_id=value).exists():
            raise serializers.ValidationError("指定的成果不存在。")
        return value