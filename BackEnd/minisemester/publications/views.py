from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json
import traceback
# --- 新增导入 ---
from utils.auth_decorators import login_and_owner_required

# 导入我们项目中的相关模块
from . import services
from .serializers import ClaimOwnershipCheckSerializer, PublicationCreateSerializer, PublicationUploadFullTextSerializer, PublicationCommentCreateSerializer, PublicationLikeSerializer, PublicationDetailSerializer, CommentSerializer, PublicationDuplicateCheckSerializer, UserPublicationRequestSerializer, PublicationListSerializer
from .services import get_user_publications
from utils.decorators import api_exception_handler
from utils.exceptions import BusinessLogicError

from .serializers import RespondClaimSerializer, PublicationNotificationSerializer, ReadingHistoryCreateSerializer, SearchQuerySerializer, PublicationSearchResultSerializer
from .services import respond_to_publication_claim, check_claim_ownership, add_publication_reading_history, search_publications, generate_search_summary


@csrf_exempt
@require_POST
@api_exception_handler
def respond_claim_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    serializer = RespondClaimSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated = serializer.validated_data

    respond_to_publication_claim(
        publication_id=validated['publicationId'],
        claimer_id=validated['claimerId'],
        approver_id=validated['approverId'],
        message_id=validated['messageId'],
        response_action=validated['response']
    )

    return JsonResponse({
        "success": True,
        "message": "操作成功。"
    })


@csrf_exempt
@require_POST
@api_exception_handler
def upload_publication_file_view(request):
    """
    接口1: 上传文件到服务器，并返回其可访问的 URL 路径。
    接收 multipart/form-data 请求。
    """
    # 2. 获取上传的文件
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        raise BusinessLogicError("未找到上传的文件，请确保请求中包含名为 'file' 的文件。")

    # 3. 调用服务层处理文件上传，获取返回的 URL 路径
    file_path_url = services.handle_file_upload(uploaded_file)

    # 4. 返回成功响应
    return JsonResponse({
        "status": "success",
        "file_path": file_path_url
    })


@csrf_exempt
@require_POST
@api_exception_handler
def create_publication_view(request):
    """
    接口2: 创建科研成果的元数据记录 (不安全版本，依赖前端传入 created_by)。
    接收 application/json 请求。
    """
    # 1. 移除身份验证
    # if not request.user.is_authenticated:
    #     raise BusinessLogicError("用户未登录，请先登录")

    # 2. 解析请求体中的 JSON 数据

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    # 3. 使用序列化器验证数据 (序列化器现在会验证 created_by)
    serializer = PublicationCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    # 4. 调用服务层创建成果记录 (不再传入 request.user)
    services.create_publication(serializer.validated_data)

    # 5. 返回成功响应
    return JsonResponse({
        "status": "success",
        "message": "科研成果创建成功"
    })


@csrf_exempt
@require_POST
@api_exception_handler
def create_publication_comment_view(request):
    """
    接口: 创建科研成果评论
    """
    '''
    # 1. 身份验证
    if not request.user.is_authenticated:
        raise BusinessLogicError("用户未登录，请先登录")
    '''

    # 2. 解析请求数据
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON数据")

    # 3. 数据验证
    serializer = PublicationCommentCreateSerializer(data=data)
    if not serializer.is_valid():
        raise BusinessLogicError(serializer.errors)

    '''
    # 4. 检查用户ID是否匹配当前登录用户
    if request.user.id != data['user_id']:
        raise BusinessLogicError("用户ID不匹配")
    '''

    # 5. 调用服务层处理评论创建
    result = services.handle_comment_creation(serializer.validated_data)

    # 6. 返回响应
    return JsonResponse({
        "success": result["success"],
        "message": result["message"]
    })


@csrf_exempt
@require_POST
@api_exception_handler
# --- 使用新版装饰器，参数名为 'user_id' ---
@login_and_owner_required(param_name='user_id')
def like_publication_view(request):
    """
    用户给成果点赞
    """
    '''
    # 1. 身份验证
    if not request.user.is_authenticated:
        raise BusinessLogicError("用户未登录，请先登录")
    '''

    # 2. 解析请求数据
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON数据")

    # 3. 数据验证
    serializer = PublicationLikeSerializer(data=data)
    if not serializer.is_valid():
        raise BusinessLogicError(serializer.errors)

    '''
    # 4. 检查用户ID是否匹配当前登录用户
    if request.user.id != data['user_id']:
        raise BusinessLogicError("用户ID不匹配")
    '''

    # 5. 调用服务层处理成果点赞
    result = services.handle_publication_like_action(serializer.validated_data)

    # 6. 返回响应
    return JsonResponse({
        "success": result["success"],
        "message": result["message"],
        "publication_title": result["publication_title"],
        "username": result["username"]
    })


