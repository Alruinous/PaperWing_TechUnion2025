from ..models import Conversation, ConversationParticipant, ConversationFollow, Message
from users.models import User
from utils.exceptions import BusinessLogicError
from django.db.models import Q
from utils.ai_services import get_ai_response


def create_conversation(initiator: User, title: str, type: str) -> Conversation:
    """
    创建新的讨论单元，并将发起人自动添加为参与者。
    
    :param initiator: 发起这次创建的用户对象 (User instance)
    :param title: 讨论单元的标题
    :param type: 讨论单元的类型 ('forum' or 'project')
    :return: 创建成功的 Conversation 对象
    """
    # 创建讨论单元
    conversation = Conversation.objects.create(
        initiator=initiator,
        title=title,
        type=type
    )

    # 将发起人添加为参与者，状态为“已批准”
    ConversationParticipant.objects.create(
        conversation=conversation,
        user=initiator,
        status='approved'
    )

    return conversation

def get_projects_by_creator(user_id):
    """
    根据创建者ID获取其创建的所有项目。
    """
    # 查询类型为 'project' 且发起人为指定 user_id 的所有对话
    projects = Conversation.objects.filter(
        initiator_id=user_id,
        type='project'
    ).order_by('-conversation_id')  # 按创建时间倒序排列
    return projects

def get_participant_status(*, user_id, project_id):
    """
    查询指定用户在指定项目中的参与状态。
    """
    try:
        # 尝试直接从参与者表中获取记录
        participant = ConversationParticipant.objects.get(
            user_id=user_id,
            conversation_id=project_id
        )
        # 如果找到记录，直接返回其状态
        return participant.status
    except ConversationParticipant.DoesNotExist:
        # 如果在参与者表中找不到记录，说明该用户未以任何方式参与该项目
        return "not_involved"
    
def get_project_details(project_id: int):
    """
    根据项目ID获取项目的详细信息。
    使用 select_related('initiator') 优化数据库查询，一次性获取项目及其创建者信息。
    """
    try:
        project = Conversation.objects.select_related('initiator').get(
            conversation_id=project_id,
            type='project'
        )
        return project
    except Conversation.DoesNotExist:
        raise BusinessLogicError("指定的项目不存在。")
    
def respond_to_invitation(*, user_id: int, project_id: int, response_action: str):
    """
    处理用户对项目邀请的回复。

    Args:
        user_id (int): 回复邀请的用户ID。
        project_id (int): 相关的项目ID。
        response_action (str): 用户的回复，'accept' 或 'decline'。
    """
    try:
        # 查找对应的参与记录
        participant = ConversationParticipant.objects.get(
            user_id=user_id,
            conversation_id=project_id
        )
    except ConversationParticipant.DoesNotExist:
        raise BusinessLogicError("未找到相关的项目参与记录。")

    # 关键验证：确保用户是在“被邀请”的状态下进行操作
    if participant.status != 'invited' and participant.status != 'pending':
        raise BusinessLogicError(f"操作无效，您当前的状态是 '{participant.get_status_display()}'，不是 '已邀请'。")

    if response_action == 'accept':
        # 如果同意，将状态更新为“已批准”
        participant.status = 'approved'
        participant.save()
    elif response_action == 'decline':
        # 如果拒绝，直接删除这条参与记录
        participant.delete()

def delete_project_member(*, project_id: int, user_id_to_delete: int):
    """
    从项目中删除一个成员。

    Args:
        project_id (int): 项目的ID。
        user_id_to_delete (int): 要被删除的用户的ID。
    """
    try:
        # 查找要被删除的用户在项目中的参与记录
        participant = ConversationParticipant.objects.get(
            conversation_id=project_id,
            user_id=user_id_to_delete
        )
    except ConversationParticipant.DoesNotExist:
        # 如果用户本来就不在项目中，可以认为操作已成功或直接忽略
        # 为了明确，我们返回一个消息
        raise BusinessLogicError("该用户不是项目成员，无需删除。")

    # 关键验证：禁止删除项目管理员
    if participant.status == 'admin':
        raise BusinessLogicError("不能删除项目创建者（管理员）。")

    # 如果不是管理员，则执行删除操作
    participant.delete()


def get_joined_projects(user_id):
    """
    获取用户加入的所有项目（approved 或 admin）。
    """
    # 只查项目类型
    participant_qs = ConversationParticipant.objects.filter(
        user_id=user_id,
        status__in=['approved', 'admin'],
        conversation__type='project'
    ).select_related('conversation')
    # 提取项目
    projects = [p.conversation for p in participant_qs]
    return projects


#------关于讨论单元forum---------

