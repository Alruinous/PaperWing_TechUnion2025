from rest_framework import serializers
from .models import Conversation, Message, ConversationParticipant
from users.models import User
import re # 导入 re 模块


class ConversationCreateSerializer(serializers.Serializer):
    """
    用于创建讨论单元的序列化器 (DTO)。
    它只定义了需要从前端接收的字段。
    """
    title = serializers.CharField(max_length=255, required=True, error_messages={
        'required': '讨论主题(title)是必填项。',
        'blank': '讨论主题(title)不能为空。'
    })
    type = serializers.ChoiceField(choices=Conversation.TYPE_CHOICES, required=True, error_messages={
        'required': '讨论类型(type)是必填项。',
        'invalid_choice': '无效的讨论类型，有效值为 "forum" 或 "project"。'
    })

class SendMessageSerializer(serializers.Serializer):
    senderId = serializers.IntegerField()
    receiverId = serializers.IntegerField()
    type = serializers.ChoiceField(choices=['user', 'invitation', 'ask', 'system', 'claim', 'apply', 'group', 'forum'])
    content = serializers.CharField(max_length=2000)
    projectId = serializers.IntegerField()
    # 新增：接收可选的 resultId
    resultId = serializers.IntegerField(required=False, allow_null=True)
    # timestamp 字段仅用于接收，不参与业务逻辑，设为非必需
    timestamp = serializers.CharField(required=False)

    def validate_senderId(self, value):
        # 系统消息允许 senderId=0
        if value == 0:
            return value
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("发送者用户不存在。")
        return value

    def validate_receiverId(self, value):
        # 群发消息允许 receiverId=0
        if value == 0:
            return value
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("接收者用户不存在。")
        return value

    def validate(self, data):
        """
        复合验证 (重构后):
        1. 根据消息类型，验证 projectId 或 resultId 的存在性和有效性。
        2. 用户不能给自己发普通消息。
        """
        msg_type = data.get('type')
        project_id = data.get('projectId')
        result_id = data.get('resultId')

        # 规则1：项目相关消息必须有关联的 projectId
        if msg_type in ['invitation', 'apply', 'group']:
            if not project_id or project_id == 0:
                raise serializers.ValidationError({"projectId": "该类型消息必须关联一个有效的项目ID。"})
            if not Conversation.objects.filter(conversation_id=project_id, type='project').exists():
                raise serializers.ValidationError({"projectId": "关联的项目不存在或不是一个有效的项目。"})

        # 规则2：成果相关消息必须有关联的 resultId
        elif msg_type in ['ask', 'claim']:
            if not result_id or result_id == 0:
                raise serializers.ValidationError({"resultId": "该类型消息必须关联一个有效的成果ID。"})
            # 注意：这里我们不验证 resultId 的存在性，因为成果可能在另一个服务或表中。
            # 如果需要验证，可以在这里添加对成果模型的查询。

        # 规则3：普通用户消息不能发给自己
        if msg_type == 'user' and data.get('senderId') == data.get('receiverId'):
            raise serializers.ValidationError("不能给自己发送消息。")
        return data
    
class GetMessagesRequestSerializer(serializers.Serializer):
    """
    获取消息列表请求的验证器。
    """
    box = serializers.ChoiceField(choices=['inbox', 'sent'])
    userId = serializers.IntegerField()


