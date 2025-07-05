from discussions.models import Conversation, ConversationParticipant, ConversationFollow
from users.models import User
from utils.exceptions import BusinessLogicError

def create_project_or_question(user_id: int, title: str, type: int, abstract: str, field: str) -> None:
    """
    创建一个新的讨论单元（Conversation），并将发起人自动添加为参与者。
    type: 0=项目讨论组，1=公开论坛
    """
    # 校验用户是否存在
    user = User.objects.filter(id=user_id).first()
    if not user:
        raise BusinessLogicError("用户不存在")

    # type 映射
    if type == 0:
        conv_type = 'project'
    elif type == 1:
        conv_type = 'forum'
    else:
        raise BusinessLogicError("无效的讨论类型")

    # 创建讨论单元
    conversation = Conversation.objects.create(
        title=title,
        initiator=user,
        type=conv_type,
        abstract=abstract,
        research_fields=field
    )

    # 添加发起人为参与者
    ConversationParticipant.objects.create(
        conversation=conversation,
        user=user,
        status='admin',  # 默认发起人为管理员
    )

    # 添加发起人为follow状态
    ConversationFollow.objects.create(
        user=user,
        conversation=conversation,
    )

    return