@csrf_exempt
@require_GET
@api_exception_handler
def get_publication_detail_view(request):
    try:  # <-- 添加 try
        '''
        # 1. 身份验证
        if not request.user.is_authenticated:
            raise BusinessLogicError("用户未登录，请先登录")
        '''

        # 2. 获取查询参数
        pub_id = request.GET.get('pub_id')
        user_id = request.GET.get('user_id')

        # 3. 参数验证
        if not pub_id or not user_id:
            raise BusinessLogicError("缺少必要参数: pub_id 和 user_id")

        # 4. 检查用户ID是否匹配当前登录用户
        '''
        if request.user.id != user_id:
            raise BusinessLogicError("用户ID不匹配")
        '''

        # 5. 调用服务层获取成果详情
        result = services.get_publication_detail(pub_id, user_id)

        # 6. 序列化数据
        serialized_response = PublicationDetailSerializer(data=result)
        if not serialized_response.is_valid():
            # 打印详细的序列化错误
            print("序列化错误:", serialized_response.errors)
            raise BusinessLogicError("数据序列化失败")

        # 7. 返回响应
        return JsonResponse({
            "success": True,  # 这里应该总是 True，因为失败的情况已经被异常捕获
            "data": serialized_response.data  # 使用 .data 获取序列化后的数据
        })
    except Exception as e:  # <-- 添加 except
        # 打印完整的错误追溯到控制台
        traceback.print_exc()
        # 返回一个通用的500错误响应
        return JsonResponse({"success": False, "message": f"服务器内部错误: {str(e)}"}, status=500)


@require_GET
@api_exception_handler
def get_publication_comments_view(request):
    """
    接口: 获取科研成果评论列表
    接收 GET 请求，查询参数为 pub_id
    """
    # 1. 身份验证
    '''
    if not request.user.is_authenticated:
        raise BusinessLogicError("用户未登录，请先登录")'''

    # 2. 获取查询参数
    pub_id = request.GET.get('pub_id')

    # 3. 参数验证
    if not pub_id:
        raise BusinessLogicError("缺少必要参数: pub_id")

    # 4. 调用服务层获取成果详情
    result = services.get_publication_comments(pub_id)

    # 5. 返回响应
    if not result.get("error"):
        return JsonResponse(result)
    else:
        return JsonResponse(result, status=404)


@csrf_exempt
@require_GET
@api_exception_handler
def check_duplicate_view(request):
    """
    接口: 检查文献重复性
    GET /publications/check_duplicate/
    """
    # 使用序列化器验证 Query 参数
    serializer = PublicationDuplicateCheckSerializer(data=request.GET)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    title = validated_data.get('title')
    user_id = validated_data.get('created_by')

    # 调用服务层执行检查
    is_duplicate = services.check_publication_duplicate(
        title=title, user_id=user_id)

    if is_duplicate:
        return JsonResponse({
            "exists": True,
            "message": "该用户已存在相同标题的文献记录"
        })
    else:
        return JsonResponse({
            "exists": False,
            "message": "未发现重复记录"
        })


@csrf_exempt
@require_POST
@api_exception_handler
def user_publication_view(request):
    try:
        data = json.loads(request.body)
    except Exception:
        raise BusinessLogicError("请求体格式错误")
    serializer = UserPublicationRequestSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    user_id = serializer.validated_data['userId']

    publications = get_user_publications(user_id)
    pub_list = PublicationListSerializer(publications, many=True).data

    return JsonResponse({
        "success": True,
        "data": {"publications": pub_list},
        "message": "查询成功"
    })


@csrf_exempt
@require_POST
@api_exception_handler
# --- 使用新版装饰器，参数名为 'user_id' ---
@login_and_owner_required(param_name='user_id')
def cancelfavor(request):
    """
    取消成果点赞
    """
    '''
    # 1. 身份验证
    if not request.user.is_authenticated:
        raise BusinessLogicError("用户未登录，请先登录")
    '''

    # 2. 解析请求数据
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON数据")

    user_id = data.get('user_id')
    pub_id = data.get('pub_id')

    services.cancel_favour(pub_id=pub_id, user_id=user_id)

    return JsonResponse({
        "success": True,
        "message": "取消点赞成功"
    })


@csrf_exempt
@require_POST
@api_exception_handler
def check_claim_ownership_view(request):
    """
    接口: 检查成果认领归属
    POST /publications/check_claim_ownership/
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    serializer = ClaimOwnershipCheckSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    # --- 修改这里 ---
    # 将 validated_data 中的键名手动映射到服务层函数的参数名
    is_owner = check_claim_ownership(
        publication_id=validated_data['publicationId'],
        user_id=validated_data['userId']
    )

    if is_owner:
        return JsonResponse({
            "is_owner": True,
            "message": "您的姓名存在于该成果的作者列表中。"
        })
    else:
        return JsonResponse({
            "is_owner": False,
            "message": "您的姓名不在该成果的作者列表中，请确认。"
        })


@csrf_exempt
@require_POST
@api_exception_handler
def send_email_to_followers_view(request):
    """
    接口: 发布成果后给粉丝发邮件
    POST /publications/sendemail/
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    serializer = PublicationNotificationSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    message = services.notify_followers_by_email(
        user_id=validated_data['userId'],
        notification_type=validated_data['type'],
        number=validated_data['number']
    )

    return JsonResponse({
        "success": True,
        "message": message
    })