class MessageListSerializer(serializers.ModelSerializer):
    """
    用于格式化消息列表响应的序列化器。
    """
    messageId = serializers.IntegerField(source='message_id')
    type = serializers.CharField(source='message_type')
    # --- 关键修改：全部改为 SerializerMethodField 以处理 None 的情况 ---
    senderId = serializers.SerializerMethodField()
    receiverId = serializers.SerializerMethodField()
    senderAvatar = serializers.SerializerMethodField()
    receiverAvatar = serializers.SerializerMethodField()

     # --- 新增字段 ---
    senderName = serializers.SerializerMethodField()
    senderUsername = serializers.SerializerMethodField()
    receiverName = serializers.SerializerMethodField()
    receiverUsername = serializers.SerializerMethodField()

    projectId = serializers.SerializerMethodField()
    resultId = serializers.SerializerMethodField()
    # --- 修改结束 ---
    timestamp = serializers.DateTimeField(source='sent_at', format="%Y/%m/%d/%H/%M")

    class Meta:
        model = Message
        fields = [
            'messageId', 'type', 'senderId', 'receiverId',
            'senderAvatar', 'receiverAvatar', 'content', 'projectId', 'timestamp', 'resultId',
            'senderName', 'senderUsername', 'receiverName', 'receiverUsername'
        ]

    def get_senderId(self, obj):
        """如果 sender 存在则返回其ID，否则返回 0。"""
        return obj.sender.id if obj.sender else 0

    def get_receiverId(self, obj):
        """如果 receiver 存在则返回其ID，否则返回 0。"""
        return obj.receiver.id if obj.receiver else 0

    def get_senderAvatar(self, obj):
        """如果 sender 及其头像存在则返回URL，否则返回空字符串。"""
        return obj.sender.avatar_url if obj.sender and obj.sender.avatar_url else ""

    def get_receiverAvatar(self, obj):
        """如果 receiver 及其头像存在则返回URL，否则返回空字符串。"""
        return obj.receiver.avatar_url if obj.receiver and obj.receiver.avatar_url else ""

     # --- 新增方法 ---
    def get_senderName(self, obj):
        """如果 sender 存在则返回其真实姓名，否则返回空字符串。"""
        return obj.sender.name if obj.sender and obj.sender.name else ""

    def get_senderUsername(self, obj):
        """如果 sender 存在则返回其用户名，否则返回空字符串。"""
        return obj.sender.username if obj.sender else ""

    def get_receiverName(self, obj):
        """如果 receiver 存在则返回其真实姓名，否则返回空字符串。"""
        return obj.receiver.name if obj.receiver and obj.receiver.name else ""

    def get_receiverUsername(self, obj):
        """如果 receiver 存在则返回其用户名，否则返回空字符串。"""
        return obj.receiver.username if obj.receiver else ""
    # --- 新增结束 ---


    def get_projectId(self, obj):
        """如果关联的 conversation 存在则返回其ID，否则返回 0。"""
        return obj.conversation.conversation_id if obj.conversation else 0
        
    def get_resultId(self, obj):
        """如果 result_id 存在则返回其值，否则返回 0。"""
        return obj.result_id or 0



