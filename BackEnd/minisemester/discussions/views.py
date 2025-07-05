from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from . import services
from .serializers import (
    ConversationCreateSerializer, SendMessageSerializer, 
    GetMessagesRequestSerializer, MessageListSerializer,
    # --- 新增导入 ---
    DeleteMemberSerializer
)
from .services import send_private_message, create_conversation
from utils.decorators import api_exception_handler
from utils.exceptions import BusinessLogicError
from users.serializers import UserInfoRequestSerializer # 复用这个验证器
from .serializers import JoinedProjectRequestSerializer, JoinedProjectListSerializer, RespondInvitationSerializer, ProjectListSerializer, ParticipantStatusRequestSerializer, ProjectDetailSerializer, ProjectReplyListSerializer# 导入新的序列化器
from .services import get_joined_projects
from .serializers import ProjectReplySerializer
from .models import Message, Conversation, User
# --- 新增导入 ---
from utils.auth_decorators import login_and_owner_required


@csrf_exempt
@require_POST
@api_exception_handler
def create_conversation_view(request):
    """
    创建讨论单元的视图函数。
    """
    # 检查用户是否登录 (在实际项目中，这里会用 Token 验证)
    if not request.user.is_authenticated:
        raise BusinessLogicError("用户未登录，请先登录")

    # 解析请求体数据
    data = json.loads(request.body)

    # 使用 Serializer 验证数据
    serializer = ConversationCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)  # 如果验证失败，会抛出 ValidationError

    # 调用 Service 层执行业务逻辑
    # 由于 __init__.py 的设置，这里的调用方式保持不变
    services.create_conversation(
        initiator=request.user,
        title=serializer.validated_data.get('title'),
        type=serializer.validated_data.get('type')
    )

    # 返回成功的响应
    return JsonResponse({"success": True, "message": "讨论单元创建成功"}, status=200)

@csrf_exempt
@require_POST
@api_exception_handler
@login_and_owner_required(param_name='senderId')
def send_message_view(request):
    """
    发送用户消息/邀请消息/成果数据请求消息/系统消息
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    # --- 新增：在验证前，转换前端传入的消息类型 ---
    # 根据您的要求，不修改模型，而是在视图层处理数据不一致的问题。
    # 如果前端传来 'invite'，我们将其翻译成后端模型认识的 'invitation'。
    if data.get('type') == 'invite':
        data['type'] = 'invitation'
        
    # 安全检查：确保当前登录用户是发送者
    serializer = SendMessageSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    validated_data = serializer.validated_data

    
    message = services.send_private_message(
        sender_id=validated_data['senderId'],
        receiver_id=validated_data['receiverId'],
        message_type=validated_data['type'],
        content=validated_data['content'],
        project_id=validated_data.get('projectId'),
        result_id=validated_data.get('resultId')
    )

    return JsonResponse({
        "success": True,
        "messageId": message.message_id,
        "receiverId": validated_data['receiverId']
    }, status=200)

@csrf_exempt
@require_POST  # 1. 关键修改：将接口从 GET 改为 POST
@api_exception_handler
# --- 使用新版装饰器，参数名为 'userId' ---
@login_and_owner_required(param_name='userId')
def get_messages_view(request):
    """
    获取用户的收件箱或已发送消息列表 (不安全版本)。
    接收 POST 请求，参数在 JSON body 中。
    """
    # 2. 关键修改：从 request.body 中解析 JSON 数据，而不是 request.GET
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    # 3. 移除登录验证
    # if not request.user.is_authenticated:
    #     raise BusinessLogicError("用户未登录，请先登录")

    # 验证请求参数
    request_serializer = GetMessagesRequestSerializer(data=data)
    request_serializer.is_valid(raise_exception=True)
    
    validated_data = request_serializer.validated_data
    user_id = validated_data['userId']
    box_type = validated_data['box']

    # 4. 移除权限检查，完全信任前端传入的 userId
    # if request.user.id != user_id:
    #     raise BusinessLogicError("无权查看他人消息。", status_code=403)

    # 调用服务层获取消息
    messages_queryset = services.get_messages_for_user(user_id=user_id, box_type=box_type)

    # 序列化消息列表
    messages_serializer = MessageListSerializer(messages_queryset, many=True)

    response_data = {
        "success": True,
        "data": {
            "total": messages_queryset.count(),
            "messages": messages_serializer.data
        }
    }

    return JsonResponse(response_data, status=200)


@csrf_exempt
@require_POST
@api_exception_handler
# --- 使用新版装饰器，参数名为 'user_id' ---
@login_and_owner_required(param_name='user_id')
def create_project_or_question(request):
    data = json.loads(request.body)
    user_id = data['user_id']
    title = data['title']
    type = data['type']
    abstract = data['abstract']
    field = data['field']

    services.create_project_or_question(user_id, title, type, abstract, field)

    return JsonResponse({
        "success": True,
        "message": "创建成功"
    }, status=200)


@csrf_exempt
@require_POST
@api_exception_handler
def get_created_projects_view(request):
    """
    获取指定用户创建的所有项目列表。
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    # 验证请求参数中的 userId
    request_serializer = UserInfoRequestSerializer(data=data)
    request_serializer.is_valid(raise_exception=True)
    user_id = request_serializer.validated_data['userId']

    # 调用服务层获取项目列表
    projects_queryset = services.get_projects_by_creator(user_id=user_id)

    # 序列化数据以供响应
    projects_serializer = ProjectListSerializer(projects_queryset, many=True)

    # 构建响应体
    response_data = {
        "success": True,
        "data": {
            "total": projects_queryset.count(),
            "projects": projects_serializer.data
        }
    }
    return JsonResponse(response_data, status=200)

