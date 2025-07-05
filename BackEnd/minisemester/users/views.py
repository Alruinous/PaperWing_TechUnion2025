from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login 
import json

from .services import user_services  # 导入通用用户服务
from .services import user_follow   # 导入关注相关的服务

from .serializers import (
    UserRegisterSerializer, UserLoginSerializer, UserDetailSerializer,
    CheckEmailSerializer, CheckAccountEmailSerializer, UserInfoRequestSerializer, UserFullDetailSerializer,
    UserUpdateSerializer, FollowListSerializer, AuthorOwnershipCheckSerializer, CombinedReadingHistorySerializer
)
from . import services
from utils.decorators import api_exception_handler
from utils.exceptions import BusinessLogicError
from discussions.serializers import ConversationCreateSerializer
from django.core.paginator import Page
# --- 新增导入 ---
from utils.auth_decorators import login_and_owner_required


@csrf_exempt
@require_POST
@api_exception_handler
def register_view(request):
    """
    用户注册接口
    接收 JSON 格式的注册信息，创建新用户。
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    serializer = UserRegisterSerializer(data=data)
    serializer.is_valid(raise_exception=True) # 如果验证失败，异常会被 @api_exception_handler 捕获

    # 调用服务层函数处理业务逻辑
    services.register_user(**serializer.validated_data)

    return JsonResponse({
        "status": "success",
        "message": "注册成功"
    }, status=201)


@csrf_exempt
@require_POST
@api_exception_handler
def login_view(request):
    """
    用户登录接口
    接收账号和密码，验证成功后返回用户信息并建立 session。
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    serializer = UserLoginSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    # 调用服务层进行用户验证
    user = services.login_user(
        request=request,
        **serializer.validated_data
    )

    # 在 Django 中创建 session
    login(request, user)

    # 序列化要返回的用户信息
    response_serializer = UserDetailSerializer(user)
    response_data = {
        "status": "success",
        "message": "登录成功",
        **response_serializer.data
    }

    return JsonResponse(response_data, status=200)


@csrf_exempt
@require_POST
@api_exception_handler
def check_account_or_email_view(request):
    """
    校验账号或邮箱是否已存在。
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    serializer = CheckEmailSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    # 调用服务层进行检查
    exists = services.check_email_exists(**serializer.validated_data)

    return JsonResponse({"exists": exists}, status=200)

@csrf_exempt
@require_POST 
@api_exception_handler

def user_info_view(request):
    """
    查询用户个人科研信息 (GET请求)
    """
    # 2. 修改：从 request.body 读取 JSON 数据
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    # 3. 修改：用解析后的 data 初始化序列化器
    request_serializer = UserInfoRequestSerializer(data=data) 
    request_serializer.is_valid(raise_exception=True)

    # 调用服务层获取用户
    user = services.get_user_info(user_id=request_serializer.validated_data['userId'])

    # 序列化要返回的用户信息
    response_serializer = UserFullDetailSerializer(user)

    # 构建最终的响应结构
    response_data = {
        "status": 200,
        "message": "success",
        "data": response_serializer.data
    }

    return JsonResponse(response_data, status=200)

@csrf_exempt
@require_POST
@api_exception_handler
# --- 使用新版装饰器，参数名为 'user_id' ---
@login_and_owner_required(param_name='user_id')
def update_user_info_view(request):
    """
    根据传入的 userId 更新用户的个人科研信息。
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    # 使用新的序列化器验证数据
    serializer = UserUpdateSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    
    validated_data = serializer.validated_data
    # 从验证过的数据中弹出 userId，因为它将作为独立参数传递
    user_id_to_update = validated_data.pop('userId')

    # 调用服务层更新用户信息
    services.update_user_info(
        user_id=user_id_to_update,
        data=validated_data  # 传递剩余的字段数据
    )

    return JsonResponse({
        "status": "success",
        "message": "用户信息更新成功"
    }, status=200)

@csrf_exempt
@require_GET
@api_exception_handler
def get_messages(request):
    """
    获取首页的推荐信息，报错成果和问题
    """
    user_id = request.GET.get('userId')
    messages = services.get_messages(user_id)

    return JsonResponse({
        "messages": messages,
        "success": True,
        "message": "返回成功"
    }, status=200)


@csrf_exempt
@require_GET
@api_exception_handler
def get_authors(request):
    """
    获取首页的推荐人员
    """
    user_id = request.GET.get('userId')

    authors = services.get_authors(user_id)
    
    return JsonResponse({
        "authors": authors,
        "success": True,
        "message": "返回推荐人员成功"
    }, status=200)

@csrf_exempt
@require_POST
@api_exception_handler
# --- 使用新版装饰器，并传入正确的参数名 ---
@login_and_owner_required(param_name='followerid')
def follow(request):
    """
    关注用户
    """
    data = json.loads(request.body) 
    follower_id = data.get('followerid')
    followee_id = data.get('followeeid')

    services.follow_user(follower_id, followee_id)

    return JsonResponse({
        "success": True,
        "message": "关注成功"
    }, status=200)


@csrf_exempt
@require_POST
@api_exception_handler
# --- 使用新版装饰器，并传入正确的参数名 ---
@login_and_owner_required(param_name='followerid')
def unfollow(request):
    """
    取关用户
    """
    data = json.loads(request.body) 
    follower_id = data.get('followerid')
    followee_id = data.get('followeeid')

    services.unfollow_user(follower_id, followee_id)

    return JsonResponse({
        "success": True,
        "message": "取关成功"
    }, status=200)


