# Synthrom

一个简单的 RSS 阅读器，支持文章抓取、邮件推送等功能。

## 功能特点

- 支持文章分类管理
- GitHub Issues 评论和收藏
- 每天 6:00、11:00、20:00 (北京时间) 抓取文章
- 每天早上 8:00 (北京时间) 发送订阅邮件


## 使用方法

1. Fork 本仓库

2. 配置 GitHub Secrets：
   - `SMTP_SERVER`: SMTP 服务器地址
   - `SMTP_PORT`: SMTP 端口
   - `SENDER_EMAIL`: 发件人邮箱
   - `SENDER_PASSWORD`: 邮箱密码

3. 修改配置文件：
   - `config/email.yml`: 设置收件人邮箱
   - `feeds.yml`: 添加你想订阅的 RSS 源

4. 启用 GitHub Actions：
   - 进入仓库的 Settings > Actions > General
   - 在 "Workflow permissions" 部分选择 "Read and write permissions"
   - 点击 "Save" 保存设置