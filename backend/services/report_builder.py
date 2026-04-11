import io
import os
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ==================================================================
# ⚙️ 字体加载逻辑 (无敌版)
# ==================================================================
FONT_PATHS = [
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\msyh.ttc",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts', 'simhei.ttf') 
]

font_name = 'Helvetica' # 兜底
for path in FONT_PATHS:
    if os.path.exists(path):
        try:
            pdfmetrics.registerFont(TTFont('CustomFont', path))
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            font_name = 'CustomFont'
            break
        except: continue

# ==================================================================
# 🎨 内部辅助函数：高精度图表生成
# ==================================================================

def _generate_trend_chart(dates, scores):
    """趋势图：增加渐变填充效果感"""
    fig, ax = plt.subplots(figsize=(8, 3.5), dpi=300)
    ax.plot(dates, scores, marker='o', color='#1890FF', linewidth=2.5, markersize=6, markerfacecolor='white', markeredgewidth=2)
    ax.fill_between(dates, scores, color='#1890FF', alpha=0.1) # 增加淡蓝色面积填充
    ax.set_ylim(0, 105)
    ax.set_ylabel("心情指数", fontsize=9, color='#666666')
    ax.grid(True, axis='y', linestyle=':', alpha=0.6)
    ax.axhline(y=60, color='#cccccc', linestyle='--', linewidth=1)
    # 隐藏边框
    for spine in ['top', 'right', 'left']: ax.spines[spine].set_visible(False)
    ax.tick_params(axis='both', colors='#888888', labelsize=8)
    
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png', transparent=True, bbox_inches='tight')
    plt.close(fig)
    img_stream.seek(0)
    return img_stream

def _generate_scatter_chart(valences, arousals):
    """散点图：增加象限背景色"""
    fig, ax = plt.subplots(figsize=(4, 4), dpi=300)
    # 绘制象限底色
    ax.axvspan(1, 5.5, 5.5, 10, color='#FFF1F0', alpha=0.3) # 应激区-浅红
    ax.axvspan(1, 5.5, 1, 5.5, color='#F0F5FF', alpha=0.3)  # 抑郁区-浅蓝
    
    ax.scatter(valences, arousals, color='#1890FF', alpha=0.7, s=100, edgecolors='white', linewidth=1.5, zorder=3)
    ax.set_xlim(1, 10); ax.set_ylim(1, 10)
    ax.axhline(5.5, color='#999999', linewidth=0.8); ax.axvline(5.5, color='#999999', linewidth=0.8)
    
    styles = {'fontsize': 10, 'fontweight': 'bold', 'alpha': 0.5}
    ax.text(8, 8, '激越', ha='center', **styles)
    ax.text(3, 8, '应激', ha='center', color='#CF1322', **styles)
    ax.text(3, 3, '抑郁', ha='center', color='#1D39C4', **styles)
    ax.text(8, 3, '放松', ha='center', color='#389E0D', **styles)
    ax.set_xticks([]); ax.set_yticks([])
    
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png', transparent=True, bbox_inches='tight')
    plt.close(fig)
    img_stream.seek(0)
    return img_stream

def _generate_pie_chart(dist):
    """饼图：改为现代环形图"""
    fig, ax = plt.subplots(figsize=(4, 4), dpi=300)
    labels = ['积极/高能', '平静/中性', '消极/内耗']
    sizes = [dist.get('positive', 0), dist.get('neutral', 0), dist.get('negative', 0)]
    colors_list = ['#52C41A', '#BFBFBF', '#FF4D4F']
    
    # 过滤 0
    data = [(s, l, c) for s, l, c in zip(sizes, labels, colors_list) if s > 0]
    if not data: 
        ax.pie([1], colors=['#F5F5F5'], startangle=90, wedgeprops={'width': 0.3})
        ax.text(0, 0, '暂无数据', ha='center', va='center', color='#999999')
    else:
        s, l, c = zip(*data)
        ax.pie(s, labels=l, colors=c, autopct='%1.1f%%', startangle=90, 
               pctdistance=0.85, wedgeprops={'width': 0.3, 'edgecolor': 'white', 'linewidth': 2},
               textprops={'fontsize': 9, 'color': '#333333'})
    
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png', transparent=True, bbox_inches='tight')
    plt.close(fig)
    img_stream.seek(0)
    return img_stream

