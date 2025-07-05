import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import os
from django.conf import settings
import pandas as pd
import time
import numpy as np # 引入 numpy 用于创建圆形遮罩
# --- 新增：从 matplotlib 导入字体管理器 ---
from matplotlib.font_manager import FontProperties
# --- 新增：导入 graphviz 库 ---
import graphviz
import numpy as np # 引入 numpy 用于创建圆形遮罩
# --- 新增：从 matplotlib 导入字体管理器 ---
from matplotlib.font_manager import FontProperties

# --- 关键修改：不再依赖 rcParams 的自动寻找，因为服务器上可能失败 ---
# 我们将直接在绘图函数中指定字体路径。
# 这是在 Ubuntu 上通过 apt-get 安装后的标准路径。
UBUNTU_FONT_PATH = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'

# --- 新增：创建一个可重用的字体属性对象 ---
# 我们检查字体文件是否存在，如果存在则加载，否则此对象为 None
try:
    font_prop = FontProperties(fname=UBUNTU_FONT_PATH)
except FileNotFoundError:
    font_prop = None

def _get_output_filepath(user_id: int, chart_type: str) -> str:
    output_dir = os.path.join(settings.MEDIA_ROOT, 'report_images')
    os.makedirs(output_dir, exist_ok=True)
    timestamp = int(time.time())
    return os.path.join(output_dir, f'{chart_type}_{user_id}_{timestamp}.png')

def generate_wordcloud_image(word_data: list, user_id: int) -> str:
    """根据词频数据生成词云图，模仿 ECharts 样式。"""
    freq_dict = {item['name']: item['value'] for item in word_data if 'name' in item and 'value' in item}
    if not freq_dict:
        return None

    filepath = _get_output_filepath(user_id, 'wordcloud')

    # --- 模仿 ECharts 的圆形遮罩 ---
    x, y = np.ogrid[:600, :600]
    mask = (x - 300) ** 2 + (y - 300) ** 2 > 290 ** 2
    mask = 255 * mask.astype(int)

    wc = WordCloud(
        # --- 关键修复：直接指定字体路径，不再让它自己找 ---
        font_path=UBUNTU_FONT_PATH,
        background_color='white',
        width=800,
        height=800, # 改为正方形以适应圆形
        max_words=100,
        colormap='viridis', # ECharts 默认的彩色方案之一
        mask=mask # 应用圆形遮罩
    )
    wc.generate_from_frequencies(freq_dict)
    
    # 移除边框白边
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wc)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(filepath, bbox_inches='tight', pad_inches=0)
    plt.close()

    return filepath

def generate_heatmap_image(heatmap_data: list, years: list, topics: list, user_id: int) -> str:
    """根据热力图数据生成图片，模仿 ECharts 样式。"""
    if not all([heatmap_data, years, topics]):
        return None

    df = pd.DataFrame(0.0, index=topics, columns=years)
    for item in heatmap_data:
        if len(item) == 3:
            year_idx, topic_idx, value = item
            if topic_idx < len(topics) and year_idx < len(years):
                df.iloc[topic_idx, year_idx] = value

    filepath = _get_output_filepath(user_id, 'heatmap')

    # --- 模仿 ECharts 的简洁风格 ---
    plt.figure(figsize=(10, 8))
    # 使用 'YlGnBu' 颜色映射，这与 ECharts 的默认热力图颜色相似
    # annot=True 显示数值, fmt=".2f" 格式化为两位小数
    sns.heatmap(
        df, 
        annot=True, 
        cmap="YlGnBu", 
        fmt=".2f", 
        linewidths=.5,
        cbar=False # 模仿 ECharts 的 visualMap: { show: false }，隐藏颜色条
    )
    
    # --- 关键修复：不再使用 font_properties 字典，而是直接使用 FontProperties 对象 ---
    if font_prop:
        plt.title('技术主题热度趋势图', fontsize=16, pad=20, fontproperties=font_prop)
        plt.xlabel('年份', fontsize=12, fontproperties=font_prop)
        plt.ylabel('技术主题', fontsize=12, fontproperties=font_prop)
        
        # 设置刻度标签字体
        plt.xticks(rotation=0)
        plt.yticks(rotation=0)
        # 对刻度标签应用字体属性
        for label in plt.gca().get_xticklabels():
            label.set_fontproperties(font_prop)
        for label in plt.gca().get_yticklabels():
            label.set_fontproperties(font_prop)
    else:
        # 如果字体文件不存在，至少能生成不带中文的图，而不是崩溃
        plt.title('Technology Topic Heatmap', fontsize=16, pad=20)
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Topic', fontsize=12)

    plt.tight_layout(rect=[0.05, 0, 1, 1]) 
    
    plt.savefig(filepath)
    plt.close()
    return filepath

# --- 新增函数：生成思维导图 ---
def generate_mindmap_image(mindmap_data: dict, user_id: int) -> str:
    """
    使用 Graphviz 生成思维导图图片，模仿 ECharts 风格。
    """
    if not mindmap_data or 'name' not in mindmap_data:
        return None

    filepath = _get_output_filepath(user_id, 'mindmap')
    
    # 初始化一个有向图，并设置全局样式以模仿 ECharts
    dot = graphviz.Digraph(comment='Mind Map')
    dot.attr('graph', rankdir='LR', splines='ortho', bgcolor='transparent')
    dot.attr('node', shape='box', style='rounded', fontname='WenQuanYi Zen Hei', fontsize='12')
    dot.attr('edge', arrowhead='none')

    # 使用一个内部递归函数来添加节点和边
    node_counter = 0
    def add_nodes_edges(data, parent_id=None):
        nonlocal node_counter
        current_id = f"node_{node_counter}"
        node_counter += 1
        
        dot.node(current_id, data['name'])
        
        if parent_id:
            dot.edge(parent_id, current_id)
            
        if 'children' in data and data['children']:
            for child in data['children']:
                add_nodes_edges(child, current_id)

    # 从根节点开始构建图
    add_nodes_edges(mindmap_data)

    # 渲染图片并保存。Graphviz 会自动调用系统命令。
    # 我们指定输出文件名（不带扩展名），它会自动加上 .png
    output_filename = os.path.splitext(filepath)[0]
    dot.render(output_filename, format='png', cleanup=True)
    
    # render 会生成 filename.png，所以我们返回这个路径
    return f"{output_filename}.png"