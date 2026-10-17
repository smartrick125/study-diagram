# 样例 04：URP 自定义 Pass 学前地图（术语照留 + 白话）

- 模块：路线 · 学前地图
- 输入：「今天学在 URP 里加一步自己的渲染，先画个联系图」
- 源码：`04-URP自定义Pass学前地图.mmd`；三元组：`04-URP自定义Pass学前地图.关系.md`；上次渲染结果：`04-URP自定义Pass学前地图.png`（v0.6，看图通过）
- 来源：新功能「术语照留，配一句白话」（核心想法 2026-10-17，借鉴 B-007～B-010）

## 期望要点（重画后逐条对）

- [ ] 每个节点第一行是原样的专业词（URP、SRP、Shader、Render Pass、Scriptable Renderer Feature、Render Graph、HDRP），没被换成中文意译
- [ ] 每个节点第二行是 `白话：…`，约 20 字以内，只用常见词，没有引出新术语
- [ ] 有前提的节点（Render Graph）前提放在白话下一行
- [ ] 学前地图三层、★ 盲点、单向连线照旧；没有线穿过别的节点，标签不重叠

## 重画命令

```bash
python C:/Users/21265/.claude/skills/study-diagram/scripts/render.py tests/04-URP自定义Pass学前地图.mmd --out temp
```
