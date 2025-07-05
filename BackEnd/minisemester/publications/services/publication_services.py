from django.core.files.storage import default_storage, FileSystemStorage
from django.db import transaction
from ..models import Publication, PublicationComment, PublicationLike, PublicationUser, ReadingHistory
from users.models import User
from utils.exceptions import BusinessLogicError
import os
import uuid
from django.db.models import Q
from utils.ai_services import get_ai_response
from django.db import transaction
from django.utils import timezone
from publications.serializers import CommentSerializer
from discussions.models import Message
from discussions.services import send_private_message
from users.services import user_follow
from utils.email_service import send_custom_email


def handle_file_upload(file):
    """处理文件上传并返回可供访问的 URL 路径"""
    fs = FileSystemStorage()

    # 为了避免文件名冲突和安全问题，生成一个唯一的文件名
    # 最好将文件存放在一个子目录中，例如 'publications/'
    ext = os.path.splitext(file.name)[1]
    unique_filename = f"publications/{uuid.uuid4()}{ext}"

    # 保存文件
    filename = fs.save(unique_filename, file)

    # 修正：返回可以通过 MEDIA_URL 访问的相对 URL 路径
    # 例如：/media/publications/some-uuid.pdf
    return fs.url(filename)


@transaction.atomic
def create_publication(validated_data):
    """
    根据验证过的数据创建科研成果记录 (不安全版本)。
    """
    # validated_data 中已经包含了经过序列化器验证的 created_by User 对象
    publication = Publication.objects.create(**validated_data)
    # 加入user到PublicationUser表中(上传者默认认领)
    PublicationUser.objects.create(
        publication=publication,
        user=publication.created_by
    )


def handle_comment_creation(validated_data):
    """
    处理评论创建并返回操作结果
    """
    try:
        # 获取出版物
        publication = Publication.objects.get(pub_id=validated_data['pub_id'])
        # 获取用户
        user = User.objects.get(id=validated_data['user_id'])
        # 创建评论
        comment = PublicationComment.objects.create(
            publication=publication,
            user=user,
            content=validated_data['comment'],
            created_at=timezone.now()
        )
        return {
            "success": True,
            "message": "评论发布成功"
        }
    except Publication.DoesNotExist:
        raise BusinessLogicError("指定的科研成果不存在")
    except User.DoesNotExist:
        raise BusinessLogicError("指定的用户不存在")
    except Exception as e:
        raise BusinessLogicError(f"评论发布失败: {str(e)}")


def handle_publication_like_action(validated_data):
    """
    用户给成果点赞
    """
    try:
        # 获取出版物
        publication = Publication.objects.get(pub_id=validated_data['pub_id'])
        # 获取用户
        user = User.objects.get(id=validated_data['user_id'])

        publication_like = PublicationLike.objects.create(
            publication=publication,
            user=user,
            liked_at=timezone.now()
        )
        return {
            "success": True,
            "message": "点赞成功",
            "publication_title": publication.title,
            "username": user.username
        }

    except Publication.DoesNotExist:
        raise BusinessLogicError("指定的科研成果不存在")
    except User.DoesNotExist:
        raise BusinessLogicError("指定的用户不存在")
    except Exception as e:
        raise BusinessLogicError(f"操作失败: {str(e)}")


