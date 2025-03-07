import os
import json
import smtplib
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from datetime import datetime, timedelta
import pytz
import ssl
import argparse
import time

def load_config():
    """加载邮件配置"""
    with open('config/email.yml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_beijing_time_window():
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.datetime.now(beijing_tz)
    
    # 获取今天的早上8点
    today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
    
    # 如果现在还不到早上8点，就用昨天早上8点到今天早上8点
    # 如果已经过了早上8点，就用今天早上8点到明天早上8点
    if now.hour < 8:
        end_time = today_8am
        start_time = end_time - datetime.timedelta(days=1)
    else:
        start_time = today_8am
        end_time = start_time + datetime.timedelta(days=1)
    
    return start_time, end_time

def get_today_articles():
    """从feed.json中获取今天早8点到昨天早8点的文章"""
    with open('feed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    
    today = now.strftime('%Y-%m-%d')
    today_8am = f"{today} 08:00:00"
    yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    yesterday_8am = f"{yesterday} 08:00:00"
    
    today_articles = []
    for article in data['articles']:
        try:
            article_date = article['date']
            if yesterday_8am <= article_date < today_8am:
                today_articles.append(article)
        except (ValueError, TypeError) as e:
            print(f"错误: 处理文章时间出错 - {e}")
            continue
    
    return today_articles

def generate_email_content(articles):
    """生成邮件HTML内容"""
    if not articles:
        return None
    
    # 获取当前时间
    tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M')
    
    # 修改CSS样式部分
    style = """
        <style>
            /* 基础样式 */
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.5;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 12px;  /* 减小整体边距 */
                font-size: 14px;
            }
            
            /* 邮件主体 */
            .email-body {
                padding: 12px;  /* 减小内边距 */
            }
            
            /* 头部样式 */
            .header {
                display: flex;
                justify-content: space-between;
                align-items: baseline;
                border-bottom: 1px solid #eee;  /* 减小分隔线粗细 */
                padding-bottom: 6px;  /* 减小底部间距 */
                margin: 12px 0;  /* 减小上下间距 */
            }
            
            .header h2 {
                font-size: 18px;
                font-weight: 500;
                color: #2c3e50;
                margin: 0;
            }
            
            /* 文章卡片样式 */
            .post {
                border: 1px solid #e0e0e0;
                border-radius: 6px;  /* 减小圆角 */
                padding: 12px;  /* 减小内边距 */
                margin-bottom: 16px;  /* 减小卡片间距 */
            }
            
            /* 标题样式 */
            .title {
                margin-bottom: 8px;  /* 减小标题下方间距 */
                padding-bottom: 6px;  /* 减小标题分隔线上方间距 */
                border-bottom: 1px solid #f0f0f0;
            }
            
            .title a {
                color: #2c3e50;
                text-decoration: none;
                font-weight: 500;
                font-size: 15px;  /* 稍微调小标题字号 */
            }
            
            /* 分类标签样式 */
            .category {
                display: inline-block;
                padding: 2px 6px;  /* 减小标签内边距 */
                border-radius: 3px;
                font-size: 12px;
                margin-right: 6px;
            }
            
            .category.blog {
                background: #e8f5e9;
                color: #2e7d32;
            }
            
            .category.news {
                background: #fff3e0;
                color: #ef6c00;
            }
            
            /* 元信息样式 */
            .meta {
                font-size: 12px;
                color: #666;
                margin-bottom: 8px;  /* 减小元信息下方间距 */
            }
            
            /* 摘要样式 */
            .summary {
                color: #444;
                line-height: 1.5;
                font-size: 13px;
            }
            
            /* 分类标题样式 */
            h3 {
                font-size: 16px;
                font-weight: 500;
                color: #1a1a1a;
                margin: 16px 0 12px;  /* 减小分类标题间距 */
                padding-bottom: 6px;
                border-bottom: 1px solid #f0f0f0;
            }
        </style>
    """
    
    # 修改 HTML 结构，减少嵌套层级
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {style}
    </head>
    <body>
        <div class="header">
            <h2>今日RSS更新</h2>
            <span class="time">{current_time}</span>
        </div>
    """
    
    # 按分类组织文章
    articles_by_category = {
        'Blog': [],
        'News': []
    }
    
    for article in articles:
        category = article['category']
        if category in articles_by_category:
            articles_by_category[category].append(article)
    
    # 按固定顺序显示分类 (Blog在前，News在后)
    for category in ['Blog', 'News']:
        category_articles = articles_by_category[category]
        if category_articles:  # 只显示有文章的分类
            html += f'<h3>{category}</h3>'
            for article in sorted(category_articles, key=lambda x: x['timestamp'], reverse=True):
                category_class = 'blog' if category == 'Blog' else 'news'
                # 减少 div 嵌套层级
                html += f"""
                <div class="post">
                    <div class="title"><a href="{article['link']}" target="_blank">{article['title']}</a></div>
                    <div class="meta">
                        <span class="category {category_class}">{article['category']}</span>
                        {article['author']} / {article['date']}
                    </div>
                    <div class="summary">{article['summary']}</div>
                </div>
                """
    
    html += """
        <div style="color: #666; font-size: 12px; margin-top: 20px; border-top: 1px solid #eee; padding-top: 12px;">
            由 RSS Reader 自动生成
        </div>
    </body>
    </html>
    """
    
    # 在发送前进行额外处理
    # 移除可能导致Gmail截断的注释
    html = html.replace('<!--', '').replace('-->', '')
    
    # 确保所有块级元素都有display: block !important
    for tag in ['div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        html = html.replace(f'<{tag}', f'<{tag} style="display: block !important;"')
    
    # 保存邮件HTML预览
    os.makedirs('test_data', exist_ok=True)
    with open('test_data/email_preview.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    return html

def send_email():
    """发送邮件"""
    config = load_config()
    if not config['email']['enabled']:
        return
    
    articles = get_today_articles()
    if not articles:
        return
    
    html_content = generate_email_content(articles)
    
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = os.environ.get('SMTP_PORT')
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    
    if not all([smtp_server, smtp_port, sender_email, sender_password]):
        raise ValueError("错误: 缺少SMTP配置信息")
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '今日RSS更新'
    msg['From'] = formataddr(('RSS Reader', sender_email))
    msg['To'] = ', '.join(config['email']['recipients'])
    
    text_content = "请使用支持HTML的邮件客户端查看此邮件。"
    msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        print("✓ 邮件发送成功")
        return True
        
    except smtplib.SMTPException as e:
        print(f"✗ 邮件发送失败: {str(e)}")
        return False
        
    except Exception as e:
        print(f"✗ 发生错误: {str(e)}")
        return False
        
    finally:
        try:
            server.quit()
        except:
            pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--beijing-time', action='store_true')
    parser.add_argument('--time-window', type=int)
    args = parser.parse_args()
    
    if args.beijing_time:
        start_time, end_time = get_beijing_time_window()
    else:
        end_time = datetime.datetime.now(pytz.UTC)
        start_time = end_time - datetime.timedelta(hours=args.time_window or 24)
    
    articles = get_articles_in_timewindow(start_time, end_time)
    
    if articles:
        max_retries = 3
        for i in range(max_retries):
            if send_email():
                break
            if i < max_retries - 1:
                print(f"✗ 第{i+1}次尝试失败,5秒后重试...")
                time.sleep(5)

if __name__ == '__main__':
    main() 