#!/bin/bash
# 小说初始化脚本
# 将 skill 目录下的模板复制到用户小说项目目录
# 用法: ./init-novel.sh <小说名或目录路径>
#   如果是相对路径（不含/），视为小说名，在当前目录下创建
#   如果是绝对路径或含/，直接作为目录路径

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

usage() {
    cat << EOF
用法: $(basename "$0") <小说名或目录>

为一部新小说初始化工作区。

示例:
  $(basename "$0") 逆天丹帝              # 在当前目录下创建逆天丹帝/
  $(basename "$0") /root/novels/逆天丹帝  # 在指定目录下创建

EOF
}

log_info() { echo -e "${GREEN}[信息]${NC} $1"; }
log_step() { echo -e "${CYAN}[步骤]${NC} $1"; }

NOVEL_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help) usage; exit 0 ;;
        -*) echo -e "${RED}[错误]${NC} 未知选项: $1"; usage; exit 1 ;;
        *) NOVEL_NAME="$1"; shift ;;
    esac
done

if [ -z "$NOVEL_NAME" ]; then
    echo -e "${RED}[错误]${NC} 请提供小说名或目录"
    usage
    exit 1
fi

# 判断是目录路径还是小说名
if [[ "$NOVEL_NAME" == *"/"* ]]; then
    # 包含/，视为完整路径，直接创建
    mkdir -p "$NOVEL_NAME"
    NOVEL_DIR="$(cd "$NOVEL_NAME" && pwd)"
else
    # 不含/，视为小说名，在当前目录下创建
    NOVEL_DIR="$(pwd)/$NOVEL_NAME"
    mkdir -p "$NOVEL_DIR"
    NOVEL_DIR="$(cd "$NOVEL_DIR" && pwd)"
fi

echo ""
echo -e "${CYAN}═══════════════════════════════════════${NC}"
echo -e "${CYAN}  爽文小说生成器 - 初始化工作区${NC}"
echo -e "${CYAN}═══════════════════════════════════════${NC}"
echo ""
echo -e "  项目目录: ${GREEN}${NOVEL_DIR}${NC}"
echo ""

log_step "创建项目目录..."
mkdir -p "$NOVEL_DIR/output"

log_step "复制模板文件..."
cp -r "$SKILL_DIR/.learnings/" "$NOVEL_DIR/.learnings"
cp -r "$SKILL_DIR/references/" "$NOVEL_DIR/references"
mkdir -p "$NOVEL_DIR/scripts"
cp "$SKILL_DIR/scripts/"*.py "$NOVEL_DIR/scripts/"

echo ""
log_info "初始化完成！"
echo ""
echo "项目结构:"
echo "  ${NOVEL_DIR}/"
echo "  ├── output/          # 章节输出"
echo "  ├── .learnings/      # 记忆文件"
echo "  ├── references/      # 参考指南"
echo "  └── scripts/         # 脚本"
echo ""
echo "后续步骤:"
echo "  1. 向 AI 代理描述你的小说方向/题材"
echo "  2. 代理会自动完善提示词，保存到 output/提示词.md"
echo "  3. 确认提示词后，代理生成大纲到 output/大纲.md"
echo "  4. 逐章生成，每章保存为 output/第XX章_章名.md"
echo ""
