import feedparser
import re
import json
from datetime import datetime
import pytz
from collections import defaultdict
import yaml
import os
from pathlib import Path

def get_feed_category(feed_url, feed_list_content):
    # 查找feed_url所属的分类
    lines = feed_list_content.split('\n')
    current_category = None
    for line in lines:
        line = line.strip()
        if line.endswith(':'):
            current_category = line[:-1]  # 移除冒号
        elif line == feed_url:
            return current_category
    return 'Blog'  # 默认分类为 Blog

def fetch_feeds():
    # 加载标签配置
    with open('config/labels.yml', 'r', encoding='utf-8') as f:
        label_config = yaml.safe_load(f)
    
    # 创建分类到配置的映射
    category_configs = {label['feed_category']: label for label in label_config['labels']}
    default_limit = label_config['default_limit']

    with open('feed.list', 'r') as f:
        feed_list_content = f.read()
        feeds = [line.strip() for line in feed_list_content.splitlines() if line.strip() and not line.endswith(':')]
    
    articles_by_category = defaultdict(list)
    
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            category = get_feed_category(feed_url, feed_list_content)
            
            # 获取该分类的文章数量限制
            category_config = category_configs.get(category, {})
            article_limit = category_config.get('article_limit', default_limit)
            
            entries = feed.entries
            if article_limit > 0:
                entries = entries[:article_limit]
            
            for entry in entries:
                published = entry.get('published_parsed', entry.get('updated_parsed'))
                if published:
                    dt = datetime(*published[:6])
                    dt = pytz.UTC.localize(dt)
                    beijing_tz = pytz.timezone('Asia/Shanghai')
                    dt = dt.astimezone(beijing_tz)
                    published_str = dt.strftime('%Y-%m-%d %H:%M')
                else:
                    published_str = ''
                
                summary = ''
                if 'summary' in entry:
                    summary = re.sub(r'<[^>]+>', '', entry.summary)
                    summary = summary.strip()[:150] + ('...' if len(summary) > 150 else '')
                elif 'description' in entry:
                    summary = re.sub(r'<[^>]+>', '', entry.description)
                    summary = summary.strip()[:150] + ('...' if len(summary) > 150 else '')
                
                article = {
                    'title': entry.title,
                    'link': entry.link,
                    'date': published_str,
                    'author': feed.feed.title,
                    'timestamp': dt.timestamp() if published else 0,
                    'summary': summary or '无摘要',
                    'source_url': feed.feed.link or feed_url,
                    'category': category
                }
                articles_by_category[category].append(article)
        except Exception as e:
            print(f"Error fetching {feed_url}: {str(e)}")
            continue
    
    # 对每个分类的文章进行排序
    all_articles = []
    
    # 先添加Blog文章
    if 'Blog' in articles_by_category:
        blog_articles = articles_by_category['Blog']
        blog_articles.sort(key=lambda x: x['timestamp'], reverse=True)
        all_articles.extend(blog_articles)
    
    # 再添加News文章
    if 'News' in articles_by_category:
        news_articles = articles_by_category['News']
        news_articles.sort(key=lambda x: x['timestamp'], reverse=True)
        all_articles.extend(news_articles)
    
    # 不需要最终排序，保持Blog在前News在后的顺序
    # all_articles.sort(key=lambda x: x['timestamp'], reverse=True)
    
    data = {
        'update_time': datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d'),
        'articles': all_articles
    }
    
    with open('feed.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_feed_config():
    """从 feed.list 加载订阅源配置"""
    feeds = []
    current_category = None
    
    with open('feed.list', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:  # 跳过空行
                continue
            
            if line.endswith(':'):  # 分类行
                current_category = line[:-1]
            else:  # RSS源链接行
                if current_category:
                    feeds.append({
                        'name': line,  # 暂时用URL作为名称
                        'url': line,
                        'category': current_category
                    })
    
    return {'feeds': feeds}

def fetch_all_feeds():
    """抓取所有订阅源的文章"""
    config = load_feed_config()
    
    # 确保posts目录存在
    posts_dir = Path('posts')
    posts_dir.mkdir(exist_ok=True)
    
    # 获取中国时区
    tz = pytz.timezone('Asia/Shanghai')
    today = datetime.now(tz).date()
    
    for feed in config['feeds']:
        try:
            print(f"正在抓取: {feed['url']}")
            parsed = feedparser.parse(feed['url'])
            
            # 使用真实的源标题
            feed_title = parsed.feed.get('title', feed['url'])
            
            for entry in parsed.entries[:10]:  # 每个源最多取10篇
                # 解析发布时间
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    date = datetime.fromtimestamp(
                        datetime.fromtimestamp(
                            datetime.fromtimestamp(published).timestamp()
                        ).timestamp(), 
                        tz
                    )
                else:
                    date = datetime.now(tz)
                
                # 只保存今天的文章
                if date.date() == today:
                    post = {
                        'title': entry.title,
                        'link': entry.link,
                        'date': date.isoformat(),
                        'source': feed_title,
                        'category': feed['category'],
                        'summary': entry.get('summary', '暂无描述')
                    }
                    
                    # 使用文章标题作为文件名(过滤非法字符)
                    safe_title = "".join(c for c in entry.title if c.isalnum() or c in (' ', '-', '_'))
                    filename = f"{safe_title[:50]}.yml"
                    
                    with open(posts_dir / filename, 'w', encoding='utf-8') as f:
                        yaml.dump(post, f, allow_unicode=True)
                        
        except Exception as e:
            print(f"抓取 {feed['url']} 失败: {str(e)}")
            continue

if __name__ == '__main__':
    fetch_feeds()
    fetch_all_feeds() 