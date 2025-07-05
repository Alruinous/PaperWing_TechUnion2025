from django.http import JsonResponse
from rest_framework.exceptions import ValidationError
import json
from .exceptions import BusinessLogicError
import logging  # 1. 导入 logging 模块
from functools import wraps


def api_exception_handler(view_func):
    """
    API 异常处理装饰器。
    捕获视图函数中抛出的各种异常，并返回统一格式的 JSON 响应。
    """
    def wrapper(request, *args, **kwargs):
        try:
            # 执行原始视图函数
            return view_func(request, *args, **kwargs)

        # 捕获业务逻辑错误
        except BusinessLogicError as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

        # 捕获 DRF Serializer 的验证错误
        except ValidationError as e:
            # 从 DRF 的错误字典中提取第一条错误信息
            error_detail = e.detail
            first_key = next(iter(error_detail))
            first_error_message = error_detail[first_key][0]
            message = f"参数错误: {first_error_message}"
            return JsonResponse({"success": False, "message": message}, status=400)

        # 捕获 JSON 解析错误
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "请求体不是有效的JSON格式"}, status=400)

        # 捕获所有其他未知异常
        except Exception as e:
            # 在生产环境中，这里应该记录错误日志
            # logger.error(f"Unhandled exception in {view_func.__name__}: {e}", exc_info=True)
            return JsonResponse({"success": False, "message": f"服务器内部发生未知错误: {str(e)}"}, status=500)

    return wrapper