# ==================================================================
# 💠 UI 组件：精致卡片容器
# ==================================================================
def _make_styled_card(elements, bg_color='#FFFFFF', border_color='#E8E8E8', left_border=None):
    """
    elements: 内部 Paragraph 列表
    left_border: 如果提供，会在卡片左侧加粗色条 (如 #1890FF)
    """
    card_table = Table([[elements]], colWidths=[175*mm])
    style_config = [
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg_color)),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor(border_color)),
        ('LEFTPADDING', (0,0), (-1,-1), 18),
        ('RIGHTPADDING', (0,0), (-1,-1), 18),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ('ROUNDEDCORNERS', (0,0), (-1,-1), [6, 6, 6, 6])
    ]
    if left_border:
        style_config.append(('LINEBEFORE', (0,0), (0,0), 3, colors.HexColor(left_border)))
        
    card_table.setStyle(TableStyle(style_config))
    return card_table

# ==================================================================
# 🚀 导出主函数
# ==================================================================
def build_psychological_pdf_stream(analytics, summary, dates, scores, valences, arousals):
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, 
                            rightMargin=12*mm, leftMargin=12*mm, 
                            topMargin=15*mm, bottomMargin=15*mm)
    
    # --- 统一样式表 ---
    title_style = ParagraphStyle(name='T', fontName=font_name, fontSize=24, textColor=colors.HexColor('#1A1A1A'), alignment=1, spaceAfter=5, fontWeight='BOLD')
    sub_style = ParagraphStyle(name='S', fontName=font_name, fontSize=10, textColor=colors.HexColor('#8C8C8C'), alignment=1, spaceAfter=25)
    h2_style = ParagraphStyle(name='H2', fontName=font_name, fontSize=14, textColor=colors.HexColor('#1890FF'), spaceBefore=20, spaceAfter=12, leftIndent=2)
    normal_style = ParagraphStyle(name='N', fontName=font_name, fontSize=11, leading=18, textColor=colors.HexColor('#434343'))
    label_style = ParagraphStyle(name='L', fontName=font_name, fontSize=11, textColor=colors.black, fontWeight='BOLD')
    tag_style = ParagraphStyle(name='Tag', fontName=font_name, fontSize=10, textColor=colors.white, backColor=colors.HexColor('#1890FF'), borderPadding=3, borderRadius=4)

    story = []
    
    # 1. 页眉标题区
    story.append(Paragraph("PSYCHOLOGICAL INSIGHT REPORT", ParagraphStyle('m', fontName=font_name, fontSize=8, textColor=colors.HexColor('#CCCCCC'), alignment=1)))
    story.append(Paragraph("深度心理洞察报告", title_style))
    story.append(Paragraph(f"评估 ID: {datetime.now().strftime('%Y%m%d%H%M')} | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}", sub_style))

    # 2. 风险警报 (仅高风险显示)
    if analytics.get('risk_level') == 'HIGH':
        risk_content = [
            Paragraph("🚨 <b>情绪高风险预警</b>", ParagraphStyle('r', fontName=font_name, fontSize=12, textColor=colors.HexColor('#CF1322'))),
            Spacer(1, 3),
            Paragraph("系统检测到您近期情绪能量极低或存在剧烈波动。建议您暂时停下手中工作，若持续感到痛苦，请务必寻求专业心理咨询支持。", 
                      ParagraphStyle('rd', fontName=font_name, fontSize=10, textColor=colors.HexColor('#A8071A'), leading=14))
        ]
        story.append(_make_styled_card(risk_content, bg_color='#FFF1F0', border_color='#FFA39E', left_border='#CF1322'))
        story.append(Spacer(1, 10))

    # 3. AI 核心诊断卡片
    story.append(Paragraph("💡 AI 导师诊断陈述", h2_style))
    
    # 健康指数状态栏
    health_index = analytics.get('health_index', 60)
    health_color = '#52C41A' if health_index > 70 else ('#FAAD14' if health_index > 45 else '#F5222D')
    
    diag_elements = [
        Table([
            [Paragraph(f"<b>画像解析：</b> {analytics.get('persona')}", normal_style), 
             Paragraph(f"<font color='{health_color}'>●</font> <b>心理健康指数：{health_index}</b>", normal_style)]
        ], colWidths=[90*mm, 70*mm]),
        Spacer(1, 10),
        Paragraph("<b>当前心境：</b>", label_style),
        Paragraph(summary.get('status_summary'), normal_style),
        Spacer(1, 10),
        Table([
            [Paragraph("<b>🔍 潜在情绪触发点</b>", label_style), Paragraph("<b>🌱 CBT 干预建议</b>", label_style)],
            [Paragraph("<br/>".join([f"• {i}" for i in summary.get('core_issues', [])]), normal_style),
             Paragraph("<br/>".join([f"• {i}" for i in summary.get('action_advices', [])]), normal_style)]
        ], colWidths=[80*mm, 80*mm])
    ]
    story.append(_make_styled_card(diag_elements, bg_color='#FFFFFF', border_color='#E8E8E8', left_border='#1890FF'))

    # 4. 风险记录
    quotes = analytics.get('high_risk_quotes', [])
    if quotes:
        story.append(Paragraph("🚨 核心痛点与风险原话回溯", h2_style))
        qc = []
        for q in quotes:
            qc.append(Paragraph(f"<font color='#8C8C8C' size='9'>[{q['time']}]</font> &nbsp; <i>\"{q['text']}\"</i>", 
                                ParagraphStyle('q', fontName=font_name, fontSize=10, leading=14, textColor='#595959')))
        story.append(_make_styled_card(qc, bg_color='#FAFAFA', border_color='#D9D9D9'))

    # 5. 趋势分析
    story.append(Paragraph("📉 近期心境波动轨迹", h2_style))
    trend_info = f"波动率指数: <b>{analytics.get('volatility')}</b> &nbsp;&nbsp; | &nbsp;&nbsp; 干预环比变化: <b>{analytics.get('progress_delta')}</b>"
    story.append(Paragraph(trend_info, ParagraphStyle('ti', fontName=font_name, fontSize=10, leftIndent=2)))
    story.append(Spacer(1, 5))
    story.append(Image(_generate_trend_chart(dates, scores), width=175*mm, height=75*mm))

    # 6. 二维空间与饼图
    story.append(Paragraph("🧭 能量空间与内稳态结构", h2_style))
    chart_row = [
        [Image(_generate_scatter_chart(valences, arousals), width=80*mm, height=80*mm), 
         Image(_generate_pie_chart(analytics.get('distribution', {})), width=80*mm, height=80*mm)],
        [Paragraph("心理能量空间 (Russell模型)", ParagraphStyle('c1', fontName=font_name, alignment=1, fontSize=9, textColor='#8C8C8C')),
         Paragraph("情绪内稳态占比", ParagraphStyle('c2', fontName=font_name, alignment=1, fontSize=9, textColor='#8C8C8C'))]
    ]
    story.append(KeepTogether([Table(chart_row, colWidths=[88*mm, 88*mm])]))

    # 页脚修饰线条
    story.append(Spacer(1, 15))
    story.append(Table([[""]], colWidths=[180*mm], style=TableStyle([('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor('#F0F0F0'))])))
    story.append(Paragraph("本报告仅供心理状态参考，不作为医学诊断依据。", 
                           ParagraphStyle('f', fontName=font_name, fontSize=8, color='#BFBFBF', alignment=1)))

    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer