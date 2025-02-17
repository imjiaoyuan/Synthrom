import feedparser
import re
import json
from datetime import datetime
import pytz
from collections import defaultdict
import yaml  # 添加 yaml 导入

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
    for category, articles in articles_by_category.items():
        articles.sort(key=lambda x: x['timestamp'], reverse=True)
        all_articles.extend(articles)
    
    # 最终按时间排序
    all_articles.sort(key=lambda x: x['timestamp'], reverse=True)
    
    data = {
        'update_time': datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d'),
        'articles': all_articles
    }
    
    with open('feed.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    fetch_feeds() 