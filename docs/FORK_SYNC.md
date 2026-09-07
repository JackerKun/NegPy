# Fork 同步与翻译流程

本文件描述如何把上游 NegPy 的更新合并进本 fork,给新增界面字符串补中文翻译,再推送到 `JackerKun/NegPy`。本 fork 相对上游的唯一长期差异是**界面语言功能(i18n)**:英文为源语言,简体中文经 `tr()` 运行时查表翻译。

> 这是 fork 维护文档,不是上游 NegPy 的产品文档。上游没有本文件,合并时不会冲突。

## 角色

| 名称 | 仓库 | 用途 |
|---|---|---|
| `upstream` | `marcinz606/NegPy` | 原作者仓库。只 `fetch`,永不 `push`。 |
| `origin` | `JackerKun/NegPy` | 你的 fork。推送目标,也是云端备份。 |

一次性配置(已完成,列出仅供新克隆时参考):

```bash
git remote rename origin upstream
git remote add origin https://github.com/JackerKun/NegPy.git
git fetch upstream && git fetch origin
```

上次同步基点记录在 `.git/fork-sync-base`(由 `i18n_audit.py mark-synced` 写入),当前为上游 0.58.0(`e8dc997`)。

## 关键文件

| 文件 | 作用 |
|---|---|
| `negpy/kernel/system/i18n.py` | `tr()`、`set_language()`。英文与缺失 key 回退为原文。 |
| `negpy/kernel/system/i18n_zh.py` | 中文目录 `STRINGS`(约 1688 key)。`# fmt: off` 区块,ruff 不重排。 |
| `negpy/desktop/main.py` | 启动时 `set_language()`,读全局设置 `language`。 |
| `i18n_audit.py` | 本 fork 的审计工具:查重、列出待翻译新字符串、记录基点。 |

## 定期同步流程

### 第 0 步 · 前置检查

```bash
git status --short        # 必须干净;有改动先提交或 stash
git switch main
```

### 第 1 步 · 拉取上游

```bash
git fetch upstream
git log --oneline main..upstream/main    # 看看上游新增了什么
```

### 第 2 步 · 列出待翻译字符串(合并前)

**必须在 `git merge` 之前运行。** 此时 `main` 与 `upstream/main` 的 merge-base 就是上次同步点,脚本据此列出上游新增/改动、且尚未翻译的英文界面字符串。

```bash
uv run python i18n_audit.py new-strings
```

脚本用 AST 比对 `upstream/main` 与基点的文件差异:自动折叠多行隐式拼接、跳过 docstring、f-string 片段和测试文件;并跳过三个**故意保留英文**的预启动文件(见下方"注意事项")。输出即本次要翻译的工作清单。记住这份清单。

### 第 3 步 · 合并上游

```bash
git merge upstream/main --no-edit
```

### 第 4 步 · 解决冲突

原则:**上游逻辑为准,重新套上 `tr()`。**

- 上游改了某段代码、而本 fork 在同一处包了 `tr()`:采用上游的新代码,再把其中的用户可见字符串重新用 `tr()` 包起来。
- 模块级常量(如对话框的 `_GROUPS` 表)保持英文原文,**不要**在定义处包 `tr()`;翻译发生在渲染点(`tr(title)`、`tr(label)` 等)。若上游改了常量的英文文本,只需更新目录里的 key(见第 5 步),渲染点无需动。
- 内联字符串(如 `QLabel("...")`、`setToolTip("...")`)直接在原位包 `tr()`。

冲突标记清理后:

```bash
grep -rn '<<<<<<<\|>>>>>>>' negpy/ --include='*.py'   # 应无输出
git add <解决的文件>
git commit --no-edit                                   # 完成合并提交
```

### 第 5 步 · 补翻译

对第 2 步清单里的每条字符串,在 `i18n_zh.py` 里处理:

- **新增字符串**:加一条 `"英文原文": "中文",`。多行拼接的字符串,key 用**拼接后的完整文本**(源码里也可写成同样的隐式拼接,便于对照)。
- **上游改动的字符串**:英文原文变了,旧 key 作废。把旧条目的 key 换成新英文文本并更新中文,不要留孤儿 key。
- 放在语义相邻的分组注释下(如相机相关放 `# ---- ... camera ... ----` 附近)。

术语遵循下方**术语表**;同一概念在所有面板用同一词,新增标签前先 `grep` 现有译法。

### 第 6 步 · 验证

```bash
# 6.1 目录查重 + 确认无待翻译遗留(此时已合并,显式传上一个基点)
uv run python i18n_audit.py duplicates
uv run python i18n_audit.py new-strings <第2步用的基点>

# 6.2 格式化 + lint(CLAUDE.md 要求提交前必跑)
make format

# 6.3 完整测试(唯一失败应仅是既有的 macOS 专有项,见注意事项)
QT_QPA_PLATFORM=offscreen uv run pytest tests/ -q

# 6.4 运行时翻译抽检:新控件在 zh_CN 下确实显示中文
```

