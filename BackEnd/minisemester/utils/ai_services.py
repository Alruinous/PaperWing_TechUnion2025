import openai
from django.conf import settings
from .exceptions import BusinessLogicError


def get_ai_response(prompt: str, system_message: str = "You are a helpful assistant.") -> str:
    """
    调用大模型 API 获取响应的通用服务函数。

    Args:
        prompt (str): 用户提供的主要提示或问题。
        system_message (str, optional): 定义 AI 角色的系统消息。默认为 "You are a helpful assistant."。

    Returns:
        str: 从 AI 模型获取的文本响应。

    Raises:
        BusinessLogicError: 如果 API Key 未配置或 API 调用失败。
    """
    if not settings.DASHSCOPE_API_KEY:
        raise BusinessLogicError("AI 服务未配置：缺少 API Key。")

    try:
        client = openai.OpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url=settings.DASHSCOPE_BASE_URL,
        )

        completion = client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': prompt}
            ]
        )

        # 返回模型的最终答案
        return completion.choices[0].message.content

    except openai.APIConnectionError as e:
        # 处理网络连接问题
        raise BusinessLogicError(f"AI 服务连接失败: {e.__cause__}")
    except openai.RateLimitError:
        # 处理达到速率限制的错误
        raise BusinessLogicError("AI 服务请求过于频繁，请稍后再试。")
    except openai.APIStatusError as e:
        # 处理 API 状态错误 (例如 4xx, 5xx)
        raise BusinessLogicError(
            f"AI 服务返回错误状态: {e.status_code}, 响应: {e.response}")
    except Exception as e:
        # 处理其他所有预料之外的错误
        raise BusinessLogicError(f"调用 AI 服务时发生未知错误: {str(e)}")
