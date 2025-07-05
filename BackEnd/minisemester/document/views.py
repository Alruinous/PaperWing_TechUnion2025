import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_GET
from .serializers import DocumentUploadSerializer, AISummarySerializer, DocumentDuplicateCheckSerializer, DocumentReadingHistoryCreateSerializer
from .models import Document
# --- 新增导入 ---
from utils.auth_decorators import login_and_owner_required

from utils.decorators import api_exception_handler
from utils.exceptions import BusinessLogicError
from . import services
from .serializers import DocumentUploadSerializer
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json
from django.http import JsonResponse
from utils.decorators import api_exception_handler
from .services import ai_document_services

from .services import subscription_services, report_generation_services
from .serializers import AnalysisSubscriptionSerializer, AnalysisReportSerializer
from .models import AnalysisSubscription, AnalysisReport


@csrf_exempt
@require_POST
@api_exception_handler
def getCollection(request):
    """
    获取文献库内容
    """
    data = json.loads(request.body)
    user_id = data.get("userId")
    return_data = services.getCollection(user_id)

    return JsonResponse({
        "success": True,
        "data": return_data,
        "message": "返回推荐人员成功"
    }, status=200)
    
@csrf_exempt
@require_POST
@api_exception_handler
def upload_document_view(request):
    """
    接口: 上传文献
    POST /documents/upload/
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    # 使用序列化器验证请求数据
    serializer = DocumentUploadSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    # 调用服务层执行业务逻辑
    new_document = services.upload_new_document(**validated_data)

    # 返回成功的响应
    return JsonResponse({
        "success": True,
        "message": "文献上传成功。",
        "data": {
            "doc_id": new_document.doc_id
        }
    }, status=201) # 使用 201 Created 状态码表示资源创建成功

# Create your views here.
@csrf_exempt
@require_GET
@api_exception_handler
def check_duplicate_view(request):
    """
    接口: 检查文献标题是否重复
    GET /documents/check_duplicate/
    """
    # 使用序列化器验证GET请求的参数
    serializer = DocumentDuplicateCheckSerializer(data=request.GET)
    serializer.is_valid(raise_exception=True)
    title_to_check = serializer.validated_data['title']

    # 执行不区分大小写的查询
    is_exists = Document.objects.filter(title__iexact=title_to_check).exists()

    if is_exists:
        return JsonResponse({
            "exists": True,
            "message": "已存在相同标题的文献记录"
        })
    else:
        return JsonResponse({
            "exists": False,
            "message": "文献标题可用"
        })


@csrf_exempt
@require_GET
@api_exception_handler
def generate_ai_summary_view(request):
    """
    AI 摘要生成接口视图。
    接收 GET 请求中的 doc_id 参数。
    """
    doc_id = request.GET.get('doc_id')
    if not doc_id:
        raise BusinessLogicError("缺少 doc_id 参数")

    try:
        doc_id = int(doc_id)
    except (ValueError, TypeError):
        raise BusinessLogicError("doc_id 参数必须是有效的整数")

    # 调用服务层获取 AI 生成的摘要
    summary_data = ai_document_services.generate_summary_for_document(doc_id)

    # 使用序列化器格式化数据
    serializer = AISummarySerializer(data=summary_data)
    serializer.is_valid(raise_exception=True)  # 确保数据有效

    # 按照您要求的格式返回 JSON 响应
    return JsonResponse({
        "success": True,
        "message": "AI摘要生成成功",
        "data": serializer.data  # 这里的 data 是 {"summary": "..."}
    })

@csrf_exempt
@require_POST
@api_exception_handler
# --- 使用新版装饰器，参数名为 'user_id' ---
@login_and_owner_required(param_name='userId')
def add_reading_history_view(request):
    """
    接口: 添加文献阅读历史
    POST /documents/add_reading_history/
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise BusinessLogicError("无效的JSON格式")

    serializer = DocumentReadingHistoryCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    services.add_document_reading_history(
        user_id=validated_data['userId'],
        document_id=validated_data['documentId']
    )

    return JsonResponse({
        "success": True,
        "message": "阅读历史已记录。"
    })