@csrf_exempt
@require_POST
@api_exception_handler
def get_participant_status_view(request):
    """
    获取用户在特定项目中的参与状态。
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    # 验证请求数据
    serializer = ParticipantStatusRequestSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    # 调用服务层获取状态
    status = services.get_participant_status(
        user_id=validated_data['userId'],
        project_id=validated_data['projectId']
    )

    # 构建并返回成功响应
    return JsonResponse({
        "success": True,
        "data": {
            "status": status
        }
    })

@csrf_exempt
@require_GET
@api_exception_handler
def get_project_detail_view(request):
    """
    获取单个项目的详细信息。
    """
    project_id_str = request.GET.get('projId')
    if not project_id_str:
        raise BusinessLogicError("缺少项目ID (projId) 参数。")
    
    try:
        project_id = int(project_id_str)
    except (ValueError, TypeError):
        raise BusinessLogicError("项目ID (projId) 格式无效，应为整数。")

    # 调用服务层获取项目对象
    project = services.get_project_details(project_id)
    
    # 使用序列化器格式化数据
    serializer = ProjectDetailSerializer(project)
    
    # 返回成功的响应
    return JsonResponse({
        "success": True,
        "message": "获取项目详情成功",
        "detail": serializer.data
    })

@csrf_exempt
@require_POST
@api_exception_handler
def respond_invitation_view(request):
    """
    处理用户对项目邀请的回复（同意/拒绝）。
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    # 验证请求数据
    serializer = RespondInvitationSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    # 调用服务层执行业务逻辑
    services.respond_to_invitation(
        user_id=validated_data['userId'],
        project_id=validated_data['projectId'],
        response_action=validated_data['respond']
    )

    # 返回成功的响应
    return JsonResponse({
        "success": True,
        "message": "操作成功"
    })

@csrf_exempt
@require_POST
@api_exception_handler
def joined_projects_view(request):
    try:
        data = json.loads(request.body)
    except Exception:
        raise BusinessLogicError("请求体格式错误")
    serializer = JoinedProjectRequestSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    user_id = serializer.validated_data['userId']

    projects = get_joined_projects(user_id)
    result = JoinedProjectListSerializer(projects, many=True).data

    return JsonResponse(result, safe=False)


@csrf_exempt
@require_POST
@api_exception_handler
def post_reply_view(request):
    try:
        data = json.loads(request.body)
    except Exception:
        raise BusinessLogicError("请求体格式错误")
    serializer = ProjectReplySerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated = serializer.validated_data

    user = User.objects.get(id=validated['userId'])
    conversation = Conversation.objects.get(conversation_id=validated['projId'], type='project')

    Message.objects.create(
        sender=user,
        receiver=None,
        conversation=conversation,
        content=validated['reply'],
        message_type='group',
        result_id=0
    )

    return JsonResponse({
        "success": True,
        "message": "消息发送成功"
    })

