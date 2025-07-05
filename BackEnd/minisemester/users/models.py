from django.db import models
from django.contrib.auth.models import AbstractUser
import re

class User(AbstractUser):
    """
    自定义用户模型，继承自 AbstractUser
    """
    # account是AbstractUser中的username字段
    # register_time 是AbstractUser中的date_joined字段
    # email是AbstractUser中的email字段
    name = models.CharField(max_length=100, verbose_name="真实姓名")
    title = models.CharField(max_length=100, blank=True,
                             null=True, verbose_name="职称")
    education = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="学历")
    institution = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="所属单位")
    avatar_url = models.URLField(
        max_length=255, blank=True, null=True, verbose_name="头像链接")
    bio = models.TextField(blank=True,  null=True, verbose_name="个人简介")
    research_fields = models.TextField(
        blank=True, null=True, verbose_name="研究方向")

    @property
    def research_fields_list(self) -> list[str]:
        if not self.research_fields:
            return []
        return [field.strip() for field in re.split(r'[，,]', self.research_fields) if field.strip()]


    def __str__(self):
        return self.username


class UserFollow(models.Model):
    """
    用户关注关系表
    """
    follower = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='following', verbose_name="关注者")
    followee = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='followers', verbose_name="被关注者")
    followed_at = models.DateTimeField(auto_now_add=True, verbose_name="关注时间")

    class Meta:
        unique_together = ('follower', 'followee')
        verbose_name = "用户关注"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.follower} follows {self.followee}"