def get_forum_recommended(user_id: int) -> list:
    """
    获取推荐的论坛类型讨论单元。
    """
    recommended_questions = []
    user = User.objects.filter(id=user_id).first()
    if not user:
        raise BusinessLogicError("用户不存在")
    
    user_fields = user.research_fields_list
    # 查询当前用户已关注的 forum id 集合
    followed_forum_ids = set(
        ConversationFollow.objects.filter(user_id=user_id, conversation__type='forum')
        .values_list('conversation_id', flat=True)
    )

    if not user_fields:
        lastest_forum_5 = Conversation.objects.filter(type='forum').order_by('-created_at')[:5]
    else:
        # 有研究方向：构造查询条件
        query = Q()
        for field in user_fields:
            query |= Q(research_fields__icontains=field)
        # 先根据研究方向筛选前3个
        matched_forums = list(Conversation.objects.filter(type='forum').filter(query).order_by('-created_at')[:3])
        if len(matched_forums) < 5:
            # 还需要补多少个
            needed = 5 - len(matched_forums)
            exclude_ids = [f.conversation_id for f in matched_forums]
            # 补充最新的，不重复已有的
            fillers = list(Conversation.objects.filter(type='forum').exclude(conversation_id__in=exclude_ids).order_by('-created_at')[:needed])
            matched_forums += fillers
        lastest_forum_5 = matched_forums
        if not lastest_forum_5:
            # 如果按领域匹配结果为空，fallback 返回最新的公开论坛
            lastest_forum_5 = Conversation.objects.filter(type='forum').order_by('-created_at')[:5]
    for forum in lastest_forum_5:
        recommended_questions.append({
            "abstract": forum.abstract,
            "initiatorAvatar": forum.initiator.avatar_url,
            "initiatorId": forum.initiator.id,
            "initiatorName": forum.initiator.name,
            "isFollowed": forum.conversation_id in followed_forum_ids,
            "questionId": forum.conversation_id,
            "title": forum.title,
            "year": forum.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return recommended_questions


def get_forum_followed(user_id: int) -> list:
    """
    获取用户已关注的论坛类型讨论单元。
    """
    # 假设有一个关注表，记录用户关注的论坛
    followed_questions = []
    user = User.objects.get(id=user_id)
    if not user:
        raise BusinessLogicError("用户不存在")
    
    # 查询所有已关注的 forum id
    followed_forum_ids = set(
        ConversationFollow.objects.filter(user_id=user_id, conversation__type='forum')
        .values_list('conversation_id', flat=True)
    )
    forums_follow = user.followed_conversations.filter(conversation__type='forum')
    for forum_follow in forums_follow:
        forum = forum_follow.conversation
        followed_questions.append({
            "abstract": forum.abstract,
            "initiatorAvatar": forum.initiator.avatar_url,
            "initiatorId": forum.initiator.id,
            "initiatorName": forum.initiator.name,
            "isFollowed": forum.conversation_id in followed_forum_ids,
            "questionId": forum.conversation_id,
            "title": forum.title,
            "year": forum.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return followed_questions
    

def get_forum_mine(user_id: int) -> list:
    """
    获取用户自己发起的论坛类型讨论单元。
    """
    my_questions = []
    user = User.objects.get(id=user_id)
    if not user:
        raise BusinessLogicError("用户不存在")
    my_forums = Conversation.objects.filter(participants__user=user, participants__status='admin', type='forum').distinct()

    for forum in my_forums:
        my_questions.append({
            "abstract": forum.abstract,
            "initiatorAvatar": forum.initiator.avatar_url,
            "initiatorId": forum.initiator.id,
            "initiatorName": forum.initiator.name,
            "isFollowed": True,
            "questionId": forum.conversation_id,
            "title": forum.title,
            "year": forum.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return my_questions


def get_forum(user_id: int) -> dict:
    """
    获取所有论坛类型的讨论单元，分为推荐、已关注、自己发起。
    """
    data = {
        "recommended_questions": get_forum_recommended(user_id),
        "followed_questions": get_forum_followed(user_id),
        "my_questions": get_forum_mine(user_id)
    }
    return data

def follow_question(user_id: int, question_id: int) -> None:
    """
    用户关注某个论坛（question）。
    """
    try:
        user = User.objects.get(id=user_id)
        conversation = Conversation.objects.get(conversation_id=question_id, type='forum')
    except User.DoesNotExist:
        raise BusinessLogicError("用户不存在")
    except Conversation.DoesNotExist:
        raise BusinessLogicError("论坛不存在")

    # 防止重复关注
    obj, created = ConversationFollow.objects.get_or_create(
        user=user,
        conversation=conversation
    )
    if not created:
        # 已经关注，无需重复操作，可以选择抛出异常或直接返回
        raise BusinessLogicError("已关注，无需重复关注")
    

def unfollow_question(user_id: int, question_id: int) -> None:
    """
    用户取消关注某个论坛（question）。
    """
    try:
        user = User.objects.get(id=user_id)
        conversation = Conversation.objects.get(conversation_id=question_id, type='forum')
    except User.DoesNotExist:
        raise BusinessLogicError("用户不存在")
    except Conversation.DoesNotExist:
        raise BusinessLogicError("论坛不存在")

    # 查找关注记录
    follow_record = ConversationFollow.objects.filter(user=user, conversation=conversation).first()
    if not follow_record:
        raise BusinessLogicError("未关注，无需取关")
    
    follow_record.delete()  # 删除关注记录