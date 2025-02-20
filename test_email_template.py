from datetime import datetime
import pytz
from send_email import generate_email_content

def format_datetime(date_str):
    """格式化日期时间为中国格式"""
    try:
        dt = datetime.fromisoformat(date_str)
        tz = pytz.timezone('Asia/Shanghai')
        dt = dt.astimezone(tz)
        return dt.strftime('%Y/%m/%d %H:%M')
    except Exception as e:
        print(f"时间格式化失败: {e}")
        return date_str

def generate_test_email():
    # 模拟一些测试文章数据
    test_posts = {
        'Blog': [
            {
                'title': '深度学习在自然语言处理中的最新进展',
                'link': 'https://example.com/post1',
                'feed_title': 'AI研究论坛',
                'date': '2024-03-20T10:30:00+08:00',
                'summary': '本文详细介绍了Transformer架构的最新改进，以及在大规模语言模型训练中的创新应用。包括注意力机制的优化、模型压缩技术等关键突破。',
                'category': 'Blog'
            },
            {
                'title': 'Python 3.12新特性解析',
                'link': 'https://example.com/post2',
                'feed_title': 'Python开发者周刊',
                'date': '2024-03-20T14:20:00+08:00',
                'summary': 'Python 3.12带来了多项重要更新，包括性能优化、新的语法特性和标准库更新。本文深入解析这些新特性对开发者的影响。',
                'category': 'Blog'
            }
        ],
        'News': [
            {
                'title': '2024年开源项目发展趋势',
                'link': 'https://example.com/post3',
                'feed_title': '开源中国',
                'date': '2024-03-20T16:45:00+08:00',
                'summary': '从贡献者数量、项目活跃度和应用领域等多个维度，分析2024年开源项目的发展现状和未来趋势。',
                'category': 'News'
            }
        ]
    }
    
    # 使用与 send_email.py 相同的邮件生成函数
    html = generate_email_content(test_posts)
    
    # 保存到文件以便预览
    with open('email_preview.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("邮件预览已生成到 email_preview.html")

if __name__ == '__main__':
    generate_test_email() 