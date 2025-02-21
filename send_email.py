import os
import json
import smtplib
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from datetime import datetime
import pytz

def load_config():
    """加载邮件配置"""
    with open('config/email.yml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_today_articles():
    """从feed.json中获取今天的文章"""
    with open('feed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 获取中国时区的今天日期
    tz = pytz.timezone('Asia/Shanghai')
    today = datetime.now(tz).strftime('%Y-%m-%d')
    
    # 筛选今天的文章
    today_articles = [
        article for article in data['articles']
        if article['date'].startswith(today)
    ]
    
    return today_articles

def generate_email_content(articles):
    """生成邮件HTML内容"""
    if not articles:
        return None
    
    # 获取当前时间
    tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M')
    
    # CSS样式部分使用普通字符串
    style = """
        <style>
            /* 重置默认样式 */
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 15px;
                background: #f9f9f9;
                font-size: 14px;  /* 默认字体大小调小 */
            }
            
            /* 移动端适配 */
            @media screen and (max-width: 600px) {
                body {
                    padding: 10px;
                    font-size: 13px;  /* 移动端字体更小 */
                }
            }
            
            .header {
                display: flex;
                justify-content: space-between;
                align-items: baseline;
                border-bottom: 2px solid #eee;
                padding-bottom: 8px;
                margin: 20px 0 15px;
            }
            
            .header h2 {
                font-size: 20px;  /* 标题字体调小 */
                font-weight: 500;
                color: #2c3e50;
                margin: 0;
            }
            
            .header .time {
                font-size: 13px;
                color: #7f8c8d;
            }
            
            h3 {
                font-size: 18px;  /* 分类标题调小 */
                font-weight: 500;
                color: #34495e;
                margin: 20px 0 12px;
            }
            
            .post {
                background: white;
                border-radius: 6px;
                padding: 15px;
                margin: 12px 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
            
            .title {
                font-size: 16px;  /* 文章标题调小 */
                margin-bottom: 8px;
            }
            
            .title a {
                color: #2c3e50;
                text-decoration: none;
                font-weight: 500;
            }
            
            .meta {
                font-size: 13px;
                color: #7f8c8d;
                margin-bottom: 8px;
            }
            
            .category {
                display: inline-block;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: 500;
                margin-right: 6px;
            }
            
            .category.blog {
                background: #e3f2fd;
                color: #1976d2;
            }
            
            .category.news {
                background: #f3e5f5;
                color: #7b1fa2;
            }
            
            .summary {
                font-size: 14px;
                color: #5f6368;
                line-height: 1.5;
            }
            
            footer {
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #eee;
                text-align: center;
                font-size: 13px;
                color: #95a5a6;
            }
            
            /* 强制显示完整内容 */
            .email-content {
                display: block !important;
                max-height: none !important;
                overflow: visible !important;
            }
        </style>
    """
    
    # 修改HTML结构
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {style}
    </head>
    <body>
        <div class="email-content">
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
                html += f"""
                <div class="post">
                    <div class="title">
                        <a href="{article['link']}" target="_blank">{article['title']}</a>
                    </div>
                    <div class="meta">
                        <span class="category {category_class}">{article['category']}</span>
                        {article['author']} / {article['date']}
                    </div>
                    <div class="summary">{article['summary']}</div>
                </div>
                """
    
    html += """
            <footer>
                由 RSS Reader 自动生成
            </footer>
        </div>
    </body>
    </html>
    """
    
    # 保存邮件HTML预览
    os.makedirs('test_data', exist_ok=True)
    with open('test_data/email_preview.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    return html

def send_email():
    """发送邮件"""
    print("开始加载邮件配置...")
    config = load_config()
    if not config['email']['enabled']:
        print("邮件通知未启用")
        return
    
    print("开始获取今日文章...")
    articles = get_today_articles()
    if not articles:
        print("今天没有新文章更新")
        return
    
    print(f"找到 {len(articles)} 篇今日文章")
    print("开始生成邮件内容...")
    html_content = generate_email_content(articles)
    
    # 获取环境变量中的SMTP配置
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = os.environ.get('SMTP_PORT')
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    
    if not all([smtp_server, smtp_port, sender_email, sender_password]):
        raise ValueError("缺少SMTP配置信息")
    
    print(f"SMTP配置: {smtp_server}:{smtp_port}")
    print(f"发件人: {sender_email}")
    
    # 创建邮件
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '今日RSS更新'
    msg['From'] = formataddr(('今日RSS更新', sender_email))
    msg['To'] = ', '.join(config['email']['recipients'])
    
    msg.attach(MIMEText(html_content, 'html'))
    
    # 发送邮件
    try:
        print("开始连接SMTP服务器...")
        import ssl
        context = ssl.create_default_context()
        
        if int(smtp_port) == 465:
            # 使用 SSL 连接
            print("使用SSL连接...")
            try:
                server = smtplib.SMTP_SSL(smtp_server, 
                                        int(smtp_port), 
                                        context=context,
                                        timeout=10)
                print("SSL连接成功")
            except Exception as e:
                print(f"SSL连接失败: {str(e)}")
                print("尝试普通连接...")
                server = smtplib.SMTP(smtp_server, int(smtp_port))
                server.starttls(context=context)
                print("TLS连接成功")
        else:
            # 使用 TLS 连接
            print("使用TLS连接...")
            server = smtplib.SMTP(smtp_server, int(smtp_port))
            server.starttls(context=context)
            print("TLS连接成功")
        
        try:
            print("开始登录...")
            server.login(sender_email, sender_password)
            print("登录成功")
            
            print("开始发送邮件...")
            server.send_message(msg)
            print("邮件发送成功")
        except Exception as e:
            print(f"操作失败: {str(e)}")
            print(f"错误类型: {type(e)}")
            raise
        finally:
            print("关闭连接...")
            server.quit()
            
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
        print(f"错误类型: {type(e)}")
        raise

if __name__ == '__main__':
    send_email() 