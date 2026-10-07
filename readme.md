# CCM's Personal Homepage

A personal homepage built with [Zola](https://www.getzola.org/), featuring:

- ✍️ **Blog Posts** - Technical articles, tutorials, and retrospectives
- 📚 **E-books** - Systematic learning notes (mdBook)
- 🚀 **Open Source** - My open source projects and contributions
- 🗄️ **Archive** - Outdated content for historical reference

## Features

- ⚡ Fast static site generation with Zola (Rust)
- 📱 Responsive design
- 🔍 **Built-in search with Chinese support** (中文搜索)
- 📊 **Mermaid diagrams** (流程图、序列图、类图等)
- 💬 Comment support via Giscus
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
│   ├── posts/               # Blog posts (technical articles, tutorials, retrospectives)
│   ├── open-source/         # Open source projects and contribution records
│   ├── ebooks/              # E-books and systematic learning notes (mdBook)
│   └── archive/             # Archived/outdated content for historical reference
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

> ⚠️ `github-notes/` has been removed. Reading notes are now managed as e-books under `ebooks/` or as blog posts in `posts/`.

### New E-book

Create a new directory under `content/ebooks/`:

```markdown
# content/ebooks/<book-name>/_index.md
+++
title = 'Book Name'
sort_by = 'weight'
+++

# Book Title

Reading notes and systematic learning content.
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

### Archive Outdated Content

When a post becomes outdated (project discontinued, replaced by a better approach), **archive it instead of deleting it** — old bookmarks must keep working. Four steps:

1. **Move both language versions** out of the post list:

   ```bash
   git mv content/posts/<file>.md content/archive/
   git mv content/posts/<file>.en.md content/archive/   # if it exists
   ```

2. **Front matter** — add `aliases` (no `weight` needed: the archive list sorts by `date`, which every post has — a page missing `date` is not built at all, and CI treats that warning as a failure):

   ```toml
   +++
   title = "Old Post"
   date = 2024-01-01T00:00:00+08:00
   aliases = ["/posts/<old-slug>/"]   # zh page; the .en.md uses "/en/posts/<old-slug>/"
   +++
   ```

   The alias generates a redirect page at the old URL, so existing bookmarks land on the archive page (the URL hash is preserved). Where to find the old slug:

   - the `slug` front-matter field of the post, or
   - the directory name under `public/posts/` from the old build, or
   - build the filename in a scratch Zola site — Chinese filenames become pinyin (e.g. `使用fgm管理Go版本` → `shi-yong-fgmguan-li-goban-ben`); posts published before the 2026-04 Hugo→Zola migration may instead use percent-encoded Unicode.

   > An archived slug + alias is **permanently reserved** — never reuse it for a new post. Zola fails the build on path collisions, so CI catches the mistake (rename the new post).

3. **Archive banner** at the top of the body (bilingual): why it is archived + what replaces it + confirmation the link still works:

   ```markdown
   > ⚠️ **注意：这篇文章已归档**
   >
   > `<project>` 已停止维护，本方案已被 **`<replacement>`** 取代。
   > 本文仅供历史参考，请勿再按文中方式使用。
   ```

4. **Verify**:

   ```bash
   bash tools/check-pairs.sh   # both language versions moved together (CI runs this too)
   zola build                  # 0 errors; CI fails the deploy on ANY warning
   # public/posts/<old-slug>/index.html exists (redirect to /archive/...)
   # public/archive/<slug>/index.html contains the archive banner
   # post gone from public/posts/index.html, listed in public/archive/index.html
   ```

> Do **not** add a fictional `archived = true` front-matter field — no template reads it. Visibility is controlled purely by directory (`posts/` vs `archive/`) plus the banner.

## Configuration

Edit `config.toml` to customize:

- Site title and URL
- Author information
- GitHub username
- Comment system (Giscus)

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
