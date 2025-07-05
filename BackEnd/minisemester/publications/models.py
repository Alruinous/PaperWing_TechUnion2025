from django.db import models
from users.models import User
import re


class Publication(models.Model):
    """
    科研成果
    """
    pub_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500, verbose_name="成果标题")
    type = models.CharField(max_length=50, blank=True,
                            null=True, verbose_name="成果类型")
    authors = models.TextField(help_text="作者列表，用逗号分隔", verbose_name="作者列表")
    journal = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="期刊/会议")
    volume = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="卷号")
    issue = models.CharField(max_length=50, blank=True,
                             null=True, verbose_name="期号")
    year = models.SmallIntegerField(blank=True, null=True, verbose_name="发表年份")
    abstract = models.TextField(blank=True, null=True, verbose_name="摘要")
    keywords = models.TextField(
        blank=True, null=True, help_text="关键词列表，用逗号分隔", verbose_name="关键词")
    external_url = models.URLField(
        max_length=255, blank=True, null=True, verbose_name="外部链接")
    local_file_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="本地文件路径")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='uploaded_publications', verbose_name="上传者")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="上传时间", db_index=True)
    
    research_fields = models.TextField(blank=True, null=True, verbose_name="研究领域")

    @property   
    def research_fields_list(self) -> list[str]:
        """
        将研究领域字段按逗号拆分为列表
        """
        if not self.research_fields:
            return []
        return [field.strip() for field in re.split(r'[，,]', self.research_fields) if field.strip()]

    @property
    def authors_list(self) -> list[str]:
        if not self.authors:
            return []
        # 去掉空白，按逗号拆分
        return [author.strip() for author in re.split(r'[，,]', self.authors) if author.strip()]

    def __str__(self):
        return self.title


class PublicationUser(models.Model):
    """
    成果与用户的关联（例如：收藏、标记为作者等）
    """
    # --- 修改点：指定数据库列名为 pub_id ---
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, db_column='pub_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('publication', 'user')
        verbose_name = "成果用户关联"
        verbose_name_plural = verbose_name


class PublicationKeyword(models.Model):
    """
    成果的关键词（更规范化的设计）
    """
    # --- 修改点：指定数据库列名为 pub_id ---
    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name='structured_keywords', db_column='pub_id')
    keyword = models.CharField(max_length=100)

    class Meta:
        unique_together = ('publication', 'keyword')
        verbose_name = "成果关键词"
        verbose_name_plural = verbose_name


class PublicationLike(models.Model):
    """
    成果点赞记录
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='liked_publications')
    # --- 修改点：指定数据库列名为 pub_id ---
    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name='likes', db_column='pub_id')
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'publication')
        verbose_name = "成果点赞"
        verbose_name_plural = verbose_name


class PublicationComment(models.Model):
    """
    成果评论
    """
    comment_id = models.AutoField(primary_key=True)
    # --- 修改点：指定数据库列名为 pub_id ---
    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name='comments', db_column='pub_id')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(verbose_name="评论内容")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.publication}"


class ReadingHistory(models.Model):
    """
    用户阅读记录
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reading_history')
    # --- 修改点：指定数据库列名为 pub_id ---
    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name='read_by_users', db_column='pub_id')
    read_time = models.DateTimeField(auto_now_add=True, verbose_name="阅读时间")

    class Meta:
        verbose_name = "阅读记录"
        verbose_name_plural = verbose_name
        ordering = ['-read_time']