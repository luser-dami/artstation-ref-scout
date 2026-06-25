# ArtStation Ref Scout

一键搜索 ArtStation，获取美术参考素材。基于官方 API v2，无需登录，无反爬问题。

```
pip install --user git+https://github.com/luser-dami/artstation-ref-scout.git
as-scout --kw "cyberpunk chinese" --cat environment --pages 2
```

输出：项目标题、作者、封面缩略图、ArtStation 直链，自动生成 Markdown 报告。

## 安装

```bash
pip install --user git+https://github.com/luser-dami/artstation-ref-scout.git
```

国内加速：
```bash
pip install --user git+https://github.com/luser-dami/artstation-ref-scout.git -i https://pypi.tuna.tsinghua.edu.cn/simple
```

升级：
```bash
pip install --user --upgrade git+https://github.com/luser-dami/artstation-ref-scout.git
```

## 用法

```bash
# 基本搜索
as-scout --kw "cyberpunk chinese" --pages 2

# 按分类过滤（environment / character_design / game_art / 3d_modeling / concept_art / illustration）
as-scout --kw "cyberpunk" --cat environment

# 指定输出目录
as-scout --kw "cyberpunk" --outdir ~/art-refs

# 使用代理（国内访问 ArtStation API 可能需要）
HTTPS_PROXY=http://127.0.0.1:7897 as-scout --kw "cyberpunk"
as-scout --kw "cyberpunk" --proxy http://127.0.0.1:7897

# 更多页
as-scout --kw "cyberpunk" --pages 5
```

## 输出

```
~/art-refs/<关键词>/
├── index.json    # 完整结构化数据
└── report.md     # Markdown 报告（含预览图 + 直链）
```

`report.md` 打开即用（VS Code / Typora / GitHub 都渲染缩略图），点击 🔗 跳转 ArtStation 原页看大图。

## 关键词建议

ArtStation 搜索对英文关键词效果更好。中文场景请翻译：

| 中文 | 推荐英文关键词 |
|------|---------------|
| 国风/古风 | chinese traditional, wuxia, dynasty, tang dynasty |
| 赛博朋克 | cyberpunk, cyber, neon |
| 废土 | post-apocalyptic, wasteland, fallout |
| 奇幻 | fantasy, medieval, magic |
| 机器人 | robot, mecha, android, sci-fi |
| 角色设计 | character design, portrait, OC |
| 场景 | environment, landscape, cityscape |

## 已知限制

- ❌ 只能拿封面缩略图（`smaller_square`），大图需手动点开链接在浏览器看
- ❌ 项目详情 API 已不存在，无法获取多张 assets 和 tags
- ❌ Web 搜索走 Cloudflare 拦截，纯 API 搜索

## 许可证

MIT
