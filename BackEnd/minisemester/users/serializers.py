from rest_framework import serializers
from .models import User
from publications.models import Publication
from document.models import Document

class UserRegisterSerializer(serializers.Serializer):
    """
    用户注册数据序列化器和验证器。
    """
    #account = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, error_messages={'min_length': '密码长度不能少于8位。'})
    name = serializers.CharField(max_length=100)
    institution = serializers.CharField(max_length=255, allow_blank=True)
    # department = serializers.CharField(max_length=255)
    research_fields = serializers.CharField(allow_blank=True)
    
    # region 字段在模型中不存在，仅作接收，不参与业务逻辑
    #region = serializers.CharField(required=False, write_only=True)
 
    #def validate_account(self, value):
    #    """
    #    检查账号是否已存在。
     #   """
     #   if User.objects.filter(username=value).exists():
     #       raise serializers.ValidationError("该账号已被注册。")
     #   return value

    def validate_email(self, value):
        """
        检查邮箱是否已存在。
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册。")
        return value.lower()


class CheckEmailSerializer(serializers.Serializer):
    """
    校验邮箱重复性序列化器。
    """
    email = serializers.EmailField()


class UserLoginSerializer(serializers.Serializer):
    """
    用户登录数据序列化器和验证器。
    """
    account = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用于登录成功后返回用户基本信息的序列化器。
    """
    user_id = serializers.IntegerField(source='id')
    account = serializers.CharField(source='username')

    class Meta:
        model = User
        # 只序列化这三个字段
        fields = ['user_id', 'account', 'email', 'name', 'avatar_url']
    def to_representation(self, instance):
        """处理 avatar_url 可能为 None 的情况"""
        ret = super().to_representation(instance)
        # 如果头像链接在数据库中为 null，则返回空字符串，方便前端处理
        if ret.get('avatar_url') is None:
            ret['avatar_url'] = ""
        return ret


class CheckAccountEmailSerializer(serializers.Serializer):
    """
    校验账号或邮箱重复性序列化器。
    """
    account = serializers.CharField(max_length=100)
    email = serializers.EmailField()

class UserInfoRequestSerializer(serializers.Serializer):
    """
    查询用户信息请求的验证器。
    """
    userId = serializers.IntegerField()


class UserFullDetailSerializer(serializers.ModelSerializer):
    """
    用于返回用户完整详细信息的序列化器。
    """
    user_id = serializers.IntegerField(source='id')
    account = serializers.CharField(source='username')
    status = serializers.SerializerMethodField()
    register_time = serializers.DateTimeField(source='date_joined', format="%Y-%m-%dT%H:%M:%S%z")

    class Meta:
        model = User
        fields = [
            'user_id', 'account', 'email', 'name', 'title',
            'education', 'institution', 'avatar_url', 'bio',
            'research_fields', 'status', 'register_time'
        ]

    def get_status(self, obj):
        """根据 is_active 字段返回 'active' 或 'inactive'。"""
        return "active" if obj.is_active else "inactive"

    def to_representation(self, instance):
        """
        重写此方法，将所有值为 None 的字符串相关字段转换为空字符串。
        """
        ret = super().to_representation(instance)
        # 字段列表
        string_fields = ['title', 'education', 'institution', 'avatar_url', 'bio', 'research_fields']
        for field in string_fields:
            if ret.get(field) is None:
                ret[field] = ""
        return ret
    
class UserUpdateSerializer(serializers.Serializer):
    """
    更新用户信息请求的验证器 (使用传入的 userId)。
    """
    userId = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=100, allow_blank=True)
    education = serializers.CharField(max_length=100, allow_blank=True)
    institution = serializers.CharField(max_length=255, allow_blank=True)
    avatar_url = serializers.CharField(max_length=255, allow_blank=True)
    bio = serializers.CharField(allow_blank=True)
    research_fields = serializers.CharField(allow_blank=True)

    def validate_userId(self, value):
        """检查用户是否存在。"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的用户ID不存在。")
        return value
    

class AuthorOwnershipCheckSerializer(serializers.Serializer):
    """
    用于验证作者归属检查请求的序列化器。
    """
    userId = serializers.IntegerField()
    authors = serializers.CharField(allow_blank=False, trim_whitespace=True)

    def validate_userId(self, value):
        """验证用户是否存在。"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的用户不存在。")
        return value

class FollowListSerializer(serializers.ModelSerializer):
    """
    用于序列化关注者/正在关注列表的用户信息。
    """
    userId = serializers.IntegerField(source='id')

    class Meta:
        model = User
        fields = ['userId', 'name', 'title', 'institution', 'avatar_url']

    def to_representation(self, instance):
        """
        重写此方法，确保所有 None 值的字段都返回空字符串，以保证前端兼容性。
        """
        ret = super().to_representation(instance)
        for field in self.Meta.fields:
            # userId 是整数，不处理
            if field == 'userId':
                continue
            if ret.get(field) is None:
                ret[field] = ""
        return ret


# --- 新增：为 Publication 模型创建一个全字段的序列化器 ---
class _HistoryPublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = '__all__' # 包含所有字段

# --- 新增：为 Document 模型创建一个全字段的序列化器 ---
class _HistoryDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__' # 包含所有字段

# --- 修改：这是主序列化器，现在它将动态地选择使用哪个子序列化器 ---
class CombinedReadingHistorySerializer(serializers.Serializer):
    """
    用于序列化合并后的单条阅读历史记录 (全字段版)。
    """
    type = serializers.CharField(source='history_type')
    read_time = serializers.DateTimeField()
    item = serializers.SerializerMethodField()

    def get_item(self, obj):
        """
        根据历史记录的类型，动态选择并返回序列化后的 item 数据。
        """
        if obj.history_type == 'publication':
            # obj 是一个 PublicationReadingHistory 实例
            serializer = _HistoryPublicationSerializer(obj.publication)
            return serializer.data
        elif obj.history_type == 'document':
            # obj 是一个 DocumentReadingHistory 实例
            serializer = _HistoryDocumentSerializer(obj.document)
            return serializer.data
        return None