# 信奥课程阅读库

网站：<https://zcxxcz.github.io/xinao-courses/>

37 讲课程，8 个主题。首页保留总索引与阅读路线，每讲包含图文对照、精编讲稿、完整讲稿；另有七讲总结和归档清单。适配电脑与手机，支持课程标题筛选、页内目录、原尺寸图片阅读、Markdown 下载。

课程来源为 FayeTY（啊粥粥）的公开 Bilibili 视频及其本地整理，原视频链接保留在课程页。讲稿为自动转录与整理，观点、年份和案例以原材料为准。原始内容权利归相应作者所有。

## 文件结构

- `content/`：可维护的 Markdown 文本，采用网站内相对路径。
- `site-assets/`：样式、脚本与无损 WebP 课程图片，保持原图尺寸。
- `catalog.json`：课程、版本与图片元信息，无个人电脑路径。
- `scripts/import_courses.py`：从指定的本地课程目录导入总索引所引用的内容。
- `scripts/build.py`：生成 `docs/` 并检查本地链接、图片与页内锚点。
- `docs/`：GitHub Pages 发布目录，纯静态文件，无运行时依赖、统计或第三方字体。

## 更新与发布

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
# 如果要从知识库同步，传入自己的 raw/courses 目录：
.venv/bin/python scripts/import_courses.py /path/to/raw/courses
.venv/bin/python scripts/build.py
# 检查结果后提交并推送；GitHub Pages 从 main 分支的 /docs 自动发布。
git add content site-assets catalog.json docs validation.json
git commit -m "Update course library"
git push
```

也可以直接修改 `content/` 后运行构建。导入器目前会校验 37 讲结构，新增课程时应同时检查索引分类和导入规则。不要上传整个个人知识库。

本地预览：`python3 -m http.server 8765 --directory docs`。
