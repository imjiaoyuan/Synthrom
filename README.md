# RSS Reader

一个简单的 RSS 阅读器，支持分类查看订阅源的最新文章。

## 功能特点

- 支持自定义分类和标签显示
- 响应式设计，支持移动端浏览
- 自动跟随系统的暗色模式
- 每小时自动更新文章
- 支持一键发起 GitHub Issue 进行评论
- 支持一键收藏文章到 GitHub Issue
- 支持自定义每个分类的文章显示方式和数量限制
- 支持已读/未读文章状态管理
- 本地保存阅读状态
- 纯静态页面，无需后端服务
- 支持 PWA，可添加到主屏幕
- 使用 GitHub Actions 自动更新文章

## 使用方法

1. Fork 本仓库
2. 修改配置文件
3. 在仓库的 Settings -> Pages 中开启 GitHub Pages
4. 访问 `https://你的用户名.github.io/RSS` 即可阅读

## 配置说明

### RSS 源配置

编辑 `feed.list` 文件，按分类添加 RSS 源的地址：

```
Blog:
https://example1.com/feed
https://example2.com/rss

Information:
https://news1.com/feed
https://news2.com/rss

Forums:
https://forum1.com/feed
https://forum2.com/rss
```

### 标签显示配置

编辑 `config/labels.yml` 文件，自定义每个分类的显示方式：

```yaml
labels:
  - feed_category: Blog        # feed.list中的分类名
    display_name: 博客         # 主页显示的标签名
    icon: mdi-post            # 标签图标
    show_date_divider: true   # 是否显示今日/历史分类
    article_limit: 60         # 每个源抓取的文章数量限制

  # ... 其他分类配置
```

### GitHub 功能配置

编辑 `config/github.yml` 文件，配置评论和收藏功能：

```yaml
github:
  repository: username/repo    # 你的GitHub仓库地址

  comment:
    enabled: true             # 是否启用评论功能
    label: comment           # 评论issue的标签
    title_template: "{title} ({date})"
    body_template: "{summary}\n\n链接：{link}"

  favorite:
    enabled: true            # 是否启用收藏功能
    label: favorite         # 收藏issue的标签
    title_template: "{title} ({date})"
    body_template: "{summary}\n\n链接：{link}"
```

## 调试说明

本地调试时，可以使用 Python 的内置 HTTP 服务器：

```bash
# 在 RSS 目录下运行
python3 -m http.server 8000

# 然后在浏览器访问
http://localhost:8000
```

## 自定义配置

- 修改 `static/style.css` 自定义界面样式
- 修改 `fetch_feeds.py` 自定义文章获取逻辑
- 修改 `index.html` 自定义页面结构和功能
- 修改配置文件自定义功能行为

## 许可证

MIT License