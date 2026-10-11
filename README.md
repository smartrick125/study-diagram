# G_project_009_学习图Skill

全局 skill `study-diagram` 的维护项目。把学习内容画成图，解决两个问题：

- **路线**：要学懂它还得先懂哪些、有哪些盲点 → 学前地图
- **顺序**：知识点按什么先后发生 → 时序图

当前版本 **v0.3**。维护规则见 [AGENTS.md](AGENTS.md)（任何 AI 都按它执行）。

## 怎么用

在任意 AI 里直接说「今天要学矩阵运算，先画个联系图」「把今天学的串起来」「这个过程画成时序图」即可；或点名「用 study-diagram 把 xxx 画成图」。

## 结构

```text
├─ AGENTS.md / CLAUDE.md   维护规则（CLAUDE.md 只有一行 @AGENTS.md）
├─ skill/                  skill 正本（各 AI 全局入口都链接到这里）
│   ├─ SKILL.md            总流程 + 模块目录
│   ├─ modules/            每个模块一个文件
│   ├─ references/         学科易错点、布局坑
│   └─ scripts/            render.py（mermaid）、plot.py（matplotlib）
├─ docs/
│   ├─ 核心想法.md          用户原意，借鉴不能推翻
│   ├─ 借鉴记录.md          每次调研的来源和取舍
│   ├─ 路线图.md            已上线 / 候选模块
│   └─ 变更日志.md
├─ tests/                  样例源码 + 期望要点，改完重画对照
└─ scripts/检查.ps1         行数、模块目录、模块格式检查
```

## 模块

见 [docs/路线图.md](docs/路线图.md)。
