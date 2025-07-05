import json
from ..models import AnalysisSubscription, AnalysisReport, Document
from utils.ai_services import get_ai_response
from utils.exceptions import BusinessLogicError
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.template.loader import render_to_string
from utils import report_visualizer
from utils.email_service import send_report_email
import os
from django.conf import settings
import random
import markdown

def _build_report_prompt(keyword: str) -> str:
    """
    构建一个精密的、要求严格 JSON 格式的 Prompt。
    """
    return f"""
你是一位顶级的技术分析师。请针对以下研究领域进行深入的、全球范围内的前沿技术趋势分析："{keyword}"。
你的任务是生成一份包含以下部分的综合报告，并且必须严格按照指定的 JSON 格式返回，不能包含任何额外的解释或文字。

JSON 格式要求如下:
{{
  "report": "string",
  "wordCloudData": [{{ "name": "string", "value": "integer" }}],
  "years": ["string"],
  "topics": ["string"],
  "heatmapData": [["integer", "integer", "float"]],
  "mindMapData": {{ "name": "string", "children": [{{ "name": "string", "children": [{{ "name": "string" }}] }}] }}
}}

具体要求:
1.  **report**: 生成一段约500字的综合性技术趋势分析报告，内容涵盖最新研究进展、主要技术挑战和未来发展方向。
2.  **wordCloudData**: 提取与 "{keyword}" 领域最相关的10个技术热词，并估算它们的热度值（0-100之间）。
3.  **years**: 提供最近4年的年份列表，例如 ["2021", "2022", "2023", "2024"]。
4.  **topics**: 列出与 "{keyword}" 相关的5个主要细分研究方向。
5.  **heatmapData**: 创建一个热力图数据。该数据是一个数组，每个元素是 `[年份索引, 细分方向索引, 热度值]`。热度值是一个0到1之间的小数，表示某一年份在某一细分方向上的研究热度。年份和细分方向的索引与 `years` 和 `topics` 数组的索引一一对应。
6.  **mindMapData**: 创建一个用于生成思维导图的层级数据结构。根节点名称应为 "{keyword}前沿"。包含3-5个一级子节点，每个子节点下再包含2-3个二级子节点，代表该领域的核心技术和概念。

请立即开始分析并严格按照上述 JSON 格式生成报告。
"""

# 原始的虚拟版本


def generate_and_save_report_fake(subscription_id: int) -> AnalysisReport:
    """
    为指定的订阅生成报告并保存到数据库。
    """
    print("我被加固了")
    try:
        subscription = AnalysisSubscription.objects.get(pk=subscription_id)
    except AnalysisSubscription.DoesNotExist:
        raise BusinessLogicError("订阅不存在")

    # 1. 构建并发送 Prompt 给 AI
    prompt = _build_report_prompt(subscription.keyword)
    system_message = "你是一个严格遵循指令的AI助手，只会返回格式化的JSON数据。"

    # 假设 get_ai_response 能够联网并返回一个包含 JSON 的字符串
    ai_response_str = get_ai_response(prompt, system_message)

    # 2. 解析 AI 返回的 JSON 字符串
    try:
        # 清理AI可能返回的Markdown代码块标记
        if ai_response_str.strip().startswith("```json"):
            ai_response_str = ai_response_str.strip()[7:-3]

        report_data = json.loads(ai_response_str)
    except json.JSONDecodeError:
        raise BusinessLogicError("AI未能返回有效的JSON格式报告，请稍后重试。")

    # 3. 创建或更新报告记录
    report, created = AnalysisReport.objects.update_or_create(
        subscription=subscription,
        defaults={'report_data': report_data}
    )

    # --- 新增：生成图片并发送邮件 (与真实数据版本完全相同的逻辑) ---
    wordcloud_path = None
    heatmap_path = None
    mindmap_path = None  # --- 新增：为思维导图路径创建变量 ---
    try:
        # 1. 生成图表图片
        wordcloud_path = report_visualizer.generate_wordcloud_image(
            report_data.get('wordCloudData', []), subscription.user.id
        )
        heatmap_path = report_visualizer.generate_heatmap_image(
            report_data.get('heatmapData', []),
            report_data.get('years', []),
            report_data.get('topics', []),
            subscription.user.id
        )
        # --- 新增：调用思维导图生成函数 ---
        mindmap_path = report_visualizer.generate_mindmap_image(
            report_data.get('mindMapData', {}), subscription.user.id
        )
        # 2. 准备模板上下文
        context = {
            'user_name': subscription.user.name or subscription.user.username,
            'keyword': subscription.keyword,
            'report_text': report_data.get('report', '报告内容生成失败。')
        }
        html_content = render_to_string(
            'emails/tech_report_email.html', context)

        # 3. 准备要嵌入的图片
        images_to_embed = {}
        if wordcloud_path:
            images_to_embed['wordcloud_image'] = wordcloud_path
        if heatmap_path:
            images_to_embed['heatmap_image'] = heatmap_path
         # --- 新增：将思维导图添加到待嵌入列表 ---
        if mindmap_path:
            images_to_embed['mindmap_image'] = mindmap_path

        # 4. 发送邮件
        if subscription.user.email:
            send_report_email(
                subject=f"【PaperWing】您的专属技术速递报告 - {subscription.keyword}",
                to_email=subscription.user.email,
                html_content=html_content,
                images_to_embed=images_to_embed
            )

    except Exception as e:
        print(f"错误：为用户 {subscription.user.email} 生成或发送报告邮件失败: {e}")
    finally:
        # 5. 清理临时生成的图片文件
        if wordcloud_path and os.path.exists(wordcloud_path):
            os.remove(wordcloud_path)
        if heatmap_path and os.path.exists(heatmap_path):
            os.remove(heatmap_path)
            # --- 新增：清理思维导图图片 ---
        if mindmap_path and os.path.exists(mindmap_path):
            os.remove(mindmap_path)
    # --- 邮件发送逻辑结束 ---

    return report


