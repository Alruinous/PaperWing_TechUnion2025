from django.db import transaction
from ..models import Message, Conversation, ConversationParticipant
from users.models import User
from utils.exceptions import BusinessLogicError
from utils.email_service import send_custom_email
from publications.models import Publication

@transaction.atomic
def send_private_message(*, sender_id, receiver_id, message_type, content, project_id, result_id):
    """
    发送一对一消息，并根据消息类型处理特殊逻辑。
    """
    try:
        sender = User.objects.get(id=sender_id) if sender_id else None
        receiver = User.objects.get(id=receiver_id) if receiver_id else None
        # 只有当 project_id 不为 0 时，才去获取 Conversation 对象
        conversation = None
        if project_id and project_id != 0:
            conversation = Conversation.objects.get(conversation_id=project_id) if project_id != 0 else None


    except User.DoesNotExist:
        raise BusinessLogicError("指定的用户不存在。")
    except Conversation.DoesNotExist:
        raise BusinessLogicError("指定的项目不存在。")

    # 当消息类型为“邀请”时，执行特殊逻辑
    if message_type == 'invitation':
        if not conversation:
            raise BusinessLogicError("邀请消息必须关联一个有效的项目。")
        
          # 新逻辑：检查发送者是否是项目创建者
        if conversation.initiator != sender:
            raise BusinessLogicError("只有项目创建者才能邀请他人。", status_code=403)
        
        # 创建或更新参与者记录，将其状态设置为“已邀请”
        participant, created = ConversationParticipant.objects.get_or_create(
            conversation=conversation,
            user=receiver,
            defaults={'status': 'invited'}
        )
        
        if not created and participant.status != 'approved':
            participant.status = 'invited'
            participant.save()
    
    # 2. 申请加入项目
    elif message_type == 'apply':
        if not conversation:
            raise BusinessLogicError("申请加入消息必须关联一个有效的项目。")
        participant, created = ConversationParticipant.objects.get_or_create(
            conversation=conversation,
            user=sender,
            defaults={'status': 'pending'}
        )
        if not created and participant.status != 'approved':
            participant.status = 'pending'
            participant.save()

    # 3. 成果请求
    elif message_type == 'ask':
        if not result_id or result_id == 0:
            raise BusinessLogicError("成果数据请求消息必须关联一个有效的成果")
        # 这里只需创建消息即可
        # --- 在这里添加发送邮件的逻辑 ---
        # 确保接收者存在并且设置了邮箱
        if receiver and receiver.email:
            try:
                # 根据 result_id 查询成果标题，让邮件内容更丰富
                publication = Publication.objects.get(pub_id=result_id)
                publication_title = publication.title
            except Publication.DoesNotExist:
                publication_title = f"成果ID {result_id}" # 如果查不到，使用ID作为后备

            # 准备邮件内容
            subject = f"【PaperWing】您有一条新的成果全文请求"
            email_message = f"""
尊敬的 {receiver.username} 用户：

用户 {sender.username} ({sender.email}) 请求获取您的成果《{publication_title}》的全文数据。

他/她的请求消息是：
"{content}"

请您登录 PaperWing 平台，在您的消息中心查看并处理此请求。

此致，
PaperWing 平台团队
"""
            # 调用我们创建的函数发送邮件
            send_custom_email(
                subject=subject,
                message=email_message,
                recipient_list=[receiver.email]
            )
        # --- 邮件发送逻辑结束 ---
    # 4. 认领成果
    elif message_type == 'claim':
        # 认领成果消息，receiver 应为成果创建者，sender 为申请认领者
        pass  # 只需创建消息

    # 5. 系统消息
    elif message_type == 'system':
        sender = None  # 系统消息发送方为 None 或 id=0

    # 6. 项目群发消息
    elif message_type == 'group':
        receiver = None  # 群发消息接收方为 None 或 id=0
    
    # 7. 论坛群发消息
    elif message_type == 'forum':
        receiver = None  # 群发消息接收方为 None 或 id=0


    
    # 创建消息记录
    message = Message.objects.create(
        sender=sender,
        receiver=receiver,
        content=content,
        message_type=message_type,
        # 对于私信，conversation 字段用于关联项目元数据
        conversation=conversation,
        result_id=result_id
    )

    return message

def get_messages_for_user(*, user_id, box_type):
    """
    根据用户ID和邮箱类型（收件箱/发件箱）获取私信列表。
    """
    # 确保只查询私信（receiver 字段不为空）
    base_query = Message.objects.select_related('sender', 'receiver').filter(receiver__isnull=False)

    if box_type == 'inbox':
        messages = base_query.filter(receiver_id=user_id).order_by('-sent_at')
    elif box_type == 'sent':
        messages = base_query.filter(sender_id=user_id).order_by('-sent_at')
    else:
        # 以防万一传入无效的 box_type
        messages = Message.objects.none() 
    
    return messages