@csrf_exempt
@require_POST
@api_exception_handler
# --- 使用新版装饰器，参数名为 'user_id' ---
@login_and_owner_required(param_name='userId')
def add_reading_history_view(request):
    """
    接口: 添加成果阅读历史
    POST /publications/add_reading_history/
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    serializer = ReadingHistoryCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    add_publication_reading_history(
        user_id=validated_data['userId'],
        publication_id=validated_data['publicationId']
    )

    return JsonResponse({
        "success": True,
        "message": "阅读历史已记录。"
    })


# @csrf_exempt
# @require_GET
# @api_exception_handler
# def search_publications_view(request):
#     """
#     接口: 搜索科研成果并返回 AI 总结
#     GET /publications/search/
#     """
#     # 1. 使用序列化器验证查询参数
#     query_serializer = SearchQuerySerializer(data=request.GET)
#     query_serializer.is_valid(raise_exception=True)
#     validated_query = query_serializer.validated_data

#     # 2. 调用服务层执行搜索和 AI 总结
#     search_result = services.search_and_summarize_publications(
#         user_id=validated_query.get('user_id'),
#         condition=validated_query.get('condition', ''),
#         pub_type=validated_query.get('type', '')
#     )

#     # 3. 直接返回服务层处理好的结果
#     return JsonResponse({
#         "success": True,
#         "message": "搜索成功",
#         "data": search_result  # 直接使用 search_result
#     })


@csrf_exempt
@require_GET
@api_exception_handler
def search_publications_view(request):
    """
    接口: 搜索科研成果 (不含AI总结)
    GET /publications/search/
    """
    # 1. 使用序列化器验证查询参数
    query_serializer = SearchQuerySerializer(data=request.GET)
    query_serializer.is_valid(raise_exception=True)
    validated_query = query_serializer.validated_data

    # 2. 调用服务层执行纯搜索
    publications_list = search_publications(
        user_id=validated_query.get('user_id'),
        condition=validated_query.get('condition', ''),
        pub_type=validated_query.get('type', '')
    )

    # 3. 直接返回服务层处理好的结果
    return JsonResponse({
        "success": True,
        "message": "搜索成功",
        "data": {
            "publications": publications_list
        }
    })


@csrf_exempt
@require_GET
@api_exception_handler
def search_ai_summary_view(request):
    """
    接口: 对搜索结果进行 AI 总结
    GET /publications/searchAI/
    """
    # 1. 使用序列化器验证查询参数 (复用SearchQuerySerializer)
    # 注意：user_id 和 number 在此接口的AI总结部分不是必需的，但为了验证其他参数，我们仍然使用它
    query_serializer = SearchQuerySerializer(data=request.GET)
    query_serializer.is_valid(raise_exception=True)
    validated_query = query_serializer.validated_data

    # 2. 调用服务层生成AI总结
    conclusion = generate_search_summary(
        condition=validated_query.get('condition', ''),
        pub_type=validated_query.get('type', '')
    )

    # 3. 返回AI总结结果
    return JsonResponse({
        "success": True,
        "message": "AI总结生成成功",
        "data": {
            "conclusion": conclusion
        }
    })

# --- 新增视图函数 ---
@csrf_exempt
@require_POST
@api_exception_handler
def upload_full_text_view(request):
    """
    接口: 更新成果的全文链接 (local_file_path)。
    POST /publication/uploadFullText/
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    serializer = PublicationUploadFullTextSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    services.update_publication_local_file_path(
        pub_id=validated_data['pub_id'],
        url=validated_data['url']
    )

    return JsonResponse({
        "success": True,
        "message": "成果全文链接更新成功。"
    })

@csrf_exempt
@require_GET
@api_exception_handler
def get_recommended_publications_view(request):
    # 1. 获取查询参数
    user_id = request.GET.get('userId')
    pub_type = request.GET.get('type')

    # 2. 参数验证
    if not user_id:
        raise BusinessLogicError("缺少必要参数: userId")
    if not pub_type:
        raise BusinessLogicError("缺少必要参数: type")

    try:
        user_id = int(user_id)
    except ValueError:
        raise BusinessLogicError("参数类型错误: userId必须为整数")

    # 3. 调用服务层获取成果列表
    result = services.get_recommended_publications(user_id, pub_type)

    # 4. 返回响应
    if result.get("success"):
        return JsonResponse(result)
    else:
        return JsonResponse(result, status=404)