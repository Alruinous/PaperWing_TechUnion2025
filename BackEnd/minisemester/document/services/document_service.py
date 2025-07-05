from django.db import transaction
from ..models import Document, DocumentUser, DocumentReadingHistory, CollectionFolder, FolderItem
from users.models import User
from utils.exceptions import BusinessLogicError
from django.db.models import Q  # 1. 导入 Q 对象
from django.utils import timezone
import random
from django.conf import settings

@transaction.atomic
def upload_new_document(**kwargs):
    """
    处理文献上传的核心业务逻辑。
    1. 检查文献是否重复。
    2. 创建 Document 记录。
    3. 创建 DocumentUser 关联记录。
    """
    user_id = kwargs.pop('userId')
    title = kwargs.get('title')
    
    # 1. 查重逻辑：简单检查标题是否完全匹配，以防止明显重复
    if Document.objects.filter(title__iexact=title).exists():
        raise BusinessLogicError("系统中已存在相同标题的文献，请检查是否重复上传。")

    try:
        uploader = User.objects.get(id=user_id)
    except User.DoesNotExist:
        # 此异常理论上会被序列化器捕获，这里是双重保险
        raise BusinessLogicError("上传用户不存在。")

    # 2. 创建 Document 记录
    # 将前端的 localFilePath 字段名映射到模型的 local_file_path
    
    new_document = Document.objects.create(
        uploaded_by=uploader,
        **kwargs
    )

    # 3. 在用户的个人文献库中创建关联记录
    doc_user = DocumentUser.objects.create(
        user=uploader,
        document=new_document,
        source_type=DocumentUser.SourceType.SELF_UPLOADED
    )

    # 上传到默认收藏夹（我上传的）
    default_folder = CollectionFolder.objects.filter(user=uploader,is_default=True).first()
    if not default_folder:
        default_folder = CollectionFolder.objects.create(
            user=uploader,
            name='self-upload',
            is_default=True
        )
    FolderItem.objects.get_or_create(
        folder=default_folder,
        document=new_document,
        user = uploader
    )

    # 上传到‘全部’收藏夹
    all_folder = CollectionFolder.objects.filter(user=uploader, name='all').first()
    if not all_folder:
        all_folder = CollectionFolder.objects.create(
            user=uploader,
            name='all',
            is_default=False
        )
    FolderItem.objects.get_or_create(
        folder=all_folder,
        document=new_document,
        user = uploader
    )

    return new_document


def get_doc_recommended(user: User) -> list:
    """
    返回系统推荐的文献：优先推荐与用户研究领域相关的7篇，不足则补全至10篇，全部不包含自己上传的文献。
    """
    recommend_docs = []
    user_fields = user.research_fields_list

    # 1. 领域相关推荐（不包含自己上传的）
    if user_fields:
        query = Q()
        for field in user_fields:
            query |= Q(research_fields__icontains=field)
        related_docs = list(
            Document.objects.filter(query)
            .exclude(uploaded_by=user)
            .exclude(arxiv_url__isnull=True)
            .exclude(arxiv_url="")
            .order_by('-created_at')[:7]
        )
    else:
        related_docs = []

    recommend_docs.extend([
        {
            "doc_id": doc.doc_id,
            "title": doc.title,
            "authors": doc.authors,
            "year": doc.year,
            "abstract": doc.abstract,
            "conference": doc.journal,
            "local_file_path": doc.arxiv_url,
            "type": 1,
            "isFavorite": FolderItem.objects.filter(user=user, document__doc_id=doc.doc_id).exists()
        }
        for doc in related_docs
    ])

    # 2. 随机补全至10篇（不包含自己上传的和已推荐的，且 arxiv_url 不为空）
    needed = 10 - len(recommend_docs)
    if needed > 0:
        exclude_ids = [doc.doc_id for doc in related_docs]
        id_list = list(
            Document.objects.exclude(uploaded_by=user)
            .exclude(doc_id__in=exclude_ids)
            .exclude(arxiv_url__isnull=True)
            .exclude(arxiv_url="")
            .values_list('doc_id', flat=True)
        )
        sample_ids = random.sample(id_list, min(needed, len(id_list)))
        docs = Document.objects.filter(doc_id__in=sample_ids)
        for doc in docs:
            recommend_docs.append({
                "doc_id": doc.doc_id,
                "title": doc.title,
                "authors": doc.authors,
                "year": doc.year,
                "abstract": doc.abstract,
                "conference": doc.journal,
                "local_file_path": doc.arxiv_url,
                "type": 1,
                "isFavorite": FolderItem.objects.filter(user=user, document__doc_id=doc.doc_id).exists()
            })

    return recommend_docs

def get_doc_followed(user: User) -> list:
    followed_docs = []
    user_followees = User.objects.filter(followers__follower_id=user.id)
    docs_users = DocumentUser.objects.filter(user__in=user_followees).order_by('added_at')[:10]
    for doc_user in docs_users:
        doc = doc_user.document
        followed_docs.append({
            "doc_id": doc.doc_id,
            "title": doc.title,
            "authors": doc.authors,
            "year": doc.year,
            "abstract": doc.abstract,
            "conference": doc.journal,
            "local_file_path": doc.arxiv_url or settings.SERVER_ADDRESS + doc.local_file_path,
            "type": 0,
            "isFavorite": FolderItem.objects.filter(user=user, document__doc_id=doc.doc_id).exists()
        })

    return followed_docs