def _calculate_next_run(frequency: str) -> timezone.datetime:
    """
    根据频率计算下一次运行时间。
    """
    now = timezone.now()
    if frequency == 'weekly':
        return now + timedelta(days=7)
    elif frequency == 'monthly':
        return now + timedelta(days=30)
    # 可以根据需要添加更多频率选项，例如 'daily'
    # 默认返回一周后
    return now + timedelta(days=7)


def _get_english_keywords_from_ai(chinese_keyword: str) -> list[str]:
    """
    使用AI将中文领域词转换为相关的英文技术关键词列表。
    """
    prompt = f"""
    我正在进行文献检索。请将以下中文领域词 "{chinese_keyword}" 转换成一个包含5到10个最相关的、具体的英文技术关键词的JSON数组。
    这些关键词应该适合用于在学术数据库（如arXiv）中进行搜索。
    例如，如果输入是“人工智能”，你可能返回 ["Artificial Intelligence", "Machine Learning", "Deep Learning", "Neural Networks", "Computer Vision"]。
    请只返回一个JSON数组，不要包含任何其他解释或文本。
    """
    system_message = "你是一个只返回JSON格式数据的翻译和领域专家助手。"

    response_str = get_ai_response(prompt, system_message)

    try:
        # 清理AI可能返回的Markdown代码块标记
        if response_str.strip().startswith("```json"):
            response_str = response_str.strip()[7:-3]
        keywords = json.loads(response_str)
        if isinstance(keywords, list):
            return keywords
        return []
    except (json.JSONDecodeError, TypeError):
        # 如果AI返回格式不正确，则返回一个基于原始词的简单列表
        return [chinese_keyword]


