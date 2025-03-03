import os
import json
from fetch_feeds import fetch_feeds
from send_email import send_email

# 创建测试目录
os.makedirs('test_data', exist_ok=True)

# 设置测试环境变量 (以QQ邮箱为例)
os.environ['SMTP_SERVER'] = 'smtp.qq.com'
os.environ['SMTP_PORT'] = '465'
os.environ['SENDER_EMAIL'] = 'xxxxxxxx@qq.com'
os.environ['SENDER_PASSWORD'] = 'xxxxxxxxxxxxxx'

def test_smtp_connection():
    """测试SMTP连接"""
    import smtplib
    import ssl
    
    print("\n=== 测试SMTP连接 ===")
    
    # 测试端口列表
    ports = [587, 465, 25]
    
    for port in ports:
        print(f"\n尝试端口 {port}...")
        try:
            if port == 465:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL('smtp.qq.com', port, context=context, timeout=10) as server:
                    print(f"端口 {port} SSL连接成功")
                    server.login(os.environ['SENDER_EMAIL'], os.environ['SENDER_PASSWORD'])
                    print(f"端口 {port} 登录成功")
            else:
                with smtplib.SMTP('smtp.qq.com', port, timeout=10) as server:
                    print(f"端口 {port} 连接成功")
                    server.starttls()
                    print(f"端口 {port} TLS升级成功")
                    server.login(os.environ['SENDER_EMAIL'], os.environ['SENDER_PASSWORD'])
                    print(f"端口 {port} 登录成功")
        except Exception as e:
            print(f"端口 {port} 测试失败: {str(e)}")
            continue

try:
    # 测试SMTP连接
    test_smtp_connection()
    
    # 抓取文章
    print("\n=== 开始抓取文章 ===")
    fetch_feeds()
    
    # 保存一份feed.json到测试目录
    print("\n=== 保存测试数据 ===")
    with open('feed.json', 'r', encoding='utf-8') as f:
        feed_data = json.load(f)
    with open('test_data/feed.json', 'w', encoding='utf-8') as f:
        json.dump(feed_data, f, ensure_ascii=False, indent=2)
    print("Feed数据已保存到: test_data/feed.json")
    
    # 发送邮件
    print("\n=== 开始发送邮件 ===")
    send_email()
    
    print("\n=== 测试完成! ===")
    print("可以在test_data目录下查看生成的文件:")
    print("- test_data/feed.json: 抓取的文章数据")
    print("- test_data/email_preview.html: 邮件预览")
except Exception as e:
    print(f"\n!!! 测试失败 !!!")
    print(f"错误信息: {str(e)}")
    print(f"错误类型: {type(e)}")
    raise 