6.4 抽检脚本(把 `_GROUPS`、新标签换成当次涉及的对象):

```bash
NEGPY_USER_DIR=/tmp/negpy-check QT_QPA_PLATFORM=offscreen uv run python - <<'PY'
from PyQt6.QtWidgets import QApplication
app = QApplication([])
from negpy.kernel.system.i18n import set_language, tr
set_language('zh_CN')
for s in ["Shadow Reach", "Highlight Hold", "Delay between exposures"]:
    assert tr(s) != s, f"未翻译: {s}"
    print(f"{s!r} -> {tr(s)}")
print("zh OK")
set_language('en')
assert tr("Shadow Reach") == "Shadow Reach"
print("en identity OK")
PY
```

如需整窗口冒烟(可选):用 `main()` 的装配链离线构建主窗口——`StorageRepository(...)` → `repo.initialize()` → `DesktopSessionManager(repo)` → `AppController(sm)` → `MainWindow(ctrl)`,`win.show()` 不报错即通过。

### 第 7 步 · 提交翻译

```bash
git add negpy/kernel/system/i18n_zh.py <其他改动文件>
git commit -m "feat(i18n): translate upstream <版本> strings

<一句话说明本次新增/改动了哪些界面字符串>

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

### 第 8 步 · 记录基点并推送

```bash
uv run python i18n_audit.py mark-synced     # 把本次上游 tip 记为下次基点
```

推送到 fork。**用一次性内联 token,不要写进 `.git/config`**:

```bash
TOKEN='<你的 PAT>'
git push "https://JackerKun:${TOKEN}@github.com/JackerKun/NegPy.git" main:main
unset TOKEN
```

推送后确认无 token 残留:

```bash
git remote get-url origin          # 应为纯净 HTTPS URL
grep -c 'ghp_' .git/config || echo "config clean"
```

> **Token 安全**:PAT 一旦出现在聊天/命令里就视为泄露,用完到 GitHub → Settings → Developer settings → Personal access tokens **撤销并重新生成**。更稳妥的做法是用 `gh auth login` 或系统凭据管理器,避免每次粘贴 token。

## 术语表(已裁定,新增翻译须沿用)

| 英文 | 中文 | | 英文 | 中文 |
|---|---|---|---|---|
| Process | 工艺 | | Scan | 扫描 |
| Library | 图库 | | Trichrome Scan | 三色扫描 |
| Contact Sheet | 接触印相 | | Half Frame | 半格 |
| Camera | 相机 | | Soft Proof | 软打样 |
| Dilution | 稀释比 | | Flat master | 平扫母版 |
| Push / Pull | 迫冲 / 迫减 | | Film stock | 胶片 |
| Saved setup | 已保存的配置 | | Auto Grade | 自动反差等级 |

## 注意事项

- **导入期规则**:`tr()` 只在运行时调用。模块级常量保持英文,在渲染点包装。`label_with_shortcut` / `tooltip_with_shortcut` 先把文本参数包好再传入:`label_with_shortcut(tr("Pick WB"), "pick_wb")`。
- **英文源文本逐字节不变**:测试会断言英文原文。改英文措辞会破坏测试;翻译只加在目录里,不动源码英文。
- **故意保留英文的三个文件**:`windows_data_dialog.py`、`startup.py`、`user_directory.py`。它们在 Qt 之前、在数据目录(存着语言设置)可读之前运行,是 Windows 数据目录恢复的兜底对话框,无法也无需翻译。`i18n_audit.py` 已内置排除。
- **恒等条目**:ISO、DPI、TIFF、CLAHE、化学药剂名(Selenium/Sepia/Gold 等)、纯模板(`{phase}… %p%`)、`Snap` 等有意不进目录,靠 `tr()` 回退显示原文。
- **既有 macOS 专有测试失败**:`test_metadata_presets.py::test_load_tooltip_follows_a_rebinding` 在未改动的上游 HEAD 上同样失败(Qt 在 macOS 把 `Ctrl+Shift+L` 渲染成 `⇧⌘L`)。与 i18n 和同步无关,不必修。
- **复数形式**:用两个模板 `tr("{n} file")` / `tr("{n} files")` + `.format(n=...)`,两个分支都要 `.format`。
- **图标按钮标签的前导空格**:key 与 value 都要逐字节保留。

## 交给 Claude 执行

以后需要再同步时,直接说"执行 fork 同步流程"或"按 `docs/FORK_SYNC.md` 同步上游并翻译"。届时提供有效的 PAT(或已配置好 `gh auth`),Claude 会按第 0–8 步执行,并在翻译环节沿用上表术语与规则。
