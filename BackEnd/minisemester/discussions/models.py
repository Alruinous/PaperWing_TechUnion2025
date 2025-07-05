from django.db import models
from users.models import User
import re


class Conversation(models.Model):
    """
    讨论单元，可以是公开论坛或私密项目组
    """
    TYPE_CHOICES = (
        ('forum', '公开论坛'),
        ('project', '项目讨论组'),
    )
    conversation_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, blank=True,
                             null=True, verbose_name="讨论主题")
    initiator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="发起人")
    type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default='forum', verbose_name="讨论类型")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    research_fields = models.TextField(
        blank=True, null=True, verbose_name="研究领域")
    abstract = models.TextField(
        blank=True, null=True, verbose_name="简介")
    

    @property
    def research_fields_list(self) -> list[str]:
        """
        将研究领域字段按逗号拆分为列表
        """
        if not self.research_fields:
            return []
        return [field.strip() for field in re.split(r'[，,]', self.research_fields) if field.strip()]

    def __str__(self):
        return self.title or f"Conversation {self.conversation_id}"


class Message(models.Model):
    """
    消息细则 (修改后，可同时支持群聊和私信)
    """
    # 变化1: 新增消息类型定义
    MESSAGE_TYPE_CHOICES = (
        ('group', '群组消息'),
        ('user', '用户消息'),
        ('invitation', '邀请消息'),
        ('ask', '成果请求'),
        ('system', '系统消息'),
        ('claim', '认领成果'),
        ('apply', '申请加入'),
        ('forum', '论坛信息'),
    )

    message_id = models.AutoField(primary_key=True)
    
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages', 
        verbose_name="所属讨论", null=True, blank=True)
    # --- 新增：专门用于存储成果ID的字段 ---
    result_id = models.IntegerField(null=True, blank=True, verbose_name="关联成果ID")
    sender = models.ForeignKey(
            User, on_delete=models.CASCADE, related_name='sent_messages',
            verbose_name="发送者", null=True, blank=True
        )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_messages', 
        verbose_name="接收者", null=True, blank=True)
        
    content = models.TextField(verbose_name="消息内容")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="发送时间")

    message_type = models.CharField(
        max_length=20, choices=MESSAGE_TYPE_CHOICES, default='group', verbose_name="消息类型")

    def __str__(self):
        # 变化5: 更新 __str__ 方法以适应两种情况
        if self.receiver:
            return f"Direct message from {self.sender} to {self.receiver}"
        return f"Message from {self.sender} in {self.conversation}"



class ConversationParticipant(models.Model):
    """
    项目讨论组的参与者记录
    """
    STATUS_CHOICES = (
        ('pending', '待批准'),
        ('invited', '已邀请'),
        ('approved', '已批准'),
        ('admin', '管理员'),
    )
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='conversations')
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="参与状态")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")

    class Meta:
        unique_together = ('conversation', 'user')
        verbose_name = "讨论参与者"
        verbose_name_plural = verbose_name


class ConversationFollow(models.Model):
    """
    用户关注的讨论
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followed_conversations')
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='followers')
    followed_at = models.DateTimeField(auto_now_add=True, verbose_name="关注时间")

    class Meta:
        unique_together = ('user', 'conversation')
        verbose_name = "讨论关注"
        verbose_name_plural = verbose_name
