
from django.db import transaction
from django.db.models import Q  # 1. 导入 Q 对象
from django.contrib.auth import authenticate  # 2. 导入 authenticate 函数
from ..models import User
from document.models import CollectionFolder  # 导入 CollectionFolder 模型
from utils.exceptions import BusinessLogicError  # 3. 导入自定义的 BusinessLogicError
import re
from django.core.paginator import Paginator, EmptyPage
from publications.models import ReadingHistory as PublicationReadingHistory
from document.models import DocumentReadingHistory

@transaction.atomic
def register_user(*, email, password, name, institution, research_fields, **kwargs):
    """
    处理用户注册的核心业务逻辑。
    """
    # 将机构和部门信息合并
    full_institution = f"{institution}"

    # 创建用户。注意：我们将请求中的 'account' 映射到 Django User 模型的 'username' 字段。
    # create_user 方法会自动处理密码的哈希加密。
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        name=name,
        institution=full_institution,
        research_fields=research_fields,
        avatar_url="12-modified.png"  # --- 新增：设置默认头像 ---
    )

    # 创建默认的document收藏夹
    CollectionFolder.objects.create(
        user=user,
        name="self-upload",
        is_default=True
    )
    
    return user

def login_user(*, request, account, password):
    """
    处理用户登录的核心业务逻辑。
    参数 'account' 实际上是用户的邮箱。
    """
    # 1. 根据邮箱查找用户
    try:
        # 使用 .get() 来确保邮箱是唯一的，如果不是，它会抛出 MultipleObjectsReturned
        user = User.objects.get(email=account)
    except User.DoesNotExist:
        # 为了安全，不明确指出是邮箱还是密码错误
        raise BusinessLogicError("账号或密码错误")

    # 2. 使用查找到的用户的 username 和传入的密码进行验证
    authenticated_user = authenticate(request=request, username=user.username, password=password)

    if authenticated_user is None:
        # 如果验证失败，authenticate 返回 None
        raise BusinessLogicError("账号或密码错误")
    
    # 确保用户是激活状态
    if not authenticated_user.is_active:
        raise BusinessLogicError("该账户已被禁用")

    return authenticated_user


def check_email_exists(*, email):
    """
    检查邮箱是否已存在。
    """
    # 只检查 email 是否存在
    exists = User.objects.filter(email=email).exists()
    return exists


def check_account_or_email_exists(*, account, email):
    """
    检查账号或邮箱是否已存在。
    """
    # 使用 Q 对象进行 OR 查询，检查 username 或 email 是否存在匹配项
    exists = User.objects.filter(Q(username=account) | Q(email=email)).exists()
    return exists

def get_user_info(*, user_id):
    """
    根据用户ID获取用户信息。
    如果用户不存在，则抛出业务逻辑异常。
    """
    try:
        user = User.objects.get(pk=user_id)
        return user
    except User.DoesNotExist:
        raise BusinessLogicError("用户不存在")

@transaction.atomic
def update_user_info(*, user_id, data):
    """
    根据传入的 user_id 更新用户信息。
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        # 此情况理论上已被序列化器处理，但作为双重保险。
        raise BusinessLogicError("指定的用户不存在。")

    # 定义所有可以被更新的字段
    updatable_fields = [
        'name', 'title', 'education', 'institution', 
        'avatar_url', 'bio', 'research_fields'
    ]
    
    # 批量更新传入数据中存在的字段
    for field in updatable_fields:
        if field in data:
            setattr(user, field, data[field])
    
    user.save()
    return user

def check_author_ownership(*, user_id: int, authors: str) -> bool:
    """
    检查一个用户的真实姓名是否存在于一个作者字符串中。
    - 不区分大小写。
    - 自动处理中英文逗号和多余的空格。
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        # 理论上序列化器会捕获此错误，这里是双重保险
        return False

    # 获取用户真实姓名，并进行清理和转小写处理
    user_real_name = user.name.strip().lower()
    if not user_real_name:
        # 如果用户没有设置真实姓名，则直接返回False
        return False

    # 解析作者列表字符串，同样进行清理和转小写
    author_list = [author.strip().lower() for author in re.split(r'[，,]', authors) if author.strip()]

    # 检查用户姓名是否在列表中
    return user_real_name in author_list

def get_users_from_same_institution(user_id: int):
    """
    根据用户ID获取同一机构的其他用户列表。
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise BusinessLogicError("用户不存在")

    # 如果用户没有设置机构，则返回空列表
    if not user.institution:
        return User.objects.none()

    # 查询同一机构的其他用户，并排除自己
    same_institution_users = User.objects.filter(
        institution=user.institution
    ).exclude(id=user_id)

    return same_institution_users

def get_combined_reading_history(user_id: int, page: int, page_size: int):
    """
    获取用户合并后的成果和文献阅读历史，并进行分页 (全字段版)。
    """
    # 1. 分别获取两种类型的历史记录对象，并预加载关联数据以提高性能
    pub_history = list(PublicationReadingHistory.objects.filter(user_id=user_id).select_related('publication'))
    doc_history = list(DocumentReadingHistory.objects.filter(user_id=user_id).select_related('document'))

    # 2. 为每个对象添加一个临时的 'history_type' 属性，以便序列化器识别
    for item in pub_history:
        item.history_type = 'publication'
    for item in doc_history:
        item.history_type = 'document'

    # 3. 合并两个列表并按阅读时间降序排序
    combined_list = sorted(
        pub_history + doc_history,
        key=lambda x: x.read_time,
        reverse=True
    )

    # 4. 使用 Django 的 Paginator 进行分页
    paginator = Paginator(combined_list, page_size)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        # 如果请求的页码超出范围，返回最后一页
        page_obj = paginator.page(paginator.num_pages)

    # 5. 构建包含分页信息的返回结果
    return {
        'total_items': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'page_size': page_size,
        'results': list(page_obj) # 返回的是分页后的对象列表
    }
