```
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

```

# FolderItem

```
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
    document_user = models.ForeignKey(
        DocumentUser,
        on_delete=models.CASCADE,
        related_name='folder_items',
        verbose_name='用户文献记录'
    )

    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='添加时间'
    )

    class Meta:
        verbose_name = "收藏夹条目"
        verbose_name_plural = verbose_name
        unique_together = ('folder', 'document_user')  # 避免重复加入

    def __str__(self):
        return f"{self.folder.name} - {self.document_user.document.title}"

```