def get_publication_detail(pub_id, user_id):
    '''
    获取科研成果详情
    '''
    try:
        # 获取出版物
        publication = Publication.objects.get(pub_id=pub_id)
        # 获取用户
        user = User.objects.get(id=user_id)
        # 检查用户是否点赞
        is_favour = PublicationLike.objects.filter(
            publication__pub_id=pub_id,
            user=user
        ).exists()

        # --- 错误修正 1: 使用正确的 ORM 查询方式 ---
        # 错误写法: pub_id=pub_id
        # 正确写法: publication__pub_id=pub_id 或者 publication_id=pub_id
        publication_users = PublicationUser.objects.filter(
            publication__pub_id=pub_id
        ).select_related('user')

        # --- 错误修正 2: 循环体内使用正确的变量 ---
        # 构建作者列表
        authors = [
            {
                # 错误写法: publication.user.name
                # 正确写法: pub_user.user.name (pub_user 是循环变量)
                "name": pub_user.user.name,
                "user_id": pub_user.user.id,
                "avatar": pub_user.user.avatar_url or "",
            }
            for pub_user in publication_users
        ]

        # 如果通过 PublicationUser 没有找到平台内的作者，
        # 则回退到使用原始的 authors 文本字段进行解析
        if not authors and publication.authors:
            authors = [{"name": name.strip(), "user_id": None, "avatar": ""}
                       for name in publication.authors_list]

        # 获取点赞总数
        likes_count = publication.likes.count()

        return {
            "title": publication.title,
            "type": publication.type,
            "authors": authors,
            "journal": publication.journal,
            "volume": publication.volume,
            "issue": publication.issue,
            "year": str(publication.year) if publication.year else "",
            "abstract": publication.abstract,
            "keywords": publication.keywords,
            "created_by": publication.created_by.id,
            "isFavour": is_favour,
            "likes": likes_count,  # 返回点赞数而不是QuerySet
            "download": str(publication.local_file_path) if publication.local_file_path else "",
            "external_url": publication.external_url, # --- 新增：外部链接字段 ---
            "research_fields": publication.research_fields_list
        }
    except Publication.DoesNotExist:
        raise BusinessLogicError("指定的科研成果不存在")
    except User.DoesNotExist:
        raise BusinessLogicError("指定的用户不存在")
    except Exception as e:
        raise BusinessLogicError(f"获取成果详情失败: {str(e)}")


def get_publication_comments(pub_id):
    """
    获取科研成果的评论列表
    :param pub_id: 成果ID
    :return: 包含评论列表的字典
    """
    try:
        # 验证出版物是否存在
        publication = Publication.objects.get(pub_id=pub_id)

        # 获取所有评论，按照创建时间倒序排列
        comments = PublicationComment.objects.filter(
            publication=publication
        ).order_by('created_at').select_related('user')

        # 序列化评论数据
        serializer = CommentSerializer(comments, many=True)

        return {
            "success": True,
            "message": "获取评论成功",
            "data": {
                "comments": serializer.data
            }
        }
    except Publication.DoesNotExist:
        return {
            "success": False,
            "message": "指定的科研成果不存在",
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "message:": "",
            "error": str(e)
        }


def check_publication_duplicate(title: str, user_id: int) -> bool:
    """
    检查指定用户是否已上传过相同标题的 'Literature' 类型成果。
    """
    return Publication.objects.filter(
        title=title,
        type='Literature',
        created_by_id=user_id
    ).exists()

def get_user_publications(user_id: int):
    pub_ids = PublicationUser.objects.filter(user_id=user_id).values_list('publication_id', flat=True)
    return Publication.objects.filter(pub_id__in=pub_ids)

def cancel_favour(pub_id: int, user_id: int) -> None:
    """
    取消用户对指定科研成果的点赞。
    """
    pub = Publication.objects.filter(pub_id=pub_id).first()
    user = User.objects.filter(id=user_id).first()

    if not pub or not user:
        raise BusinessLogicError("指定的科研成果或用户不存在")

    like_obj = PublicationLike.objects.filter(publication=pub, user=user).first() 
    if not like_obj:
        raise BusinessLogicError("未点赞，无法取消点赞")
    like_obj.delete()


