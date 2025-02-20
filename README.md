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

在 `config/feeds.yml` 中配置 RSS 源：

```yaml
feeds:
  - category: Blog
    url: https://example.com/feed
    name: 示例博客
  
  - category: News
    url: https://example.com/news/feed
    name: 示例新闻
```

### 邮件通知配置

1. 在 `config/email.yml` 中配置收件人：

```yaml
email:
  enabled: true                # 是否启用邮件通知
  recipients:                  # 收件人列表
    - your-email@example.com
```

2. 在 GitHub 仓库添加必要的 Secrets：

   1. 进入仓库 Settings -> Security -> Secrets and variables -> Actions
   2. 点击 "New repository secret" 按钮
   3. 添加以下 4 个 Repository secrets：

   - `SMTP_SERVER`: SMTP 服务器地址（如：smtp.gmail.com）
   - `SMTP_PORT`: SMTP 服务器端口（如：587）
   - `SENDER_EMAIL`: 用于发送邮件的邮箱地址
   - `SENDER_PASSWORD`: 邮箱密码或应用专用密码
     - 如果使用 Gmail，需要使用应用专用密码
     - 可在 Google 账号设置 -> 安全性 -> 2 步验证 -> 应用专用密码 中生成

## 本地测试

1. 测试邮件模板：
```bash
python test_email_template.py
```
生成的 `email_preview.html` 文件可用浏览器打开预览邮件效果。

2. 测试抓取文章：
```bash
python fetch_feeds.py
```

## 自动化部署

项目使用 GitHub Actions 实现自动化部署：

1. 定时任务：每天北京时间 06:00, 11:00, 20:00 自动运行
2. 手动触发：可在 Actions 页面手动触发更新
3. 自动提交：更新后自动提交变更到仓库

## 许可证

MIT License