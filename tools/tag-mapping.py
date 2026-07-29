#!/usr/bin/env python3
"""
标签映射脚本：为翻译文章添加对应的中英文标签

使用方法：
    python3 tag-mapping.py [--dry-run]

示例：
    python3 tag-mapping.py --dry-run  # 预览
    python3 tag-mapping.py            # 执行
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# 标签映射表：中文 ↔ 英文
TAG_MAPPING: Dict[str, str] = {
    # 经验教训类
    "经验教训": "Lessons Learned",
    "踩坑记录": "Troubleshooting",
    "故障排查": "Debugging",
    "排查": "Troubleshooting",

    # 工具类
    "工具": "Tools",
    "工具链": "Toolchain",
    "工具对比": "Tool Comparison",

    # 开发类
    "开源项目": "Open Source",
    "工程规范": "Engineering Practices",
    "编程助手": "Coding Assistant",
    "包管理": "Package Management",

    # 调研类
    "调研": "Research",
    "隐私": "Privacy",
    "数据训练": "Data Training",

    # 技术类
    "推理": "Inference",
    "本地推理": "Local Inference",

    # 其他
    "密码重置": "Password Reset",
    "远程桌面": "Remote Desktop",
    "博客配置": "Blogging",
}

# 反向映射：英文 → 中文
REVERSE_TAG_MAPPING: Dict[str, str] = {v: k for k, v in TAG_MAPPING.items()}


def extract_tags_from_frontmatter(content: str) -> List[str]:
    """从 frontmatter 中提取标签列表"""
    # 匹配 [taxonomies]\n    tags = [...] 格式
    pattern = r'\[taxonomies\]\s+tags\s*=\s*\[(.*?)\]'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        # 尝试匹配 tags = [...] 格式（旧格式）
        pattern = r'^tags\s*=\s*\[(.*?)\]'
        match = re.search(pattern, content, re.MULTILINE)

    if match:
        tags_str = match.group(1)
        # 提取所有标签（支持单引号和双引号）
        tags = re.findall(r'["\']([^"\']+)["\']', tags_str)
        return tags
    return []


def update_tags_in_frontmatter(content: str, new_tags: List[str]) -> str:
    """更新 frontmatter 中的标签列表"""
    # 匹配 [taxonomies]\n    tags = [...] 格式
    pattern = r'(\[taxonomies\]\s+tags\s*=\s*\[)(.*?)(\])'

    def replace_tags(match):
        # 格式化标签列表
        tags_str = ', '.join(f'"{tag}"' for tag in new_tags)
        return f'{match.group(1)}{tags_str}{match.group(3)}'

    new_content = re.sub(pattern, replace_tags, content, flags=re.DOTALL)

    if new_content == content:
        # 尝试匹配旧格式
        pattern = r'(^tags\s*=\s*\[)(.*?)(\])'
        new_content = re.sub(pattern, replace_tags, content, flags=re.MULTILINE | re.DOTALL)

    return new_content


def get_translation_tags(zh_tags: List[str], en_tags: List[str]) -> Tuple[List[str], List[str]]:
    """获取需要添加的翻译标签"""
    zh_tags_set = set(zh_tags)
    en_tags_set = set(en_tags)

    # 中文文章需要添加的英文标签
    en_tags_to_add = set()
    for zh_tag in zh_tags:
        if zh_tag in TAG_MAPPING:
            en_tag = TAG_MAPPING[zh_tag]
            if en_tag not in zh_tags_set:
                en_tags_to_add.add(en_tag)

    # 英文文章需要添加的中文标签
    zh_tags_to_add = set()
    for en_tag in en_tags:
        if en_tag in REVERSE_TAG_MAPPING:
            zh_tag = REVERSE_TAG_MAPPING[en_tag]
            if zh_tag not in en_tags_set:
                zh_tags_to_add.add(zh_tag)

    return list(en_tags_to_add), list(zh_tags_to_add)


def process_translation_pair(zh_file: Path, en_file: Path, dry_run: bool = False) -> bool:
    """处理一对翻译文章"""
    try:
        zh_content = zh_file.read_text(encoding='utf-8')
        en_content = en_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  ❌ 读取失败: {e}")
        return False

    zh_tags = extract_tags_from_frontmatter(zh_content)
    en_tags = extract_tags_from_frontmatter(en_content)

    if not zh_tags or not en_tags:
        return False

    en_tags_to_add, zh_tags_to_add = get_translation_tags(zh_tags, en_tags)

    if not en_tags_to_add and not zh_tags_to_add:
        return False

    print(f"  📝 {zh_file.name}")
    print(f"     中文标签: {zh_tags}")
    print(f"     英文标签: {en_tags}")

    if en_tags_to_add:
        print(f"     ➕ 中文文章添加: {en_tags_to_add}")
    if zh_tags_to_add:
        print(f"     ➕ 英文文章添加: {zh_tags_to_add}")

    if not dry_run:
        # 更新中文文章
        new_zh_tags = zh_tags + en_tags_to_add
        new_zh_content = update_tags_in_frontmatter(zh_content, new_zh_tags)
        zh_file.write_text(new_zh_content, encoding='utf-8')

        # 更新英文文章
        new_en_tags = en_tags + zh_tags_to_add
        new_en_content = update_tags_in_frontmatter(en_content, new_en_tags)
        en_file.write_text(new_en_content, encoding='utf-8')

        print(f"     ✅ 已更新")

    return True


def main():
    dry_run = '--dry-run' in sys.argv

    posts_dir = Path('/home/cncsmonster/my-docs/cncsmonster.github.io/content/posts')

    print("=" * 80)
    print("标签映射工具")
    print("=" * 80)
    print(f"模式: {'预览' if dry_run else '执行'}")
    print(f"目录: {posts_dir}")
    print(f"映射表: {len(TAG_MAPPING)} 个标签")
    print("=" * 80)

    updated_count = 0
    total_pairs = 0

    # 找出所有翻译文章对
    for en_file in sorted(posts_dir.glob('*.en.md')):
        zh_file = en_file.parent / f"{en_file.name.replace('.en.md', '.md')}"
        if zh_file.exists():
            total_pairs += 1
            if process_translation_pair(zh_file, en_file, dry_run):
                updated_count += 1

    print("\n" + "=" * 80)
    print(f"翻译文章对总数: {total_pairs}")
    print(f"需要更新: {updated_count}")
    print("=" * 80)

    if updated_count > 0 and not dry_run:
        print("✅ 标签映射完成！")
        print("   请运行 `zola build` 重新构建站点")
    elif updated_count > 0 and dry_run:
        print("👆 以上文章将被更新（当前为预览模式）")
        print("   移除 --dry-run 参数以实际更新")
    else:
        print("ℹ️  没有需要更新的文章")

    sys.exit(0)


if __name__ == '__main__':
    main()
