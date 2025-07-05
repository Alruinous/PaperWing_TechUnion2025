import pdfplumber
from ..models import Document
from utils.exceptions import BusinessLogicError
from utils.ai_services import get_ai_response
import os
from django.conf import settings

def _extract_text_from_pdf(pdf_path: str) -> str:
    """
    从给定的本地 PDF 文件路径中提取文本。
    私有函数，仅供本模块内部使用。
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # 拼接所有页面的文本
            full_text = "".join(page.extract_text()
                                or "" for page in pdf.pages)
        return full_text
    except FileNotFoundError:
        raise BusinessLogicError(f"服务器上未找到文件：{pdf_path}")
    except Exception as e:
        # 捕获 pdfplumber 可能出现的其他解析错误
        raise BusinessLogicError(f"解析PDF文件时出错: {str(e)}")


def generate_summary_for_document(doc_id: int) -> dict:
    """
    为指定的文献生成 AI 摘要。
    """
    # 1. 从数据库获取文献对象
    try:
        document = Document.objects.get(doc_id=doc_id)
    except Document.DoesNotExist:
        raise BusinessLogicError("文献不存在")

    # 2. 检查文件路径是否存在
    if not document.local_file_path:
        raise BusinessLogicError("该文献没有关联的PDF文件")

    rel_path = document.local_file_path
    if rel_path.startswith('/media/'):
        rel_path = rel_path[len('/media/'):]
    abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
    # 3. 提取 PDF 文本
    # 注意：为了性能和避免超出 token 限制，我们只取前 4000 个字符
    document_text = _extract_text_from_pdf(abs_path)
    if not document_text.strip():
        raise BusinessLogicError("PDF 内容为空或无法解析")

    truncated_text = document_text[:4000]

    # 4. 构建 Prompt 并调用 AI 服务
    prompt = f"请为以下学术论文内容生成一段简洁、专业的摘要，不超过300字。论文内容如下：\n\n---\n\n{truncated_text}"
    system_message = "你是一个专业的学术助手，擅长对科研论文进行总结和提炼核心内容。"

    ai_summary = get_ai_response(prompt, system_message)

    # 5. 返回包含摘要的字典
    return {"summary": ai_summary}