@transaction.atomic
def respond_to_publication_claim(publication_id: int, claimer_id: int, approver_id: int, message_id: int, response_action: str):
    from publications.models import Publication, PublicationUser
    from users.models import User
    from utils.exceptions import BusinessLogicError

    try:
        publication = Publication.objects.get(pub_id=publication_id)
        claimer = User.objects.get(id=claimer_id)
    except Publication.DoesNotExist:
        raise BusinessLogicError("指定的科研成果不存在。")
    except User.DoesNotExist:
        raise BusinessLogicError("指定的认领者用户不存在。")

    if publication.created_by.id != approver_id:
        raise BusinessLogicError("只有成果的上传者才能处理认领请求。", status_code=403)

    if response_action == 'accept':
        PublicationUser.objects.get_or_create(
            publication=publication,
            user=claimer
        )
    elif response_action == 'decline':
        # 给认领者发一条拒绝消息
        send_private_message(
            sender_id=approver_id,
            receiver_id=claimer_id,
            message_type='user',
            content=f"抱歉，您的成果《{publication.title}》认领请求已被拒绝。",
            project_id=0,
            result_id=publication_id
        )

    # 删除原认领消息
    try:
        msg = Message.objects.get(message_id=message_id, message_type='claim')
        msg.delete()
    except Message.DoesNotExist:
        pass

def check_claim_ownership(*, publication_id: int, user_id: int) -> bool:
    """
    检查一个用户的真实姓名是否存在于指定成果的作者列表中。
    """
    try:
        publication = Publication.objects.get(pub_id=publication_id)
        user = User.objects.get(id=user_id)
    except (Publication.DoesNotExist, User.DoesNotExist):
        # 此错误理论上会被序列化器捕获，这里是双重保险
        return False

    # 获取用户真实姓名，并进行清理和转小写处理
    user_real_name = user.name.strip().lower()
    if not user_real_name:
        return False

    # 解析成果的作者列表字符串，同样进行清理和转小写
    author_list = [author.strip().lower() for author in publication.authors_list]

    # 检查用户姓名是否在列表中
    return user_real_name in author_list


def notify_followers_by_email(user_id: int, notification_type: int, number: int):
    """
    向指定用户的所有粉丝发送新成果发布的邮件通知。
    """
    try:
        publisher = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise BusinessLogicError("发布成果的用户不存在。")

    # 1. 获取该用户的所有粉丝
    followers = user_follow.get_followers_list(user_id)
    if not followers.exists():
        return "该用户没有粉丝，无需发送通知。"

    # 2. 准备邮件内容
    if notification_type == 0: # 单个上传
        subject = f"【PaperWing】您关注的用户 {publisher.name} 发布了新成果"
        content = f"""
尊敬的用户：

您好！

您关注的学者 {publisher.name} 发布了一项新的科研成果。

您可以登录 PaperWing 平台，访问其个人主页查看详情。

此致，
PaperWing 平台团队
"""
    else: # 批量上传
        subject = f"【PaperWing】您关注的用户 {publisher.name} 发布了 {number} 项新成果"
        content = f"""
尊敬的用户：

您好！

您关注的学者 {publisher.name} 新增了 {number} 项科研成果。

您可以登录 PaperWing 平台，访问其个人主页查看详情。

此致，
PaperWing 平台团队
"""

    # 3. 筛选出有邮箱的粉丝并发送邮件
    sent_count = 0
    for follower in followers:
        if follower.email:
            send_custom_email(
                subject=subject,
                message=content,
                recipient_list=[follower.email]
            )
            sent_count += 1
    
    if sent_count > 0:
        return f"已成功向 {sent_count} 位粉丝发送邮件通知。"
    else:
        return "用户的粉丝均未设置邮箱，无法发送通知。"


@transaction.atomic
def add_publication_reading_history(user_id: int, publication_id: int):
    """
    添加成果阅读历史，并确保每个用户的历史记录不超过100条。
    """
    try:
        user = User.objects.get(id=user_id)
        publication = Publication.objects.get(pub_id=publication_id)
    except (User.DoesNotExist, Publication.DoesNotExist):
        raise BusinessLogicError("用户或成果不存在。")

    # 使用 get_or_create 避免完全相同的记录重复。如果已存在，则更新其 read_time。
    history_entry, created = ReadingHistory.objects.get_or_create(
        user=user,
        publication=publication,
        defaults={'read_time': timezone.now()}
    )

    # 如果记录不是新创建的（即重复阅读），则手动更新时间戳
    if not created:
        history_entry.read_time = timezone.now()
        history_entry.save(update_fields=['read_time'])

    # 检查并维持每个用户最多100条历史记录的限制
    user_history_count = ReadingHistory.objects.filter(user=user).count()
    if user_history_count > 100:
        # 找出最旧的一条记录并删除
        oldest_entry = ReadingHistory.objects.filter(user=user).order_by('read_time').first()
        if oldest_entry:
            oldest_entry.delete()