@csrf_exempt
@require_POST
@api_exception_handler
def manage_subscription_view(request):
    """
    创建或更新技术速递订阅。
    """
    data = json.loads(request.body)
    serializer = AnalysisSubscriptionSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    validated_data = serializer.validated_data
    subscription_services.create_or_update_subscription(
        user_id=validated_data['userId'],
        keyword=validated_data['keyword'],
        frequency=validated_data['frequency']
    )

    return JsonResponse({"success": True, "message": "订阅成功，您的专属报告已生成！"})


@csrf_exempt
@require_GET
@api_exception_handler
def get_analysis_report_view(request):
    """
    获取当前用户的最新技术速递报告。
    """
    user_id = request.GET.get('userId')  # 假设前端会传来 userId
    if not user_id:
        raise BusinessLogicError("缺少 userId 参数")

    try:
        # 找到该用户的最新一份报告
        report = AnalysisReport.objects.filter(
            subscription__user_id=user_id).latest('generated_at')
        serializer = AnalysisReportSerializer(instance=report.report_data)
        return JsonResponse({
            "data": serializer.data,
            "success": True,
            "message": "报告获取成功"
        })
    except AnalysisReport.DoesNotExist:
        raise BusinessLogicError("尚未生成任何报告")


@csrf_exempt
@require_GET
@api_exception_handler
def check_report_status_view(request):
    """
    检查用户是否有可用的技术报告。
    """
    user_id = request.GET.get('userId')
    if not user_id:
        raise BusinessLogicError("缺少 userId 参数")

    is_generated = AnalysisReport.objects.filter(
        subscription__user_id=user_id).exists()

    return JsonResponse({
        "isGenerated": is_generated,
        "success": True,
        "message": "状态查询成功"
    })

# --- 开发阶段使用的手动触发接口 ---


@csrf_exempt
@require_POST
@api_exception_handler
def trigger_manual_report_generation_view(request):
    """
    手动触发为指定订阅生成报告，用于开发和测试。
    """
    data = json.loads(request.body)
    subscription_id = data.get('subscription_id')
    if not subscription_id:
        raise BusinessLogicError("缺少 subscription_id")

    report = report_generation_services.generate_and_save_report(
        subscription_id)
    serializer = AnalysisReportSerializer(instance=report.report_data)

    return JsonResponse({
        "success": True,
        "message": "报告已手动生成并保存",
        "data": serializer.data
    })

@csrf_exempt
@require_POST
@api_exception_handler
def get_favorite_category(request):
    """
    获取document某个用户的收藏夹的所有种类
    """
    data = json.loads(request.body)
    user_id = data.get("userId")

    return_data = services.get_favorite_category(user_id)

    return JsonResponse({
        "success": True,
        "message": "返回成功",
        "data": return_data
    }, status=200)


@csrf_exempt
@require_POST
@api_exception_handler
def add_favorite_category(request):
    """
    新建一个用户document收藏夹种类
    """
    data = json.loads(request.body)
    user_id = data.get("userId")
    new_category = data.get("newCategory")

    services.add_favorite_category(user_id, new_category)

    return JsonResponse({
        "success": True,
        "message": "分类添加成功",
    }, status=200)

@csrf_exempt
@require_POST
@api_exception_handler
def get_all_docs(request):
    """
    获取所有收藏的文档
    """
    data = json.loads(request.body)
    user_id = data.get("userId")
    return_data = services.get_all_docs(user_id)

    return JsonResponse({
        "success": True,
        "message": "返回所有文档成功",
        "data": return_data
    }, status=200)

@csrf_exempt
@require_POST
@api_exception_handler
def addFavorite(request):
    """
    添加文档到收藏夹
    """
    data = json.loads(request.body)
    user_id = data.get("userId")
    doc_id = data.get("docId")

    services.add_favorite(user_id, doc_id)

    return JsonResponse({
        "success": True,
        "message": "文档已添加到收藏夹"
    }, status=200)


@csrf_exempt
@require_POST
@api_exception_handler
def update_category(request):
    """
    更新收藏夹分类名称
    """
    data = json.loads(request.body)
    user_id = data.get("userId")
    doc_id = data.get("docId")
    new_categories = data.get("newCategory")

    services.update_category(user_id, doc_id, new_categories)

    return JsonResponse({
        "success": True,
        "message": "分类更新成功"
    }, status=200)