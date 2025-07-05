import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from email.mime.image import MIMEImage
import os

# 获取日志记录器，方便排查问题
logger = logging.getLogger(__name__)

def send_custom_email(subject: str, message: str, recipient_list: list):
    """
    通用的邮件发送函数。
    """
    if not recipient_list:
        logger.warning("邮件发送被跳过：收件人列表为空。")
        return False
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,  # 确保发送失败时会抛出异常
        )
        logger.info(f"邮件成功发送至: {recipient_list}")
        return True
    except Exception as e:
        logger.error(f"邮件发送失败至 {recipient_list}. 错误: {e}", exc_info=True)
        return False

def send_report_email(subject: str, to_email: str, html_content: str, images_to_embed: dict):
    """
    发送带内嵌图片的 HTML 邮件。
    images_to_embed 的格式: {'cid_name': '/path/to/image.png'}
    cid_name 必须与 HTML 模板中的 <img src="cid:..."> 对应。
    """
    try:
        # 创建邮件对象，同时提供纯文本备用内容
        plain_text_content = "您的邮件客户端不支持HTML格式，请在网页版查看报告。"
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.mixed_subtype = 'related' # 关键：告诉邮件客户端这是内嵌资源的邮件

        # 嵌入图片
        for cid, img_path in images_to_embed.items():
            if not img_path or not os.path.exists(img_path):
                continue
            with open(img_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', f'<{cid}>') # 设置 Content-ID
                msg.attach(img)
        
        msg.send()
        logger.info(f"报告邮件成功发送至: {to_email}")
        return True
    except Exception as e:
        logger.error(f"报告邮件发送失败至 {to_email}. 错误: {e}", exc_info=True)
        return False