def _build_search_conclusion_prompt(publications, query: str) -> str:
    """
    构建用于生成搜索总结的 AI Prompt。
    """
    if not publications:
        return "未找到相关文献。"

    # 准备给 AI 的上下文信息
    context = ""
    for i, pub in enumerate(publications[:5]):  # 最多给 AI 前5篇的内容作为参考
        context += f"文献 {i+1}: 标题: {pub.title}\n摘要: {pub.abstract}\n\n"

    prompt = f"""
    我进行了一次文献搜索，搜索词为 "{query}"，共找到了 {len(publications)} 篇相关文献。
    以下是部分文献的标题和摘要：
    ---
    {context}
    ---
    请根据以上信息，为本次搜索生成一段简洁、概括性的总结。总结应包括找到的文献总数，并简要提及这些文献的核心主题或共同点。
    """
    return prompt


# @transaction.atomic
# def search_and_summarize_publications(user_id: int, condition: str, pub_type: str) -> dict:
    """
    执行文献搜索，并调用 AI 生成总结。
    """
    # 1. 构建基础查询
    query = Q()
    if condition:
        query &= (
            Q(title__icontains=condition) |
            Q(abstract__icontains=condition) |
            Q(keywords__icontains=condition) |
            Q(authors__icontains=condition)
        )

    if pub_type:
        query &= Q(type=pub_type)

    # 2. 执行查询，并预加载相关数据以优化性能
    publications = Publication.objects.filter(query).select_related(
        'created_by').prefetch_related('likes', 'publicationuser_set__user').distinct()

    # 3. 格式化搜索结果
    results_list = []
    for pub in publications:
        # 检查当前用户是否点赞
        is_favor = False
        if user_id:
            is_favor = pub.likes.filter(user_id=user_id).exists()

        # 获取作者信息
        pub_users = pub.publicationuser_set.all()
        authors_details = []
        if pub_users:
            authors_details = [{"name": pu.user.name, "user_id": pu.user.id,
                                "avatar": pu.user.avatar_url or ""} for pu in pub_users]
        else:
            authors_details = [{"name": name.strip(), "user_id": None, "avatar": ""}
                               for name in pub.authors_list]

        results_list.append({
            "pub_id": pub.pub_id,
            "title": pub.title,
            "journal": pub.journal,
            "authors": authors_details,
            "year": str(pub.year) if pub.year else "",
            "abstract": pub.abstract,
            "keywords": [kw.strip() for kw in pub.keywords.split(',') if kw.strip()] if pub.keywords else [],
            "external_url": pub.external_url,
            "local_file_path": pub.local_file_path,
            "created_by": pub.created_by.id,
            "favor_count": pub.likes.count(),
            "is_favor": is_favor
        })

    # 4. 调用 AI 生成总结
    ai_prompt = _build_search_conclusion_prompt(publications, condition)
    conclusion = get_ai_response(ai_prompt, "你是一个高效的科研助理，擅长总结信息。")

    return {
        "conclusion": conclusion,
        "publications": results_list
    }
# --- 新增服务函数 ---
def update_publication_local_file_path(pub_id: int, url: str):
    """
    更新指定成果的本地文件路径。
    """
    try:
        publication = Publication.objects.get(pub_id=pub_id)
        publication.local_file_path = url
        publication.save(update_fields=['local_file_path'])
    except Publication.DoesNotExist:
        # 此处错误理论上会被序列化器捕获，作为双重保险
        raise BusinessLogicError("指定的成果不存在。")


