import io
import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_env = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates')))

def build_psychological_pdf_stream(analytics, summary, dates, scores, valences, arousals):
    """
    Playwright + Jinja2  PDF
    """
    va_data = [[v, arousals[i]] for i, v in enumerate(valences)]
    dist = analytics.get('distribution', {'positive': 0, 'neutral': 0, 'negative': 0})
    
    # 核心：DOM 文本依靠原生 Python 字典喂给 Jinja2，图表数组用 dumps 防止报错
    context = {
        "report_id": datetime.now().strftime('%Y%m%d%H%M%S'),
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "analytics": analytics,
        "summary": summary,
        "dates_json": json.dumps(dates, ensure_ascii=False),
        "scores_json": json.dumps(scores, ensure_ascii=False),
        "va_data_json": json.dumps(va_data, ensure_ascii=False),
        "dist_json": json.dumps(dist, ensure_ascii=False)
    }

    template = template_env.get_template('report_template.html')
    html_content = template.render(context)

    pdf_buffer = io.BytesIO()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 将 HTML 注入浏览器，并耐心等待 CDN 网络请求完毕
        page.set_content(html_content, wait_until="networkidle")
        
        # 等待 1 秒，确保图表 SVG 渲染入 DOM
        page.wait_for_timeout(1000)
        
        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
        )
        
        pdf_buffer.write(pdf_bytes)
        browser.close()

    pdf_buffer.seek(0)
    return pdf_buffer