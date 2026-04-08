# CCM's Personal Homepage

A personal homepage built with [Zola](https://www.getzola.org/), featuring:

- 📚 **GitHub Notes** - Reading notes from technical books
- ✍️ **Blog Posts** - Technical articles and tutorials
- 🚀 **Open Source** - My open source projects and contributions

## Features

- ⚡ Fast static site generation with Zola (Rust)
- 📱 Responsive design
- 🔍 **Built-in search with Chinese support** (中文搜索)
- 📊 **Mermaid diagrams** (流程图、序列图、类图等)
- 💬 Comment support via Giscus
- 📊 Visitor counter
- 🔄 Auto-deployment via GitHub Actions

## Prerequisites

- [Zola](https://www.getzola.org/documentation/getting-started/installation/) v0.19+

## Installation

### Install Zola

**Option 1: Using cargo (recommended)**

```sh
cargo install zola
```

**Option 2: Download pre-built binary**

```sh
# Linux
curl -L -o zola.tar.gz https://github.com/getzola/zola/releases/latest/download/zola-linux-x86_64-gnu.tar.gz
tar xzf zola.tar.gz
sudo mv zola /usr/local/bin/

# macOS
brew install zola

# Windows
# Download from https://github.com/getzola/zola/releases
```

### Verify Installation

```sh
zola --version
```

## Local Development

```sh
# Start development server (localhost only)
zola serve

# Start with LAN access (replace with your IP)
zola serve --interface 0.0.0.0 --port 1111

# Or use your specific LAN IP
zola serve --interface 192.168.1.100 --port 1111

# Open in browser
# - Local: http://localhost:1111
# - LAN: http://<your-ip>:1111
```

## Build for Production

```sh
# Build the site
zola build

# Output will be in the ./public directory
```

## Project Structure

```
.
├── config.toml              # Site configuration
├── content/
│   ├── posts/               # Blog posts
│   ├── github-notes/        # Reading notes
│   └── open-source/         # Open source projects
├── static/
│   ├── sass/                # SCSS stylesheets
│   └── js/                  # JavaScript files
├── templates/               # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── page.html
│   ├── section.html
│   └── ...
└── .github/workflows/       # GitHub Actions
```

## Content Creation

### New Blog Post

Create a new file in `content/posts/`:

```markdown
+++
title = 'Your Post Title'
date = 2024-01-01T00:00:00+08:00
tags = ['tag1', 'tag2']
+++

Your content here...
```

### New GitHub Note

Create a new file in `content/github-notes/`:

```markdown
+++
title = 'Book Name Notes'
date = 2024-01-01T00:00:00+08:00
tags = ['Book', 'Notes']
+++

Your reading notes...
```

### New Open Source Project

Create a new file in `content/open-source/`:

```markdown
+++
title = 'Project Name'
date = 2024-01-01T00:00:00+08:00
tags = ['Language', 'Project']
+++

Project description...
```

## Configuration

Edit `config.toml` to customize:

- Site title and URL
- Author information
- GitHub username
- Comment system (Giscus)
- Visitor counter

### Enable Comments (Giscus)

Giscus 配置信息都是**公开的**，可以安全地明文配置在代码库中：

```toml
[extra]
giscus_enabled = true
giscus_repo = "your-username/your-repo"       # 仓库名
giscus_repo_id = "R_..."                      # 仓库 ID（通过 API 获取）
giscus_category = "General"                   # 分类名称
giscus_category_id = "DIC_..."                # 分类 ID（通过 API 获取）
```

**获取配置信息：**

```bash
# 获取 Repo ID
gh repo view your-username/your-repo --json id

# 获取 Category ID
gh api graphql -f query='query {
  repository(owner: "your-username", name: "your-repo") {
    discussionCategories(first: 10) {
      nodes { id name slug }
    }
  }
}'
```

**前提条件：**
1. 启用 GitHub Discussions 功能
2. 安装 Giscus GitHub App: https://github.com/apps/giscus

## Deployment

The site is automatically deployed to GitHub Pages when you push to the `main` branch.

## License

- **Code** (templates, styles, configuration): [MIT License](LICENSE)
- **Content** (blog posts, notes): [CC BY-NC-SA 4.0](LICENSE-CONTENT)

### 许可证说明

- **代码部分**：使用 MIT 协议，你可以自由使用、修改、分发
- **文章内容**：使用 CC BY-NC-SA 4.0 协议
  - ✅ 可以分享、修改
  - ✅ 需要署名（注明原作者和原文链接）
  - ❌ 禁止商业用途
  - ✅ 相同方式共享（衍生作品需使用相同协议）
