from datetime import datetime
import pytz
import json
from send_email import generate_email_content

def load_feed_data():
    """加载 feed.json 数据"""
    try:
        with open('feed.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('articles', [])
    except Exception as e:
        print(f"加载 feed.json 失败: {e}")
        return []

def get_todays_articles(articles):
    """获取今天更新的文章"""
    today = datetime.now(pytz.timezone('Asia/Shanghai')).date()
    todays_articles = []
    
    for article in articles:
        try:
            article_date = datetime.strptime(article['date'], '%Y-%m-%d %H:%M').date()
            if article_date == today:
                todays_articles.append(article)
        except Exception:
            continue
            
    return todays_articles

def format_date(date_str):
    """格式化日期为简化的时间格式"""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
        return dt.strftime('%H:%M:%S')
    except Exception:
        return date_str

def generate_test_email():
    # 加载实际数据
    articles = load_feed_data()
    
    # 获取今天的文章
    todays_articles = get_todays_articles(articles)
    
    if not todays_articles:
        print("今天没有更新的文章")
        return
    
    # 按分类整理文章
    categorized_posts = {
        'Blog': [],
        'News': []
    }
    
    for article in todays_articles:
        category = article.get('category', 'News')
        if category in categorized_posts:
            categorized_posts[category].append({
                'title': article.get('title', '无标题'),
                'link': article.get('link', '#'),
                'feed_title': article.get('author', '未知来源'),
                'timestamp': article.get('date', ''),
                'summary': article.get('summary', '暂无摘要'),
                'category': category
            })

    # 如果没有任何分类有文章，就不生成预览
    if not any(categorized_posts.values()):
        print("今天没有更新的文章")
        return

    today = datetime.now(pytz.timezone('Asia/Shanghai'))
    weekday_cn = {
        0: '周一', 1: '周二', 2: '周三', 3: '周四', 
        4: '周五', 5: '周六', 6: '周日'
    }
    
    # 生成美化的HTML内容
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 15px;
                background-color: #ffffff;
                color: #2c3e50;
            }}
            @media (max-width: 600px) {{
                body {{
                    padding: 10px;
                }}
                .container {{
                    padding: 15px 10px;
                }}
            }}
            .container {{
                max-width: 100%;
                padding: 20px;
            }}
            .header {{
                margin-bottom: 40px;
                padding: 20px 0;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            h1 {{
                color: #2c3e50;
                margin: 0;
                font-size: 24px;
                font-weight: 600;
                letter-spacing: 1px;
            }}
            .date {{
                color: #666;
                font-size: 14px;
            }}
            .category {{
                margin-bottom: 35px;
            }}
            .category-title {{
                color: #2c3e50;
                font-size: 18px;
                padding-bottom: 12px;
                margin-bottom: 20px;
                border-bottom: 2px solid #3498db;
                font-weight: 600;
            }}
            .article {{
                margin-bottom: 25px;
                padding: 20px;
                background-color: #f8f9fa;
                border-left: 3px solid #3498db;
            }}
            .title {{
                font-size: 16px;
                margin-bottom: 12px;
                line-height: 1.4;
            }}
            .title a {{
                color: #3273dc;
                text-decoration: none;
                font-weight: 500;
            }}
            .title a:hover {{
                text-decoration: underline;
            }}
            .meta {{
                font-size: 13px;
                color: #666;
                margin-bottom: 12px;
            }}
            .meta-item {{
                display: inline-block;
            }}
            .meta-item:not(:last-child) {{
                margin-right: 20px;
            }}
            .meta-label {{
                color: #888;
            }}
            @media (max-width: 600px) {{
                .header {{
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 10px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>今日RSS更新</h1>
                <div class="date">
                    {today.strftime('%Y/%m/%d')} {weekday_cn[today.weekday()]} {today.strftime('%H:%M:%S')} 更新
                </div>
            </div>
    """
    
    # 只添加有文章的分类
    for category, posts in categorized_posts.items():
        if posts:  # 只显示有文章的分类
            html += f"""
                <div class="category">
                    <h2 class="category-title">{category}</h2>
            """
            
            for post in posts:
                formatted_time = format_date(post['timestamp'])
                html += f"""
                <div class="article">
                    <div class="title">
                        <a href="{post['link']}" target="_blank">{post['title']}</a>
                    </div>
                    <div class="meta">
                        <span class="meta-item">
                            <span class="meta-label">作者：</span>{post['feed_title']}
                        </span>
                        <span class="meta-item">
                            <span class="meta-label">更新时间：</span>{formatted_time}
                        </span>
                    </div>
                    <div class="summary">{post['summary']}</div>
                </div>
                """
                
            html += "</div>"
    
    html += """
        </div>
    </body>
    </html>
    """
    
    # 保存到文件
    with open('email_preview.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"邮件预览已生成到 email_preview.html (共 {len(todays_articles)} 篇文章)")

if __name__ == "__main__":
    generate_test_email() 