def _build_real_data_report_prompt(chinese_keyword: str, documents: list[Document]) -> str:
    """
    根据数据库中找到的真实文献构建最终的报告生成Prompt。
    """
    if not documents:
        return f"""
        我进行了一次关于 "{chinese_keyword}" 的文献检索，但在过去一周内我们的数据库中没有找到任何新发表的相关文献。
        请根据这个信息，生成一份报告，告诉用户本周内该领域没有新的文献入库。
        请严格按照以下JSON格式返回，其中'report'字段应包含这个消息：
        {{
          "report": "关于'{chinese_keyword}'领域的报告：本周平台内未发现新的相关文献。",
          "wordCloudData": [],
          "years": [],
          "topics": [],
          "heatmapData": [],
          "mindMapData": {{ "name": "{chinese_keyword}前沿", "children": [] }}
        }}
        """

    # 提取文献信息用于上下文
    context = ""
    for doc in documents[:10]:  # 最多使用10篇文献作为上下文，防止prompt过长
        context += f"- 标题: {doc.title}\n  摘要: {doc.abstract}\n\n"

    # --- 核心修改在这里 (返回Markdown格式) ---
    return f"""
    你是一位顶级的AI技术分析师。
    基于以下关于“{chinese_keyword}”领域的 {len(documents)} 篇文献信息，你的任务是生成一份完整的技术趋势分析报告。

    文献信息摘要：
    ---
    {context}
    ---

    请严格按照下面的JSON格式返回你的分析结果。绝对不能包含任何额外的解释或文字。

    **JSON格式要求:**
    {{
      "report": "string",
      "wordCloudData": [{{ "name": "string", "value": "integer" }}],
      "years": ["string"],
      "topics": ["string"],
      "heatmapData": [["integer", "integer", "float"]],
      "mindMapData": {{ "name": "string", "children": [{{ "name": "string", "children": [{{ "name": "string" }}] }}] }}
    }}

    ---
    **各字段具体生成指令：**

    1.  **`report` (string)**:
        **这是一个关键字段，它必须是一个单一的、包含Markdown格式的完整字符串。**
        请将以下所有标题和内容组织成一个连贯的文本段落，使用Markdown进行格式化（例如，用`###`表示标题，用`*`表示项目符号）。
        
        **报告文本结构模板:**
        ### 2025年第二季度技术趋势分析报告：{chinese_keyword}
        **报告生成时间：** 2025-07-01
        **分析数据源：** 平台内，2025-06-24 至 2025-07-01 期间发表的，关于‘{chinese_keyword}’的 {len(documents)} 篇相关文献。
        
        ### 核心摘要与思维导图
        （在这里撰写一段简要说明，介绍报告目标和思维导图的作用。）
        
        ### 1. 主要发现 (Key Findings)
        * （基于文献内容，详细阐述第一条发现。）
        * （基于文献内容，详细阐述第二条发现。）
        * （...阐述3-5条...）
        
        ### 2. 技术趋势分析 (Technology Trend Analysis)
        （在这里撰写一段详细的趋势分析。）
        
        ### 3. 未来发展预测 (Future Development Prediction)
        * （预测第一个发展方向。）
        * （预测第二个发展方向。）
        * （...预测3-5个...）

        ### 4. 研究启发与建议 (Research Inspiration and Suggestions)
        * （给出第一条建议。）
        * （给出第二条建议。）
        * （...给出3-5条...）

    2.  **`wordCloudData`**: 提取与 "{chinese_keyword}" 领域最相关的10个技术热词，并估算它们的热度值（0-100之间）。
    
    3.  **`years`**: 提供最近4年的年份列表，例如 `["2022", "2023", "2024", "2025"]`。
    
    4.  **`topics`**: 列出与 "{chinese_keyword}" 相关的5个主要细分研究方向。
    
    5.  **`heatmapData`**:
        **这是一个关键字段，格式必须严格遵守。**
        它是一个数组，每个元素都是一个包含三个数字的数组 `[年份索引, 细分方向索引, 热度值]`。
        - `年份索引`: 对应 `years` 数组的索引 (0-3)。
        - `细分方向索引`: 对应 `topics` 数组的索引 (0-4)。
        - `热度值`: 一个0到1之间的浮点数。
        **示例**: `[[0, 0, 0.8], [0, 1, 0.6], [1, 0, 0.9], ...]`

    6.  **`mindMapData`**: 创建一个用于生成思维导图的层级数据结构。根节点名称应为 "{chinese_keyword}前沿"。

    ---
    请立即开始分析并严格按照上述所有指令生成报告。
    """

