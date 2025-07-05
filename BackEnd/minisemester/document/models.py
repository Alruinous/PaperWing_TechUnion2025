from django.db import models
from users.models import User
import re
from django.conf import settings

class Document(models.Model):
    """
    文献库中的单篇文献（构成“大文献库”）。
    """
    # doc_id：主键，自增整数（PK, AUTO_INCREMENT）
    doc_id = models.AutoField(primary_key=True)

    # title：文献标题（VARCHAR(500)，非空）
    title = models.CharField(max_length=500, verbose_name="文献标题")

    # authors：作者列表（TEXT，非空）
    authors = models.TextField(help_text="作者列表，用逗号分隔", verbose_name="作者列表")

    # journal：期刊/会议名称（VARCHAR(200)，可选）
    journal = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="期刊/会议")

    # year：发表年份（SMALLINT，可选）
    year = models.SmallIntegerField(blank=True, null=True, verbose_name="发表年份")

    # abstract：摘要内容（TEXT，可选）
    abstract = models.TextField(blank=True, null=True, verbose_name="摘要")

    # keywords：关键词列表（TEXT，可选）
    keywords = models.TextField(
        blank=True, null=True, help_text="关键词列表，用逗号分隔", verbose_name="关键词")

    # local_file_path：本地上传文件路径（VARCHAR(500)，可选）
    local_file_path = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="本地文件路径")

    # source：文献来源
    source = models.CharField(
        max_length=50, default='user_upload', verbose_name="文献来源")

    # uploaded_by：上传者用户ID（INT，FK → User.id），对于系统爬取的文献，此项可以为空
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True,
                                    null=True, related_name='uploaded_documents', verbose_name="上传者")

    # created_at：入库时间（DATETIME，自动添加当前时间）
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="入库时间", db_index=True)
    
    research_fields = models.TextField(blank=True, null=True, verbose_name="研究领域")

    arxiv_url = models.URLField(blank=True, null=True)
    pdf_url = models.URLField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    @property   
    def research_fields_list(self) -> list[str]:
        """
        将研究领域字段按逗号拆分为列表
        """
        if not self.research_fields:
            return []
        return [field.strip() for field in re.split(r'[，,]', self.research_fields) if field.strip()]
    
    @property
    def keywords_list(self) -> list[str]:
        """
        将关键词字段按逗号拆分为列表
        """
        if not self.keywords:
            return []
        return [kw.strip() for kw in re.split(r'[，,]', self.keywords) if kw.strip()]
    
    @property
    def authors_list(self) -> list[str]:
        if not self.authors:
            return []
        return [author.strip() for author in re.split(r'[，,]', self.authors) if author.strip()]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "文献"
        verbose_name_plural = verbose_name


class DocumentUser(models.Model):
    """
    用户个人文献库的关联表。
    记录了哪个用户收藏了“大文献库”中的哪篇文献。
    """
    # --- 新增：定义文献来源类型 ---
    class SourceType(models.TextChoices):
        SELF_UPLOADED = 'self_uploaded', '自己上传'
        FROM_FOLLOWED = 'from_followed', '关注者上传'
        SYSTEM_RECOMMEND = 'system_recommend', '系统推荐'

    id = models.AutoField(primary_key=True)

    # user：用户ID（INT，FK → User.id）
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='library_items')

    # document：文献ID（INT，FK → Document.doc_id）
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name='collected_by_users')

    # --- 新增：用于快速区分来源的类型字段 ---
    source_type = models.CharField(
        max_length=20,
        choices=SourceType.choices,
        verbose_name="文献来源类型"
    )

    # added_at：添加时间（DATETIME，自动添加当前时间）
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        # 确保一个用户不能重复添加同一篇文献到自己的库中
        unique_together = ('user', 'document')
        verbose_name = "用户文献库条目"
        verbose_name_plural = verbose_name
        ordering = ['-added_at']


class AnalysisSubscription(models.Model):
    """
    技术速递订阅模型
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analysis_subscriptions'
    )
    keyword = models.CharField(max_length=255, help_text="用户订阅的领域关键词")
    frequency = models.CharField(
        max_length=50, help_text="分析频率，如 'weekly', 'monthly'")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    next_run_at = models.DateTimeField(
        null=True, blank=True, help_text="下一次报告生成的时间"
    )
    class Meta:
        # 确保每个用户对同一个关键词只有一个订阅
        unique_together = ('user', 'keyword')

    def __str__(self):
        return f"{self.user.username} - {self.keyword} ({self.frequency})"


class AnalysisReport(models.Model):
    """
    技术速递报告模型
    """
    # 使用 OneToOneField 确保每个订阅只对应一份最新的报告
    subscription = models.OneToOneField(
        AnalysisSubscription,
        on_delete=models.CASCADE,
        related_name='report'
    )
    # JSONField 非常适合存储前端需要的复杂结构化数据
    report_data = models.JSONField(help_text="AI生成的完整报告数据")
    generated_at = models.DateTimeField(auto_now_add=True, help_text="报告生成时间")

    def __str__(self):
        return f"Report for {self.subscription.keyword} at {self.generated_at.strftime('%Y-%m-%d')}"
    
class DocumentReadingHistory(models.Model):
    """
    用户文献阅读记录
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='document_reading_history')
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name='read_by_users')
    read_time = models.DateTimeField(auto_now_add=True, verbose_name="阅读时间")

    class Meta:
        verbose_name = "文献阅读记录"
        verbose_name_plural = verbose_name
        ordering = ['-read_time']

class CollectionFolder(models.Model):
    """
    用户自定义的文献收藏夹。
    文献首次收藏或上传时默认加入“默认收藏夹”。
    """
    id = models.AutoField(primary_key=True)

    # 收藏夹所属用户
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='collection_folders',
        verbose_name='用户'
    )

    # 收藏夹名称（每个用户下唯一）
    name = models.CharField(
        max_length=100,
        verbose_name='收藏夹名称'
    )

    # 是否为默认收藏夹
    is_default = models.BooleanField(
        default=False,
        verbose_name='是否为默认收藏夹'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        verbose_name = "收藏夹"
        verbose_name_plural = verbose_name
        unique_together = ('user', 'name')  # 用户下收藏夹名称唯一

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class FolderItem(models.Model):
    """
    收藏夹中的文献条目，连接 收藏夹 与 DocumentUser 记录。
    一个文献可以同时存在于多个收藏夹中。
    """
    id = models.AutoField(primary_key=True)

    # 所属收藏夹
    folder = models.ForeignKey(
        CollectionFolder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='所属收藏夹'
    )

    # 指向用户收藏文献的记录（唯一地表示某用户收藏的某篇文献）
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='folder_items',
        verbose_name='用户文献记录'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='folder_items',
        verbose_name='收藏者'
    )

    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='添加时间'
    )

    class Meta:
        verbose_name = "收藏夹条目"
        verbose_name_plural = verbose_name
        unique_together = ('user', 'folder', 'document')

    def __str__(self):
        return f"{self.folder.name} - {self.document.title}"
