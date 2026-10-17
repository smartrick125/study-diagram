# 04-URP自定义Pass学前地图 · 关系三元组

- R1: K1 能用 C# 脚本定制的叫 K3（AI 补全；Unity 手册 SRP 简介）
- R2: K3 Unity 预先做好的一套 K4（Unity 6 手册 URP 简介：“The Universal Render Pipeline (URP) is a prebuilt Scriptable Render Pipeline, made by Unity.” https://docs.unity3d.com/6000.0/Documentation/Manual/urp/urp-introduction.html ）
- R3: K2 画东西的 Pass 要用它 K5（AI 补全；只说画物体的 Pass，不说每一步都用）
- R4: K4 由一个个组成 K5（AI 补全）
- R5: K6 把自定义的一步排进 K5（Unity 手册：Renderer Feature 的 `AddRenderPasses` 调 `EnqueuePass` 把自定义 pass 插进管线 https://docs.unity3d.com/6000.3/Documentation/Manual/urp/renderer-features/scriptable-renderer-features/inject-a-pass-using-a-scriptable-renderer-feature.html ）
- R6: K7 记录这一步要读写什么 K5（Unity 6 手册：继承 `ScriptableRenderPass`，在 `RecordRenderGraph` 里添加、配置 pass https://docs.unity3d.com/6/Documentation/Manual/urp/render-graph-write-render-pass.html ）
- R7: K4 对比 K8（AI 补全；HDRP 也是 Unity 做好的 SRP）

前提：
- K7 只在没开兼容模式（Compatibility Mode）时用 Render Graph；兼容模式是旧写法，Unity 已不再改进（https://docs.unity3d.com/6000.0/Documentation/Manual/urp/renderer-features/write-a-scriptable-render-pass.html ）。

白话：每个专业词节点第二行都有 `白话：`，术语本身照留（见 SKILL.md「术语照留，配一句白话」）。
