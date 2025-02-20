import smtplib
import json
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pytz
import os

def load_email_config():
    with open('config/email.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config['email']

def load_posts():
    try:
        # 尝试多个可能的路径
        possible_paths = ['feed.json', './feed.json', 'data/feed.json']
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
                    
        print("加载文章数据失败: 找不到 feed.json 文件")
        return None
    except Exception as e:
        print(f"加载文章数据失败: {str(e)}")
        return None

def get_todays_posts(posts):
    if not posts or 'articles' not in posts:
        return []
    
    # 使用东八区时间
    tz = pytz.timezone('Asia/Shanghai')
    today = datetime.now(tz).date()
    
    todays_posts = []
    for post in posts['articles']:
        try:
            if 'date' not in post:
                continue
                
            # 处理日期格式，确保年份是4位数
            date_str = post['date']
            if date_str.startswith('1-'):  # 处理特殊情况
                continue
                
            post_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            post_date = post_time.date()
            
            if post_date == today:
                todays_posts.append({
                    'title': post.get('title', '无标题'),
                    'link': post.get('link', '#'),
                    'feed_title': post.get('author', '未知来源'),
                    'timestamp': post_time.strftime('%Y-%m-%d %H:%M'),
                    'summary': post.get('summary', '暂无摘要')
                })
        except Exception:
            continue
    
    return todays_posts

def generate_email_content(posts):
    """生成邮件HTML内容"""
    if not posts:
        return None
        
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            .article { margin-bottom: 20px; }
            .title { font-size: 18px; color: #333; }
            .meta { font-size: 14px; color: #666; }
            .summary { font-size: 16px; color: #444; }
        </style>
    </head>
    <body>
        <h2>今日更新的文章</h2>
    """
    
    for post in posts:
        # 检查 post 是否为字典类型
        if isinstance(post, dict):
            title = post.get('title', '无标题')
            link = post.get('link', '#')
            feed_title = post.get('feed_title', '未知来源')
            timestamp = post.get('timestamp', '')
            summary = post.get('summary', '暂无摘要')
        else:
            # 如果是字符串或其他类型，尝试直接使用
            title = link = feed_title = timestamp = summary = str(post)
            
        html_content += f"""
        <div class="article">
            <div class="title"><a href="{link}">{title}</a></div>
            <div class="meta">
                来源: {feed_title} | 
                时间: {timestamp}
            </div>
            <div class="summary">{summary}</div>
        </div>
        """
    
    html_content += "</body></html>"
    return html_content

def send_email(posts):
    if not posts:
        print("今天没有新文章更新")
        return
    
    email_config = load_email_config()
    if not email_config.get('enabled', False):
        print("邮件通知功能未启用")
        return
    
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = os.environ.get('SMTP_PORT')
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    recipients = email_config.get('recipients', [])
    
    if not all([smtp_server, smtp_port, sender_email, sender_password, recipients]):
        print("邮件配置不完整")
        return
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'RSS订阅更新通知 - {datetime.now(pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d")}'
    msg['From'] = sender_email
    msg['To'] = ', '.join(recipients)
    
    html_content = generate_email_content(posts)
    if html_content:
        msg.attach(MIMEText(html_content, 'html'))
        
        try:
            with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print(f"成功发送邮件给 {len(recipients)} 个收件人")
        except Exception as e:
            print(f"发送邮件失败: {str(e)}")

def main():
    posts = load_posts()
    if posts:
        todays_posts = get_todays_posts(posts)
        if todays_posts:
            print(f"找到 {len(todays_posts)} 篇今日更新的文章")
        send_email(todays_posts)

if __name__ == "__main__":
    main() 