@transaction.atomic
def search_publications(user_id: int, condition: str, pub_type: str) -> list:
    """
    执行文献搜索，不包含 AI 总结，仅返回格式化的成果列表。
    """
    # 1. 构建基础查询
    query = Q()
    if condition:
        query &= (
            Q(title__icontains=condition) |
            Q(abstract__icontains=condition) |
            Q(keywords__icontains=condition) |
            Q(authors__icontains=condition)
        )

    if pub_type:
        query &= Q(type=pub_type)

    # 2. 执行查询，并预加载相关数据以优化性能
    publications = Publication.objects.filter(query).select_related(
        'created_by').prefetch_related('likes', 'publicationuser_set__user').distinct()

    # 3. 格式化搜索结果
    results_list = []
    for pub in publications:
        # 检查当前用户是否点赞
        is_favor = False
        if user_id:
            is_favor = pub.likes.filter(user_id=user_id).exists()

        # 获取作者信息
        pub_users = pub.publicationuser_set.all()
        authors_details = []
        if pub_users:
            authors_details = [{"name": pu.user.name, "user_id": pu.user.id,
                                "avatar": pu.user.avatar_url or ""} for pu in pub_users]
        else:
            authors_details = [{"name": name.strip(), "user_id": None, "avatar": ""}
                               for name in pub.authors_list]

        results_list.append({
            "pub_id": pub.pub_id,
            "title": pub.title,
            "journal": pub.journal,
            "authors": authors_details,
            "year": str(pub.year) if pub.year else "",
            "abstract": pub.abstract,
            "keywords": [kw.strip() for kw in pub.keywords.split(',') if kw.strip()] if pub.keywords else [],
            "external_url": pub.external_url,
            "local_file_path": pub.local_file_path,
            "created_by": pub.created_by.id,
            "favor_count": pub.likes.count(),
            "is_favor": is_favor
        })

    return results_list


@transaction.atomic
def generate_search_summary(condition: str, pub_type: str) -> str:
    """
    根据搜索条件获取文献，并调用 AI 生成总结。
    """
    # 1. 构建基础查询
    query = Q()
    if condition:
        query &= (
            Q(title__icontains=condition) |
            Q(abstract__icontains=condition) |
            Q(keywords__icontains=condition) |
            Q(authors__icontains=condition)
        )

    if pub_type:
        query &= Q(type=pub_type)

    # 2. 执行查询
    publications = Publication.objects.filter(query).distinct()

    # 3. 调用 AI 生成总结
    ai_prompt = _build_search_conclusion_prompt(publications, condition)
    conclusion = get_ai_response(ai_prompt, "你是一个高效的科研助理，擅长总结信息。")

    return conclusion




def get_recommended_publications(user_id, pub_type):
    """
    获取科研成果详情
    :param user_id: 用户ID，用于检查关注状态
    :param pub_type: 成果类型
    :return: 包含成果详情的字典
    """
    try:
        # 验证用户存在
        user=User.objects.get(id=user_id)

        # 获取用户关联的成果ID集合
        user_publication_ids = PublicationUser.objects.filter(
            user_id=user_id
        ).values_list('publication_id', flat=True)

        # 获取指定类型且用户关联的成果列表
        publications = Publication.objects.filter(
            type=pub_type,
            pub_id__in=user_publication_ids
        ).order_by('-year', '-created_at')

        # 构建返回数据
        data=[]
        for pub in publications:
            data.append({
                "pub_id": pub.pub_id,
                "title": pub.title,
                "year":str(pub.year) if pub.year else "",
                "authors": pub.authors
            })
        return {
            "data":data,
            "success":True,
            "message": "获取成果成功"
        }

    except User.DoesNotExist:
        return {
            "data": [],
            "success": False,
            "message": "指定用户不存在"
        }
    except Exception as e:
        return {
            "data": [],
            "success": False,
            "message": f"获取科研成果列表失败：{str(e)}"
        }
    
