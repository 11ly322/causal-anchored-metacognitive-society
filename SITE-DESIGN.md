# agent-audit-kernel 可视化站点设计说明

状态：六步导览设计已获用户批准，进入实现与验证。部署状态和验收证据记录在实施计划中。

## 目标与边界

面向初次访客和研究评审者，解释“工具回执 → 验证与门控 → 结构化结果”，并能追溯到现有文档与七个本地 fixture。网站采用逐步讲解结构，纯静态、无运行时依赖。

页面明确标注：展示的是本地 fixture 的离线结果，没有 live 实测；不证明模型理解、工具输出的世界真实性、生产级安全或 H1/H2 成立。公开 HMAC demo key 不能证明来源，重放检查不代表跨进程持久防护。

## 页面与交互

首屏用一句话说明项目用途，并显示“本地 fixture · 非线上实测”标签。主操作为“开始六步导览”，次操作为“查看七个样例”；仓库及规范链接保持可见。

| 步骤 | 通俗解释 | 可展开的技术内容 |
| --- | --- | --- |
| 1. Claim | 把待检查的声明与其证据要求分开 | claim 标识、证据引用、scope |
| 2. 工具调用 | 记录声明依赖的工具及输出 | tool_id、exit_code、原始 stdout |
| 3. Receipt | 为一次调用记录可核对字段 | receipt_id、stdout_hash、nonce、timestamp、signature、input_digest |
| 4. 关联与溯源 | 查明哪份回执支持哪个证据叶节点 | receipt 引用、claim 绑定、scope、provenance |
| 5. Gate | 依规范顺序检查证据是否可用、是否足够 | tool → receipt 验证 → claim 绑定 → scope → coverage |
| 6. Contract | 输出可由消费者处理的三种结果 | accept / MEASUREMENT_FAILURE / INSUFFICIENT_EVIDENCE 及契约字段 |

步骤列表允许直接跳转，另提供“上一步 / 下一步”和当前进度；每步先给短说明，再展开真实字段。示意连线没有实时运行含义。结尾的原生选择器覆盖全部七个 fixture，展示来源链接、复现命令、实际记录的 stdout/stderr、退出码、完整 contract 与简明原因。

不加入登录、在线工具执行、模型聊天、伪造进度、后台服务或新实验。

## 内容与数据来源

权威来源为 [README](README.md)、[GATE](spec/GATE.md)、[RECEIPT](spec/RECEIPT.md)、[HYPOTHESES](HYPOTHESES.md)、[OPEN](OPEN.md) 以及 [离线 verifier](demo/run.py)。网站不替代这些文档。

构建时用 Python 标准库运行现有 verifier，记录七个 trace 的输出、退出码与解析后的 contract，生成静态 JSON。构建保留 trace 路径与源文件 SHA-256，输出不符或无法解析时失败；浏览器只展示构建记录，不执行审计。所有资源使用相对路径以适配项目 Pages 子路径。

| 本地 fixture | 预期 decision / detail | 退出码 |
| --- | --- | --- |
| [accept](traces/accept.json) | accept / null | 0 |
| [measurement](traces/measurement.json) | MEASUREMENT_FAILURE / STALE | 2 |
| [insufficient](traces/insufficient.json) | INSUFFICIENT_EVIDENCE / LOW_COVERAGE | 3 |
| [tampered stdout](traces/fail-tampered-stdout-hash.json) | MEASUREMENT_FAILURE / INTEGRITY | 2 |
| [replay nonce](traces/fail-replay-nonce.json) | MEASUREMENT_FAILURE / REPLAY | 2 |
| [empty checksum](traces/fail-empty-checksum.json) | MEASUREMENT_FAILURE / SCHEMA | 2 |
| [no tool](traces/fail-no-tool.json) | MEASUREMENT_FAILURE / NO_RECEIPT | 2 |

## 视觉、可用性与恢复

采用清晰的阅读层级和克制的流程图；状态同时使用文字和颜色。桌面双栏、窄屏单栏，长标识与 JSON 可换行或在独立区域滚动，不让整页横向溢出。

使用语义化标题、按钮、链接、select 和 details；可全键盘操作，焦点可见，选中步骤和加载状态可感知。遵循 prefers-reduced-motion，不依赖动画传递信息。JSON 加载失败时保留导览与文档入口，显示明确错误和“重试”；关闭 JavaScript 时仍能阅读核心说明和复现命令。

## 发布与回退

站点资源放入独立 site/ 目录。GitHub Actions 运行构建与校验后发布 Pages，发布条件只允许 feat/cams-lite-audit；即使有手动触发入口也验证分支。只上传站点产物，不上传归档、仓库元数据或凭据。

启用仓库 Pages 的 Actions 来源并核对部署环境允许该 feature branch；不合并 PR，不修改 main。若权限或仓库设置阻止发布，保留已验证的产物并报告具体边界。发布失败不会改用其他分支。回退通过该分支还原站点提交并重新部署，或停用该发布工作流。

目标 URL：https://11ly322.github.io/causal-anchored-metacognitive-society/

## 验收

- 六步与现有规范一致；七个结果、detail 和退出码与实际 verifier 输出逐一相符。
- 本地静态服务可加载所有资源；检查桌面、窄屏、键盘、减少动态效果以及加载失败/重试状态。
- 检查无实时审计暗示、无 H1/H2 或生产安全结论；规范和 trace 链接可追溯。
- 发布后访问目标 URL，核对页面和 JSON；记录部署提交与结果，确认 main 未修改、PR 未合并。

## 自检

已覆盖已批准的受众、六步结构、七个样例、证据边界、低依赖实现、恢复与发布范围。无新增产品分支或用户待选项；视觉细节在上述约束内实施。设计审阅已通过，页面和导出器已实现；浏览器验收与发布记录见实施计划。