# def get_doc_mine(user: User) -> list:
#     my_docs = []
#     documents = user.uploaded_documents.all().order_by('-created_at')
#     for doc in documents:
#         my_docs.append({
#             "doc_id": doc.doc_id,
#             "title": doc.title,
#             "authors": doc.authors,
#             "year": doc.year,
#             "abstract": doc.abstract,
#             "conference": doc.journal,
#             "local_file_path": settings.SERVER_ADDRESS + doc.local_file_path,
#         })

#     return my_docs

def getCollection(user_id: int) -> dict:
    """
    获取所有论坛类型的讨论单元，分为推荐、已关注、自己发起。
    """
    user = User.objects.get(id=user_id)
    if not user:
        raise BusinessLogicError("用户不存在")
    data = {
        "系统推荐": get_doc_recommended(user),
        "关注者上传": get_doc_followed(user),
        # "个人上传": get_doc_mine(user)
    }
    return data

@transaction.atomic
def add_document_reading_history(user_id: int, document_id: int):
    """
    添加文献阅读历史，并确保每个用户的历史记录不超过100条。
    """
    try:
        user = User.objects.get(id=user_id)
        document = Document.objects.get(doc_id=document_id)
    except (User.DoesNotExist, Document.DoesNotExist):
        raise BusinessLogicError("用户或文献不存在。")

    # 使用 get_or_create 避免完全相同的记录重复。如果已存在，则更新其 read_time。
    history_entry, created = DocumentReadingHistory.objects.get_or_create(
        user=user,
        document=document,
        defaults={'read_time': timezone.now()}
    )

    if not created:
        history_entry.read_time = timezone.now()
        history_entry.save(update_fields=['read_time'])

    # 检查并维持每个用户最多100条历史记录的限制
    user_history_count = DocumentReadingHistory.objects.filter(user=user).count()
    if user_history_count > 100:
        oldest_entry = DocumentReadingHistory.objects.filter(user=user).order_by('read_time').first()
        if oldest_entry:
            oldest_entry.delete()


def get_favorite_category(user_id: int) -> list:
    """
    获取用户收藏的文献分类。
    返回一个列表，包含用户收藏的所有分类名称。
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise BusinessLogicError("用户不存在。")

    # 获取用户收藏的所有文件夹
    folders = CollectionFolder.objects.filter(user=user).exclude(is_default=True)

    # 返回文件夹名称列表
    return [folder.name for folder in folders]


def add_favorite_category(user_id: int, category_name: str) -> None:
    """
    添加一个新的收藏夹分类。
    如果分类已存在，则抛出异常。
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise BusinessLogicError("用户不存在。")

    folder, created = CollectionFolder.objects.get_or_create(
        user=user,
        name=category_name,
        defaults={"is_default": False}
    )
    if not created:
        raise BusinessLogicError("该分类已存在。")
    

def get_all_docs(user_id: int) -> list:
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise BusinessLogicError("用户不存在。")
    
    folder_items = FolderItem.objects.filter(user=user).select_related('document', 'folder')
    doc_map = {}

    for folder_item in folder_items:
        doc = folder_item.document
        doc_id = doc.doc_id

        if doc_id not in doc_map:
            doc_map[doc_id] = {
                "doc_id": doc.doc_id,
                "title": doc.title,
                "authors": doc.authors,
                "year": doc.year,
                "abstract": doc.abstract,
                "conference": doc.journal,
                "categories": [folder_item.folder.name],
                "doc_url": doc.arxiv_url or settings.SERVER_ADDRESS + doc.local_file_path
            }
        else:
            doc_map[doc_id]["categories"].append(folder_item.folder.name)

    return list(doc_map.values())

    
def add_favorite(user_id: int, doc_id: int) -> None:
    """
    将文献添加到用户的收藏夹中。
    如果文献已存在于默认收藏夹中，则不重复添加。
    """
    try:
        user = User.objects.get(id=user_id)
        document = Document.objects.get(doc_id=doc_id)
    except (User.DoesNotExist, Document.DoesNotExist):
        raise BusinessLogicError("用户或文献不存在。")

    all_folder = CollectionFolder.objects.filter(user=user, name='all').first()
    
    if not all_folder:
        all_folder = CollectionFolder.objects.create(
            user=user,
            name='all',
            is_default=False
        )

    FolderItem.objects.get_or_create(
        folder=all_folder,
        document=document,
        user=user
    )


def update_category(user_id: int, doc_id: int, new_categories: list) -> None:
    """
    只保留该文献属于 new_categories 指定的收藏夹（不新建收藏夹）。
    """
    try:
        user = User.objects.get(id=user_id)
        document = Document.objects.get(doc_id=doc_id)
    except (User.DoesNotExist, Document.DoesNotExist):
        raise BusinessLogicError("用户或文献不存在。")

    # 获取该用户所有收藏夹，名字到对象的映射
    all_folders = {f.name: f for f in CollectionFolder.objects.filter(user=user)}
    # 只保留已存在的收藏夹
    target_folders = [all_folders[name] for name in new_categories if name in all_folders]

    # 现有的 FolderItem
    existing_items = FolderItem.objects.filter(user=user, document=document)
    target_folder_ids = set(folder.id for folder in target_folders)

    # 删除多余的
    for item in existing_items:
        if item.folder_id not in target_folder_ids:
            item.delete()

    # 添加缺失的
    for folder in target_folders:
        FolderItem.objects.get_or_create(
            user=user,
            folder=folder,
            document=document
        )