# 信奥课程阅读库

网站：<https://zcxxcz.github.io/xinao-courses/>

38 讲课程，8 个主题。首页保留总索引与阅读路线，每讲包含图文对照、精编讲稿、完整讲稿；另有七讲总结和归档清单。适配电脑与手机，支持课程标题筛选、页内目录、原尺寸图片阅读、Markdown 下载。

课程来源为 FayeTY（啊粥粥）的公开 Bilibili 视频及其本地整理，原视频链接保留在课程页。讲稿为自动转录与整理，观点、年份和案例以原材料为准。原始内容权利归相应作者所有。

## 文件结构

- `content/`：可维护的 Markdown 文本，采用网站内相对路径。
- `site-assets/`：样式、脚本与无损 WebP 课程图片，保持原图尺寸。
- `catalog.json`：课程、版本与图片元信息，无个人电脑路径。
- `scripts/import_courses.py`：从指定的本地课程目录导入总索引所引用的内容。
- `scripts/build.py`：生成 `docs/` 并检查本地链接、图片与页内锚点。
- `docs/`：GitHub Pages 发布目录，纯静态文件，无运行时依赖、统计或第三方字体。

## 本地预览

可直接修改 `content/`。可选本地验证：安装 requirements.txt 后运行 `python scripts/build.py`；预览使用 `python -m http.server 8765 --directory docs`。正式发布由云端构建 docs，不需要提交本地产物。导入课程时运行 `python scripts/import_courses.py /path/to/raw/courses`，不要上传整个个人知识库。

## 统一发布与内容索引

总入口：https://zcxxcz.github.io/ 。本项目通过公开 `catalog.json` 接入全文搜索。`publish.json` 显式列出公开内容，不包含账号数据。

Windows/macOS 均安装 Node.js 24、Git 与 GitHub CLI，先 `gh auth login`。使用独立任务分支，提交本任务文件后运行 `npm run publish`：创建 PR → 等待 Publish Pages 检查 → 自动合并 → GitHub Actions 构建发布 → 自动刷新总索引。工作区必须干净；main 更新时先合并最新 main 并解决冲突。不需要本地运行 gh-pages。

Pages Source 使用 GitHub Actions，正式产物只由云端构建。直接推送 main 后，总索引由每日补漏任务更新；需要立即更新则运行 `node scripts/publish.mjs --refresh-only`。不自动执行数据库迁移。新增或修改公开内容时同步 publish.json 的元信息和 textPaths；不得将私人文件加入索引。
