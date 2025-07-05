import json
from functools import wraps
from django.http import JsonResponse
# --- 新增导入 ---
from django.conf import settings

def login_and_owner_required(param_name='userId'):
    """
    一个更强大的自定义装饰器，可以指定要检查的参数名。
    - param_name: 需要与登录用户ID进行比较的请求参数的名称。
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # 检查全局认证开关 (逻辑不变)
            if not getattr(settings, 'ENFORCE_API_AUTH', True):
                return view_func(request, *args, **kwargs)

            # 检查用户是否已登录 (逻辑不变)
            if not request.user.is_authenticated:
                return JsonResponse({
                    "success": False,
                    "message": "用户未登录或登录已过期，请重新登录。"
                }, status=401)

            # 从请求中提取指定参数名的值
            payload_user_id = None
            if request.method == 'GET':
                # --- 修改点：使用传入的 param_name ---
                payload_user_id = request.GET.get(param_name)
            elif request.method == 'POST':
                try:
                    if request.body:
                        data = json.loads(request.body)
                        # --- 修改点：使用传入的 param_name ---
                        payload_user_id = data.get(param_name)
                except json.JSONDecodeError:
                    pass
            
            # 如果请求中包含指定的参数，则进行所有权验证
            if payload_user_id:
                try:
                    if int(payload_user_id) != request.user.id:
                        return JsonResponse({
                            "success": False,
                            "message": "权限不足，您不能访问或操作其他用户的数据。"
                        }, status=403)
                except (ValueError, TypeError):
                     return JsonResponse({
                            "success": False,
                            "message": f"请求中包含的 '{param_name}' 格式无效。"
                        }, status=400)

            # 如果所有检查都通过，则执行原始的视图函数
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator