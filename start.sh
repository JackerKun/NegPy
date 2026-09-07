#!/usr/bin/env bash
# NegPy 快速启动 / 测试脚本
#
# 用法:
#   ./start.sh              启动应用(等同 make run)
#   ./start.sh test [参数]  运行测试,额外参数透传给 pytest
#                           例: ./start.sh test -k exposure -v
#   ./start.sh lint         ruff 检查 + 格式检查
#   ./start.sh check        lint + 测试(提交前完整校验)
#   ./start.sh help         显示本帮助
set -euo pipefail
cd "$(dirname "$0")"

usage() {
    sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
}

MODE="${1:-run}"
[ $# -gt 0 ] && shift

# .env.local 提供 NEGPY_USER_DIR 等个人环境变量(与 Makefile 行为一致)
if [ -f .env.local ]; then
    set -a
    . ./.env.local
    set +a
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "错误: 未找到 uv,请先安装:" >&2
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    echo "  详见 https://docs.astral.sh/uv/getting-started/installation/" >&2
    exit 1
fi

sync_deps() {
    # 扫描仪/相机可选依赖需要系统库;安装失败时降级,保证快速启动始终可用
    if ! uv sync --all-groups >/dev/null 2>&1; then
        echo "提示: 完整依赖安装失败(可能缺少系统库),降级为基础依赖(扫描/相机功能可能受限)" >&2
        uv sync --all-groups --no-group sane --no-group camera >/dev/null 2>&1 || uv sync >/dev/null
    fi
}

case "$MODE" in
    run)
        sync_deps
        echo "启动 NegPy..."
        exec uv run python desktop.py
        ;;
    test)
        sync_deps
        if [ "$(uname -s)" != "Darwin" ] && [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
            export QT_QPA_PLATFORM=offscreen
            echo "提示: 未检测到图形环境,以 offscreen 模式运行测试"
        fi
        echo "运行测试..."
        exec uv run pytest tests/ "$@"
        ;;
    lint)
        sync_deps
        echo "运行 lint..."
        uv run ruff check .
        uv run ruff format --check .
        echo "lint 通过"
        ;;
    check)
        sync_deps
        echo "运行 lint + 测试..."
        uv run ruff check .
        uv run ruff format --check .
        uv run pytest tests/ -q
        echo "全部检查通过"
        ;;
    help | -h | --help)
        usage
        ;;
    *)
        echo "未知模式: $MODE" >&2
        echo >&2
        usage >&2
        exit 1
        ;;
esac
