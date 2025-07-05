from typing import List, TypedDict, Dict
from users.models import User
from utils.exceptions import BusinessLogicError
from publications.models import PublicationUser
import random
from django.db.models import Q
# --- 新增：从 discussions 应用导入 ConversationParticipant 模型 ---
from discussions.models import ConversationParticipant



class Author_simple(TypedDict, total=False):
    userId: int
    userName: str
    isFollowed: int

class Author(TypedDict, total=False):
    id: int                       # 学者用户id
    name: str                     # 姓名
    email: str                   # 邮箱
    bio: str                     # 个人简介
    avatar_url: str              # 头像 URL
    institution: str             # 所属机构
    followed: int                # 粉丝数
    isFollowed: bool             # 当前用户是否关注
    paperCount: int              # 发表论文数量
    research_fields: List[str]   # 研究领域标签


def get_authors(user_id: int) -> List[Author_simple]:
    # 获取当前用户
    user = User.objects.filter(id=user_id).first()
    if not user:
        raise BusinessLogicError("用户不存在")
    
    user_fields = user.research_fields_list
    # 获取当前用户已关注的用户id集合
    followed_ids = set(User.objects.filter(followers__follower_id=user_id).values_list('id', flat=True))

    # 1. 先按研究领域匹配
    matched_users = []
    if user_fields:
        # 构造查询条件
        query = Q()
        for field in user_fields:
            query |= Q(research_fields__icontains=field)
        matched_users = list(
            User.objects.filter(query)
            .exclude(id__in={user_id} | followed_ids)
            .distinct()
            .order_by('-date_joined')[:15]
        )
    else:
        matched_users = []

    # 2. 构造 Author 列表
    authors = []
    used_ids = set()
    for u in matched_users:
        authors.append({
            "userId": u.id,
            "userName": u.name,
            "isFollowed": 0,
            "avatar": u.avatar_url
        })
        used_ids.add(u.id)
        if len(authors) >= 15:
            break

    # 3. 随机补充到20个
    if len(authors) < 20:
        # 排除自己和已在authors中的用户
        exclude_ids = used_ids | {user_id} | followed_ids
        all_others = User.objects.exclude(id__in=exclude_ids)
        all_others_list = list(all_others)
        random.shuffle(all_others_list)
        for u in all_others_list:
            if len(authors) >= 20:
                break
            authors.append({
                "userId": u.id,
                "userName": u.name,
                "isFollowed": 0,
                "avatar": u.avatar_url
            })

    return authors
    
    
def searchScholar(user_id: int, condition: str, type: str) -> List[Author]:
    """
    搜索学者
    type: 根据name, title, institution, field
    """
    authors = []
    # 构造查询条件
    query = Q()
    if type == "name":
        # name和username任意一个模糊匹配即可
        query = Q(name__icontains=condition)
    elif type == "title":
        query = Q(title__icontains=condition)
    elif type == "institution":
        query = Q(institution__icontains=condition)
    elif type == "field":
        query = Q(research_fields__icontains=condition)
    else:
        # 类型不合法，返回空
        return authors

    users = User.objects.filter(query)

    # 获取当前用户已关注的用户id集合
    followed_ids = set(
        User.objects.filter(followers__follower_id=user_id).values_list('id', flat=True)
    )

    for u in users:
        authors.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "bio": u.bio,
            "avatar_url": u.avatar_url,
            "institution": u.institution,
            "followed": u.followers.count(),
            "isFollowed": u.id in followed_ids,
            "paperCount": PublicationUser.objects.filter(user=u).count(),
            "research_fields": u.research_fields_list,
        })

    return authors


def search_users_by_name(search_name: str, project_id: int) -> List[Dict]:
    """
    根据真实姓名模糊搜索用户，并返回其在特定项目中的状态。
    """
    if not search_name:
        return []

    # 1. 构造查询条件，使用 icontains 进行模糊匹配
    query = Q(name__icontains=search_name)
    found_users = User.objects.filter(query)

    # 2. 为了提高效率，一次性获取项目中所有参与者的状态，存入字典
    participant_statuses = {
        p.user_id: p.status
        for p in ConversationParticipant.objects.filter(conversation_id=project_id)
    }

    # 3. 构建返回结果列表
    authors_list = []
    for u in found_users:
        # 从预先获取的字典中查询状态，如果用户不在字典中，则为 'not_involved'
        status = participant_statuses.get(u.id, 'not_involved')

        if status == 'not_involved':
            authors_list.append({
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "bio": u.bio or "",
                "avatar_url": u.avatar_url or "",
                "institution": u.institution or "",
                "followed": u.followers.count(),
                "paperCount": PublicationUser.objects.filter(user=u).count(),
                "research_fields": u.research_fields_list,
                "status": status  # 这里的 status 必然是 'not_involved'
            })

    return authors_list