@csrf_exempt
@require_POST
@api_exception_handler
def get_followers_view(request):
    """
    获取用户的关注者列表。
    """
    try:
        data = json.loads(request.body)
        user_id = data.get('userId')
        if not user_id:
            raise BusinessLogicError("缺少 userId 参数")
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    followers = user_follow.get_followers_list(user_id)
    serializer = FollowListSerializer(followers, many=True)

    return JsonResponse({
        "status": 200,
        "message": "成功",
        "data": serializer.data
    })


@csrf_exempt
@require_POST
@api_exception_handler
def get_following_view(request):
    """
    获取用户正在关注的用户列表。
    """
    try:
        data = json.loads(request.body)
        user_id = data.get('userId')
        if not user_id:
            raise BusinessLogicError("缺少 userId 参数")
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    following_users = user_follow.get_following_list(user_id)
    serializer = FollowListSerializer(following_users, many=True)

    return JsonResponse({
        "status": 200,
        "message": "成功",
        "data": serializer.data
    })
@csrf_exempt
@require_GET
@api_exception_handler
def searchScholar(request):
    """
    搜索学者
    """
    user_id = request.GET.get('user_id')
    condition = request.GET.get('condition')
    type = request.GET.get('type')

    scholars = services.searchScholar(user_id, condition, type)

    return JsonResponse({
        "data": {
            "scholars": scholars
        },
        "success": True,
        "message": "搜索成功"
    }, status=200)

@csrf_exempt
@require_POST
@api_exception_handler
def check_email_view(request):
    """
    校验邮箱是否已存在。
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    # 使用新的序列化器
    serializer = CheckEmailSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    # 调用新的服务层函数进行检查
    exists = services.check_email_exists(**serializer.validated_data)

    return JsonResponse({"exists": exists}, status=200)

@csrf_exempt
@require_POST
@api_exception_handler
def check_author_ownership_view(request):
    """
    接口: 检查作者列表中是否包含用户本人
    POST /users/check_author_ownership/
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    serializer = AuthorOwnershipCheckSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    # --- 修改这里 ---
    # 将 validated_data 中的键名手动映射到服务层函数的参数名
    is_owner = services.check_author_ownership(
        user_id=validated_data['userId'],
        authors=validated_data['authors']
    )

    if is_owner:
        return JsonResponse({
            "is_owner": True,
            "message": "作者列表中包含本人姓名。"
        })
    else:
        return JsonResponse({
            "is_owner": False,
            "message": "作者列表中不包含本人姓名，请确认。"
        })
    
@csrf_exempt
@require_POST
@api_exception_handler
def get_same_institution_users_view(request):
    """
    获取同机构人员列表。
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    # 使用 UserInfoRequestSerializer 验证 userId
    serializer = UserInfoRequestSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    
    user_id = serializer.validated_data['userId']

    # 调用服务层获取同机构用户列表
    users = services.get_users_from_same_institution(user_id=user_id)

    # 使用 FollowListSerializer 序列化结果，它的字段完全符合要求
    response_serializer = FollowListSerializer(users, many=True)

    return JsonResponse({
        "status": 200,
        "message": "成功",
        "data": response_serializer.data
    })

@csrf_exempt
@require_GET
@api_exception_handler
# --- 使用新版装饰器，并传入正确的参数名 ---
@login_and_owner_required(param_name='userId')
def get_reading_history_view(request):
    """
    接口: 获取综合阅读历史 (全字段版)
    GET /users/reading-history/
    """
    # 1. 获取并验证参数
    user_id = request.GET.get('userId')
    page = request.GET.get('page', '1')
    page_size = request.GET.get('page_size', '10')

    if not user_id:
        raise BusinessLogicError("必须提供 userId 参数。")
    try:
        user_id = int(user_id)
        page = int(page)
        page_size = int(page_size)
        if page_size > 50: # 限制每页最大数量
            page_size = 50
    except (ValueError, TypeError):
        raise BusinessLogicError("参数类型错误。")

    # 2. 调用服务层获取数据
    paginated_data = services.get_combined_reading_history(user_id, page, page_size)

    # 3. 使用新的 CombinedReadingHistorySerializer 序列化结果列表
    serializer = CombinedReadingHistorySerializer(paginated_data['results'], many=True)

    # 4. 构建最终的响应数据结构
    response_data = {
        "total_items": paginated_data['total_items'],
        "total_pages": paginated_data['total_pages'],
        "current_page": paginated_data['current_page'],
        "page_size": paginated_data['page_size'],
        "results": serializer.data
    }

    return JsonResponse({
        "success": True,
        "message": "获取阅读历史成功。",
        "data": response_data
    })


@csrf_exempt
@require_GET
@api_exception_handler
def search_users_by_name_view(request):
    """
    接口: 根据真实姓名和项目ID，模糊搜索用户并返回其在项目中的状态
    GET /users/search/
    """
    # 1. 获取并验证参数
    name_query = request.GET.get('name')
    project_id_str = request.GET.get('projectId')

    if not name_query:
        raise BusinessLogicError("缺少必要参数 name")
    if not project_id_str:
        raise BusinessLogicError("缺少必要参数 projectId")

    try:
        project_id = int(project_id_str)
    except (ValueError, TypeError):
        raise BusinessLogicError("参数 projectId 类型错误，应为整数")

    # 2. 调用服务层执行搜索
    users_found = services.search_users_by_name(
        search_name=name_query,
        project_id=project_id
    )

    # 3. 返回成功响应
    return JsonResponse({
        "success": True,
        "message": "搜索用户成功",
        "data": users_found
    })