def _load_field_keyword_map() -> dict:
    """
    从JSON文件加载研究领域到关键词的映射。
    """
    map_path = os.path.join(
        settings.BASE_DIR, 'document', 'field_keyword_map.json')
    try:
        with open(map_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果文件不存在或格式错误，返回空字典
        return {}


def _get_keywords_from_map(user_keyword: str, field_map: dict) -> list[str]:
    """
    根据用户输入的关键词，从映射中智能地获取相关的具体关键词。
    """
    # 1. 直接匹配
    if user_keyword in field_map:
        return field_map[user_keyword]

    # 2. 模糊匹配 (如果直接匹配不到)
    for field, keywords in field_map.items():
        if user_keyword.lower() in field.lower():
            return keywords

    # 3. 如果都匹配不到，返回用户输入的词本身作为最后的尝试
    return [user_keyword]


# # 更新后的正常版本
def generate_and_save_report(subscription_id: int) -> AnalysisReport:
    """
    (真实数据版) 为指定的订阅生成报告，保存到数据库，并更新下一次运行时间。
    """
    try:
        subscription = AnalysisSubscription.objects.get(pk=subscription_id)
    except AnalysisSubscription.DoesNotExist:
        raise BusinessLogicError("订阅不存在")

    # 1. 加载领域-关键词映射
    field_map = _load_field_keyword_map()

    # 2. 从映射中获取用于搜索的关键词列表
    search_keywords = _get_keywords_from_map(subscription.keyword, field_map)

    # 为了防止关键词过多导致查询缓慢或结果过于宽泛，可以随机选择一部分
    if len(search_keywords) > 20:
        search_keywords = random.sample(search_keywords, 20)

    # 3. 使用关键词在数据库中搜索最近一周的文献
    one_week_ago = timezone.now() - timedelta(days=7)
    query = Q()
    for kw in search_keywords:
        # 搜索标题、摘要、或数据库中的关键词字段
        query |= Q(title__icontains=kw) | Q(
            abstract__icontains=kw) | Q(keywords__icontains=kw)

    relevant_documents = Document.objects.filter(
        query, created_at__gte=one_week_ago).distinct()

    # 4. 构建并发送最终的Prompt给AI
    prompt = _build_real_data_report_prompt(
        subscription.keyword, list(relevant_documents))
    system_message = "你是一个严格遵循指令的AI助手，只会返回格式化的JSON数据。"
    ai_response_str = get_ai_response(prompt, system_message)

    # 5. 解析并保存报告
    try:
        if ai_response_str.strip().startswith("```json"):
            ai_response_str = ai_response_str.strip()[7:-3]
        report_data = json.loads(ai_response_str)
    except json.JSONDecodeError:
        raise BusinessLogicError("AI未能返回有效的JSON格式报告，请稍后重试。")

    report, created = AnalysisReport.objects.update_or_create(
        subscription=subscription,
        defaults={'report_data': report_data, 'generated_at': timezone.now()}
    )

    # 6. 更新订阅的下一次运行时间
    subscription.next_run_at = _calculate_next_run(subscription.frequency)
    subscription.save(update_fields=['next_run_at'])

    # --- 新增：生成图片并发送邮件 (与真实数据版本完全相同的逻辑) ---
    wordcloud_path = None
    heatmap_path = None
    mindmap_path = None  # --- 新增：为思维导图路径创建变量 ---
    try:
        # 1. 生成图表图片
        wordcloud_path = report_visualizer.generate_wordcloud_image(
            report_data.get('wordCloudData', []), subscription.user.id
        )
        heatmap_path = report_visualizer.generate_heatmap_image(
            report_data.get('heatmapData', []),
            report_data.get('years', []),
            report_data.get('topics', []),
            subscription.user.id
        )
        # --- 新增：调用思维导图生成函数 ---
        mindmap_path = report_visualizer.generate_mindmap_image(
            report_data.get('mindMapData', {}), subscription.user.id
        )

         # --- 关键修改：转换 Markdown 为 HTML ---
        # 1. 从AI响应中获取原始的Markdown报告文本
        markdown_report_text = report_data.get('report', '报告内容生成失败。')
        # 2. 使用 markdown 库将其转换为 HTML
        html_report_text = markdown.markdown(markdown_report_text, extensions=['fenced_code', 'tables'])
        # 2. 准备模板上下文
        context = {
            'user_name': subscription.user.name or subscription.user.username,
            'keyword': subscription.keyword,
            'report_text': html_report_text # <-- 使用转换后的HTML
        }
        html_content = render_to_string(
            'emails/tech_report_email.html', context)

        # 3. 准备要嵌入的图片
        images_to_embed = {}
        if wordcloud_path:
            images_to_embed['wordcloud_image'] = wordcloud_path
        if heatmap_path:
            images_to_embed['heatmap_image'] = heatmap_path
         # --- 新增：将思维导图添加到待嵌入列表 ---
        if mindmap_path:
            images_to_embed['mindmap_image'] = mindmap_path

        # 4. 发送邮件
        print("我被加固了新")
        if subscription.user.email:
            send_report_email(
                subject=f"【PaperWing】您的专属技术速递报告 - {subscription.keyword}",
                to_email=subscription.user.email,
                html_content=html_content,
                images_to_embed=images_to_embed
            )
        print("加固完成了哦亲")

    except Exception as e:
        print(f"错误：为用户 {subscription.user.email} 生成或发送报告邮件失败: {e}")
    finally:
        # 5. 清理临时生成的图片文件
        if wordcloud_path and os.path.exists(wordcloud_path):
            os.remove(wordcloud_path)
        if heatmap_path and os.path.exists(heatmap_path):
            os.remove(heatmap_path)
            # --- 新增：清理思维导图图片 ---
        if mindmap_path and os.path.exists(mindmap_path):
            os.remove(mindmap_path)
    # --- 邮件发送逻辑结束 ---

    return report
