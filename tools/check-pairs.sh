#!/usr/bin/env bash
# 中英双语对目录一致性检查：xx.md 与 xx.en.md 必须位于同一目录。
#
# 拦截的事故：归档/移动文章时只移了一个语言版本，导致
#   - 另一语言版本滞留在原列表（可见性与配对断裂）
#   - 归档页缺少对应语言版本
#
# 用法：bash tools/check-pairs.sh   （本地或 CI，非 0 退出码 = 有违例）
set -uo pipefail
cd "$(dirname "$0")/.."

status=0
count=0
while IFS= read -r en; do
  count=$((count + 1))
  zh="${en%.en.md}.md"
  if [ ! -f "$zh" ]; then
    echo "❌ 配对断裂: $en 的同目录缺少 ${zh#content/}"
    status=1
  fi
done < <(find content -name "*.en.md" ! -name "_index.en.md" | sort)

if [ "$status" -eq 0 ]; then
  echo "✅ 双语配对一致（${count} 对）"
fi
exit "$status"
