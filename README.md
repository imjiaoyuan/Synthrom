# RSS Reader

一个简单的 RSS 阅读器，支持分类查看订阅源的最新文章，并通过邮件通知更新。

## 功能特点

- 支持多个 RSS 源订阅
- 按分类（博客/资讯）整理文章
- 每日定时更新（中国时间：06:00, 11:00, 20:00）
- 邮件通知最新更新
- GitHub Issues 评论和收藏功能

## 配置说明

### RSS 源配置

在 `feed.list` 中配置 RSS 源，按分类组织：

```
Blog:
https://example.com/blog/feed
https://another-blog.com/rss.xml

News:
https://example.com/news/feed
https://news-site.com/atom.xml
```

格式说明：
- 使用分类名加冒号（如 `Blog:`）标记分类的开始
- 每个 RSS 源链接单独一行
- 空行会被自动忽略

### 邮件通知配置

1. 在 `config/email.yml` 中配置收件人：

```yaml
email:
  enabled: true                # 是否启用邮件通知
  recipients:                  # 收件人列表
    - your-email@example.com
```

2. 配置 SMTP 服务器信息：

在 GitHub 仓库中添加以下 Secrets：
- `SMTP_SERVER`: SMTP 服务器地址（如：smtp.qq.com）
- `SMTP_PORT`: SMTP 服务器端口（如：587）
- `SENDER_EMAIL`: 发件人邮箱
- `SENDER_PASSWORD`: 邮箱密码或授权码

### 邮件通知效果

- 按分类（Blog/News）组织文章
- 美观的响应式布局，支持桌面端和移动端
- 显示文章标题、来源、发布时间和摘要
- 支持直接点击链接访问原文

## 本地测试

1. 修改测试脚本中的邮箱配置：

编辑 `test.py`，修改以下配置：
```python
# 设置测试环境变量 (以QQ邮箱为例)
os.environ['SMTP_SERVER'] = 'smtp.qq.com'
os.environ['SMTP_PORT'] = '587'  # 也可以使用 465(SSL) 或 25
os.environ['SENDER_EMAIL'] = 'your-qq-number@qq.com'  # 替换为你的QQ邮箱
os.environ['SENDER_PASSWORD'] = 'your-auth-code'  # 替换为你的授权码
```

2. 运行测试：
```bash
python test_email.py
```

测试脚本会：
- 测试 SMTP 服务器连接
- 抓取订阅源文章
- 生成邮件预览
- 发送测试邮件

测试数据和预览文件将保存在 `test_data` 目录：
- `test_data/feed.json`: 抓取的文章数据
- `test_data/email_preview.html`: 邮件预览

## 自动化部署

项目使用 GitHub Actions 实现自动化部署：

1. 定时任务：每天北京时间 06:00, 11:00, 20:00 自动运行
2. 手动触发：可在 Actions 页面手动触发更新
3. 自动提交：更新后自动提交变更到仓库

## 许可证

MIT License