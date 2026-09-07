#!/usr/bin/env bash
# NegPy 全平台发布打包脚本
#
# 用法:
#   ./publish.sh [版本号] [--skip-sane] [--with-tests]
#
#   版本号        可选;写入 VERSION 文件并用于打包命名(允许 v 前缀,如 v0.57.0)
#   --skip-sane   跳过 python-sane(缺少 SANE 系统库时用)
#   --with-tests  打包前先运行完整测试
#
# 环境变量:
#   NEGPY_MACOS_ARCH  macOS 目标架构(arm64 / x86_64),默认本机架构
#
# 各平台输出(在对应平台上生成):
#   macOS:   dist/NegPy.app + dist/NegPy-<版本>-macOS-<架构>.dmg
#   Linux:   dist/NegPy-<版本>-x86_64.AppImage(仅 x86_64)
#   Windows: dist/NegPy-<版本>-Win64-Setup.exe(需 NSIS,在 Git Bash 中运行)
set -euo pipefail
cd "$(dirname "$0")"

usage() {
    sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'
}

VERSION_ARG=""
SKIP_SANE=0
WITH_TESTS=0
for arg in "$@"; do
    case "$arg" in
        --skip-sane) SKIP_SANE=1 ;;
        --with-tests) WITH_TESTS=1 ;;
        -h | --help)
            usage
            exit 0
            ;;
        -*)
            echo "未知选项: $arg" >&2
            usage >&2
            exit 1
            ;;
        *) VERSION_ARG="$arg" ;;
    esac
done

case "$(uname -s)" in
    Darwin) PLATFORM=macos ;;
    Linux) PLATFORM=linux ;;
    MINGW* | MSYS* | CYGWIN*) PLATFORM=windows ;;
    *)
        echo "错误: 不支持的平台 $(uname -s)" >&2
        exit 1
        ;;
esac

if ! command -v uv >/dev/null 2>&1; then
    echo "错误: 未找到 uv,请先安装:" >&2
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 1
fi

if [ -n "$VERSION_ARG" ]; then
    echo "${VERSION_ARG#v}" >VERSION
fi
VERSION="$(cat VERSION)"
echo "==> 平台: $PLATFORM   版本: $VERSION"

SYNC_ARGS=(sync --all-groups)

if [ "$PLATFORM" = windows ]; then
    # SANE 无 Windows 构建,与 CI 一致
    SYNC_ARGS+=(--no-group sane)
    if ! command -v makensis >/dev/null 2>&1 &&
        [ ! -f "/c/Program Files (x86)/NSIS/makensis.exe" ] &&
        [ ! -f "/c/Program Files/NSIS/makensis.exe" ]; then
        echo "错误: 未找到 NSIS(makensis)。请先安装: choco install nsis -y" >&2
        exit 1
    fi
elif [ "$PLATFORM" = linux ]; then
    if [ "$(uname -m)" != x86_64 ]; then
        echo "提示: AppImage 打包只支持 x86_64(当前架构 $(uname -m)),打包可能失败" >&2
    fi
    command -v patchelf >/dev/null 2>&1 ||
        echo "提示: 缺少 patchelf(AppImage 需要): sudo apt-get install patchelf" >&2
    if command -v pkg-config >/dev/null 2>&1 && ! pkg-config --exists sane-backends 2>/dev/null; then
        echo "提示: 缺少 libsane 开发库: sudo apt-get install libsane-dev(或用 --skip-sane 跳过)" >&2
    fi
    if ! command -v appimagetool >/dev/null 2>&1 && [ ! -x ./appimagetool-x86_64.AppImage ]; then
        echo "==> 下载 appimagetool..."
        curl -fsSL -o appimagetool-x86_64.AppImage \
            https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
        chmod +x appimagetool-x86_64.AppImage
    fi
else
    if [ "$SKIP_SANE" = 0 ] && command -v brew >/dev/null 2>&1 && ! brew list --formula sane-backends >/dev/null 2>&1; then
        echo "提示: 未检测到 sane-backends(brew install sane-backends);若 python-sane 安装失败请加 --skip-sane 重试" >&2
    fi
fi

if [ "$SKIP_SANE" = 1 ]; then
    SYNC_ARGS+=(--no-group sane)
fi

# macOS 与 CI 一致:把 Homebrew 的头文件/库路径交给编译器
if [ "$PLATFORM" = macos ] && command -v brew >/dev/null 2>&1; then
    export CFLAGS="-I$(brew --prefix)/include"
    export LDFLAGS="-L$(brew --prefix)/lib"
fi

echo "==> 安装依赖..."
uv "${SYNC_ARGS[@]}"

if [ "$WITH_TESTS" = 1 ]; then
    echo "==> 运行测试..."
    uv run pytest tests/ -q
fi

echo "==> 清理 dist/ 并开始打包..."
rm -rf dist
uv run python build.py

checksum() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1"
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$1"
    fi
}

echo
echo "==> 打包完成,产物:"
case "$PLATFORM" in
    macos)
        [ -d dist/NegPy.app ] && echo "  App: dist/NegPy.app"
        for f in dist/*.dmg; do
            [ -f "$f" ] && echo "  DMG: $f" && checksum "$f"
        done
        echo
        echo "提示: 使用 ad-hoc 签名(无 Developer ID 证书),分发给他人后首次打开需右键 → 打开,"
        echo "      或执行: xattr -dr com.apple.quarantine /Applications/NegPy.app"
        ;;
    linux)
        for f in dist/*.AppImage; do
            [ -f "$f" ] && echo "  AppImage: $f" && checksum "$f"
        done
        ;;
    windows)
        for f in dist/*-Setup.exe; do
            [ -f "$f" ] && echo "  安装包: $f" && checksum "$f"
        done
        ;;
esac