@csrf_exempt
@require_GET
@api_exception_handler
def project_replies_view(request):
    proj_id = request.GET.get('projId')
    if not proj_id:
        raise BusinessLogicError("缺少项目ID (projId) 参数。")
    try:
        proj_id = int(proj_id)
    except Exception:
        raise BusinessLogicError("项目ID格式错误")
    # 查询所有 type=group 的消息
    replies = Message.objects.filter(
        conversation_id=proj_id,
        message_type='group'
    ).select_related('sender').order_by('sent_at')
    data = ProjectReplyListSerializer(replies, many=True).data
    return JsonResponse({
        "success": True,
        "message": "获取成功",
        "replies": data
    })

@csrf_exempt
@require_GET
@api_exception_handler
def question_replies_view(request):
    question_id = request.GET.get('questionId')
    if not question_id:
        raise BusinessLogicError("缺少问题ID (questionId) 参数。")
    try:
        question_id = int(question_id)
    except Exception:
        raise BusinessLogicError("问题ID格式错误")
    # 查询所有 type=forum 的消息
    replies = Message.objects.filter(
        conversation_id=question_id,
        message_type='forum'
    ).select_related('sender').order_by('sent_at')
    data = ProjectReplyListSerializer(replies, many=True).data
    return JsonResponse({
        "success": True,
        "message": "获取成功",
        "replies": data
    })

@csrf_exempt
@require_GET
@api_exception_handler
def question_detail_view(request):
    question_id_str = request.GET.get('questionId')
    if not question_id_str:
        raise BusinessLogicError("缺少问题ID (questionId) 参数。")
    try:
        question_id = int(question_id_str)
    except (ValueError, TypeError):
        raise BusinessLogicError("问题ID (questionId) 格式无效，应为整数。")

    # 查询 type=forum 的讨论
    try:
        question = Conversation.objects.select_related('initiator').get(
            conversation_id=question_id,
            type='forum'
        )
    except Conversation.DoesNotExist:
        raise BusinessLogicError("指定的问题不存在。")

    serializer = ProjectDetailSerializer(question)
    return JsonResponse({
        "success": True,
        "message": "获取问题详情成功",
        "detail": serializer.data
    })



@csrf_exempt
@require_GET
@api_exception_handler
def get_forum(request):
    user_id = request.GET.get('user_id')

    data = services.get_forum(user_id)

    return JsonResponse({
        "message": "获取论坛成功",
        "success": True,
        "data": data
    }, status=200)

@csrf_exempt
@require_POST
@api_exception_handler
def followQuestion(request):
    """
    关注问题
    """
    data = json.loads(request.body)
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    if not user_id or not question_id:
        raise BusinessLogicError("缺少 user_id 或 question_id 参数。")
    
    services.follow_question(user_id, question_id)
    return JsonResponse({
        "message": "关注成功",
        "success": True,
    }, status=200)


@csrf_exempt
@require_POST
@api_exception_handler
def unfollowQuestion(request):
    """
    关注问题
    """
    data = json.loads(request.body)
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    if not user_id or not question_id:
        raise BusinessLogicError("缺少 user_id 或 question_id 参数。")
    
    services.unfollow_question(user_id, question_id)
    return JsonResponse({
        "message": "取关成功",
        "success": True,
    }, status=200)


@csrf_exempt
@require_GET
@api_exception_handler
def project_ai_summary_view(request):
    """
    接收项目ID，返回AI生成的项目总结。
    GET /discussions/projectAI/?project_id=<id>
    """
    project_id_str = request.GET.get('project_id')
    if not project_id_str:
        raise BusinessLogicError("缺少项目ID (project_id) 参数。")

    try:
        project_id = int(project_id_str)
    except (ValueError, TypeError):
        raise BusinessLogicError("项目ID (project_id) 格式无效，应为整数。")

    # 调用服务层生成AI总结
    summary = services.generate_project_summary(project_id=project_id)

    # 返回成功的响应，并按照要求的数据结构封装
    return JsonResponse({
        "success": True,
        "message": "项目AI总结生成成功",
        "data": {
            "summary": summary
        }
    })

@csrf_exempt
@require_POST
@api_exception_handler
def delete_member_view(request):
    """
    接口: 删除项目成员
    POST /discussions/deleteMembers/
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    # 1. 使用序列化器验证请求参数
    serializer = DeleteMemberSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    # 2. 调用服务层执行删除逻辑
    # 注意：这里缺少权限校验，实际项目中应检查 request.user 是否有权限删除成员
    services.delete_project_member(
        project_id=validated_data['projId'],
        user_id_to_delete=validated_data['userId']
    )

    # 3. 返回成功响应
    return JsonResponse({
        "success": True,
        "message": "成员删除成功"
    })