# --- 用下面的版本替换掉旧的 ProjectListSerializer ---
class ProjectListSerializer(serializers.ModelSerializer):
    """
    用于格式化用户创建的项目列表的序列化器 (详细版)。
    """
    projectId = serializers.IntegerField(source='conversation_id')
    initiatorId = serializers.IntegerField(source='initiator_id', allow_null=True)
    researchFields = serializers.CharField(source='research_fields')
    # 新增：格式化创建时间
    createdAt = serializers.DateTimeField(source='created_at', format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Conversation
        # 新增：在字段列表中加入 abstract 和 createdAt
        fields = ['projectId', 'title', 'initiatorId', 'researchFields', 'abstract', 'createdAt']

    def to_representation(self, instance):
        """将值为 None 的字段转换为空字符串，方便前端处理。"""
        ret = super().to_representation(instance)
        string_fields = ['title', 'researchFields', 'abstract']
        for field in string_fields:
            if ret.get(field) is None:
                ret[field] = ""
        # 确保 initiatorId 为空时返回 null 或 0
        if ret.get('initiatorId') is None:
            ret['initiatorId'] = 0
        return ret
    
class ParticipantStatusRequestSerializer(serializers.Serializer):
    """
    获取用户参与状态请求的验证器。
    """
    userId = serializers.IntegerField()
    projectId = serializers.IntegerField()

    def validate_userId(self, value):
        """检查用户是否存在。"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的用户不存在。")
        return value

    def validate_projectId(self, value):
        """检查项目是否存在且类型正确。"""
        if not Conversation.objects.filter(conversation_id=value, type='project').exists():
            raise serializers.ValidationError("指定的项目不存在。")
        return value

# --- 新增：用于序列化项目成员信息的序列化器 ---
class ProjectMemberSerializer(serializers.ModelSerializer):
    """序列化项目成员信息"""
    userId = serializers.IntegerField(source='user.id')
    userName = serializers.CharField(source='user.name', default="")
    avatar = serializers.CharField(source='user.avatar_url', default="")
    # status 字段直接从 ConversationParticipant 模型获取

    class Meta:
        model = ConversationParticipant
        fields = ['userId', 'userName', 'avatar']

    def to_representation(self, instance):
        """确保 avatar 为空时返回空字符串"""
        ret = super().to_representation(instance)
        if not ret.get('avatar'):
            ret['avatar'] = ""
        return ret

class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    用于序列化项目详情，以匹配前端数据结构。
    """
    # 从关联的 initiator (User) 对象中获取信息
    avatar = serializers.CharField(source='initiator.avatar_url', read_only=True, default="")
    userId = serializers.IntegerField(source='initiator.id', read_only=True)
    userName = serializers.CharField(source='initiator.name', read_only=True)
    institution = serializers.CharField(source='initiator.institution', read_only=True, default="")
    
    # 使用 SerializerMethodField 处理需要自定义逻辑的字段
    tags = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
# --- 新增：项目成员列表字段 ---
    members = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        # 包含模型本身的字段和我们自定义的字段
        fields = [
            'avatar', 'userId', 'userName', 'institution', 
            'title', 'abstract', 'tags', 'year', 'members'
        ]

    def get_tags(self, obj):
        """将 research_fields 字符串按中英文逗号分割成数组。"""
        if not obj.research_fields:
            return []
        # 使用正则表达式分割，以兼容中英文逗号
        return [tag.strip() for tag in re.split(r'[，,]', obj.research_fields) if tag.strip()]

    def get_year(self, obj):
        """从 created_at 字段中提取年份并转为字符串。"""
        if obj.created_at:
            return str(obj.created_at.year)
        return ""
    def get_members(self, obj):
        """获取项目中状态为 'admin' 或 'approved' 的成员列表。"""
        # obj 是 Conversation 实例
        # 使用 select_related('user') 优化查询，一次性获取参与者及其关联的用户信息
        participants = obj.participants.filter(status__in=['approved']).select_related('user')
        return ProjectMemberSerializer(participants, many=True).data
    
class RespondInvitationSerializer(serializers.Serializer):
    """
    用于验证回复邀请请求参数的序列化器。
    """
    userId = serializers.IntegerField()
    projectId = serializers.IntegerField()
    respond = serializers.ChoiceField(choices=['accept', 'decline'])

    def validate_userId(self, value):
        """验证用户是否存在。"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("指定的用户不存在。")
        return value

    def validate_projectId(self, value):
        """验证项目是否存在。"""
        if not Conversation.objects.filter(conversation_id=value, type='project').exists():
            raise serializers.ValidationError("指定的项目不存在。")
        return value
    
class JoinedProjectRequestSerializer(serializers.Serializer):
    userId = serializers.IntegerField()

class JoinedProjectListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='conversation_id')
    initiatorId = serializers.IntegerField(source='initiator_id')

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'type', 'initiatorId']

class ProjectReplySerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    projId = serializers.IntegerField()
    reply = serializers.CharField(max_length=2000)

    def validate_userId(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("用户不存在。")
        return value

    def validate_projId(self, value):
        if not Conversation.objects.filter(conversation_id=value, type='project').exists():
            raise serializers.ValidationError("项目不存在。")
        return value
    
class ProjectReplyListSerializer(serializers.ModelSerializer):
    avatar = serializers.CharField(source='sender.avatar_url', default="")
    userId = serializers.IntegerField(source='sender.id')
    userName = serializers.CharField(source='sender.name', default="")
    institution = serializers.CharField(source='sender.institution', default="")
    year = serializers.SerializerMethodField()
    content = serializers.CharField()

    class Meta:
        model = Message
        fields = ['avatar', 'userId', 'userName', 'institution', 'year', 'content']

    def get_year(self, obj):
        if obj.sent_at:
            return obj.sent_at.strftime("%Y-%m-%d %H:%M:%S")
        return ""
    
class DeleteMemberSerializer(serializers.Serializer):
    """用于验证删除项目成员请求的序列化器"""
    userId = serializers.IntegerField(required=True)
    projId = serializers.IntegerField(required=True)

    def validate_userId(self, value):
        """验证用户是否存在"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("要删除的用户不存在。")
        return value

    def validate_projId(self, value):
        """验证项目是否存在"""
        if not Conversation.objects.filter(conversation_id=value, type='project').exists():
            raise serializers.ValidationError("指定的项目不存在。")
        return value