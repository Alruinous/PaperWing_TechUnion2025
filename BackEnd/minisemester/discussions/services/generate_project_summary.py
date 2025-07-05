from ..models import Conversation, Message
from utils.exceptions import BusinessLogicError
from utils.ai_services import get_ai_response


def _build_project_summary_prompt_cn(project_title: str, messages: list) -> str:
    """
    构建用于AI总结项目讨论的中文Prompt。
    """
    if not messages:
        return f"项目 '{project_title}' 尚无讨论记录。请生成一条消息说明此情况。"

    # 格式化聊天记录
    chat_history = "\n".join(
        [f"[{msg.sent_at.strftime('%Y-%m-%d %H:%M')}] {msg.sender.name if msg.sender else '系统'}: {msg.content}" for msg in messages]
    )

    prompt = f"""
你是一位专业的项目管理助理。以下是项目“{project_title}”的讨论记录。请分析这些记录并提供一份简洁的摘要报告，报告应包含以下几个部分，并以一个完整的文本块返回：

1.  **总体摘要**：简要概述讨论的主要目标、进展和当前状态。
2.  **关键议题**：用项目符号（-）列出讨论中涉及的主要主题或问题。
3.  **行动项与决策**：列出已确定的任务、做出的决策，并提及负责人（如果记录中有）。
4.  **潜在风险**：识别出的任何潜在风险或障碍。

这是聊天记录：
---
{chat_history}
---

请立即生成摘要报告。
"""
    return prompt


def generate_project_summary(project_id: int) -> str:
    """
    获取项目讨论历史并使用AI生成总结报告。
    """
    try:
        project = Conversation.objects.get(
            conversation_id=project_id, type='project')
    except Conversation.DoesNotExist:
        raise BusinessLogicError("指定的项目不存在。")

    # 获取项目的所有群组消息，按时间排序
    messages = Message.objects.filter(
        conversation=project,
        message_type='group'
    ).select_related('sender').order_by('sent_at')

    # 构建中文Prompt
    prompt = _build_project_summary_prompt_cn(project.title, list(messages))

    # 调用AI服务获取总结
    summary = get_ai_response(prompt, "你是一位高效专业的项目管理助理。")

    return summary
