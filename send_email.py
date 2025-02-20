import smtplib
import json
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pytz
import os

def load_config():
    """加载邮件配置"""
    try:
        with open('config/email.yml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config['email']
    except Exception as e:
        print(f"加载邮件配置失败: {e}")
        return None

def load_today_posts():
    """加载今天更新的文章"""
    try:
        with open('data/posts.json', 'r', encoding='utf-8') as f:
            posts = json.load(f)
        
        # 获取北京时间今天的日期
        tz = pytz.timezone('Asia/Shanghai')
        today = datetime.now(tz).date()
        
        # 按分类整理今天的文章
        categorized_posts = {
            'Blog': [],  # 博客文章
            'News': []   # 资讯
        }
        
        for post in posts:
            post_date = datetime.fromisoformat(post['date']).date()
            if post_date == today:
                category = post.get('category', 'Blog')  # 默认归类到Blog
                if category in categorized_posts:
                    categorized_posts[category].append(post)
                
        return categorized_posts
    except Exception as e:
        print(f"加载文章数据失败: {e}")
        return {'Blog': [], 'News': []}

def format_datetime(date_str):
    """格式化日期时间为中国格式"""
    try:
        # 解析ISO格式的时间字符串
        dt = datetime.fromisoformat(date_str)
        # 转换到北京时间
        tz = pytz.timezone('Asia/Shanghai')
        dt = dt.astimezone(tz)
        # 格式化为 "2024/03/21 14:30" 格式
        return dt.strftime('%Y/%m/%d %H:%M')
    except Exception as e:
        print(f"时间格式化失败: {e}")
        return date_str

def generate_email_content(categorized_posts):
    """生成邮件内容"""
    if not any(posts for posts in categorized_posts.values()):
        return None
    
    # 获取当前北京时间
    tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(tz).strftime('%Y/%m/%d %H:%M')
    
    html = """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f7;
            }
            
            .header {
                text-align: center;
                margin-bottom: 25px;
            }
            
            h2 {
                color: #1a1a1a;
                margin: 0 0 5px;
                font-size: 1.8em;
            }
            
            .time {
                color: #666;
                font-size: 1em;
            }
            
            .category-header {
                color: #2c3e50;
                font-size: 1.6em;
                margin: 30px 0 15px;
                padding-bottom: 8px;
                border-bottom: 2px solid #2c3e50;
            }
            
            .article {
                background: #fff;
                padding: 15px;
                margin-bottom: 15px;
                border-bottom: 1px solid #eee;
            }
            
            .article h3 {
                margin: 0;
                font-size: 1.3em;
                line-height: 1.4;
            }
            
            .article a {
                color: #2980b9;
                text-decoration: none;
            }
            
            .meta {
                color: #666;
                font-size: 0.9em;
                margin: 8px 0;
                padding-bottom: 8px;
                border-bottom: 1px solid #eee;
            }
            
            .meta span {
                margin-right: 15px;
            }
            
            .summary {
                color: #444;
                margin-top: 8px;
                font-size: 0.95em;
            }
            
            .footer {
                text-align: center;
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #eee;
                color: #666;
            }
            
            @media screen and (max-width: 600px) {
                body { padding: 15px; }
                .article { padding: 12px; }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>今日RSS更新</h2>
            <div class="time">""" + current_time + """</div>
        </div>
    """
    
    # 分类显示名映射
    category_names = {
        'Blog': '博客文章',
        'News': '资讯'
    }
    
    # 按分类显示文章
    for category, posts in categorized_posts.items():
        if not posts:  # 如果该分类没有文章则跳过
            continue
            
        html += f"""
        <div class="category-header">{category_names.get(category, category)}</div>
        """
        
        for post in posts:
            formatted_time = format_datetime(post['date'])
            html += f"""
            <div class="article">
                <h3><a href="{post['link']}">{post['title']}</a></h3>
                <div class="meta">
                    <span>来源: {post['feed_title']}</span>
                    <span>时间: {formatted_time}</span>
                </div>
                <div class="summary">{post.get('summary', '暂无摘要')}</div>
            </div>
            """
    
    html += """
        <div class="footer">
            感谢使用 RSS 订阅服务
        </div>
    </body>
    </html>
    """
    return html

def send_email():
    """发送邮件"""
    # 加载配置
    config = load_config()
    if not config or not config['enabled']:
        print("邮件通知未启用")
        return
        
    recipients = config['recipients']
    if not recipients:
        print("未配置收件人")
        return

    # 检查今日文章
    categorized_posts = load_today_posts()
    if not any(posts for posts in categorized_posts.values()):
        print("今天没有新文章更新")
        return
    
    html_content = generate_email_content(categorized_posts)
    if not html_content:
        return
        
    # 从环境变量获取邮件服务器配置
    smtp_server = os.environ['SMTP_SERVER']
    smtp_port = int(os.environ['SMTP_PORT'])
    sender_email = os.environ['SENDER_EMAIL']
    sender_password = os.environ['SENDER_PASSWORD']
    
    # 创建邮件
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'RSS订阅更新提醒 - {datetime.now().strftime("%Y-%m-%d")}'
    msg['From'] = sender_email
    msg['To'] = ', '.join(recipients)
    
    # 添加HTML内容
    msg.attach(MIMEText(html_content, 'html'))
    
    # 发送邮件
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("邮件发送成功")
    except Exception as e:
        print(f"发送邮件失败: {e}")

if __name__ == '__main__':
    send_email() 