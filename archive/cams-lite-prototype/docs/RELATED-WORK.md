# RELATED WORK — audit layer, not a cognition claim

| 工作族 | 它解决什么 | 本仓库不重复什么 | 本仓库的差异 |
|---|---|---|---|
| selective prediction / abstention | 用置信度决定弃权 | 不训练新选择器 | 弃权必须携带可验证 provenance 与稳定 contract |
| conformal prediction | 覆盖率保证 | 不声称分布-free 保证 | 覆盖是证据覆盖，不是预测集覆盖；拒绝原因码可审计 |
| calibration / ECE | 置信度校准 | 不把 ECE 当理解证据 | 协方差参与门控，不是事后温度缩放 |
| RAG attribution | 引用来源 | 不把“有引用”当支持 | 校验和、scope、relation、非文本叶四项一起检查 |
| C2PA / content credentials | 内容来源签名 | 不解决语义真值 | 把来源签名接到 claim 的 supports 图和 contract |
| multi-agent debate | 多角色投票 | 不用投票当审计 | 单次确定性门控，可复算，无采样 |
| refusal contracts | 版本化弃权 API | 不做通用认知架构 | 四原因码 + 外部三态脚本 + adapter cost |

## 可检验差异

1. 去掉 H1–H4 的 audit skeleton 在合成基准上应更差；若一样，审计层不承重。
2. 只读 contract 的外部脚本应能区分三态；若必须读内部协方差，契约失败。
3. 在有效任务上，审计层不应比 logprob 更保守超过 10pp。
4. 合成收益不应被写成 live H1；live 必须重跑。

## 非目标

- 不主张“理解”“意识”“脑模拟”；
- 不主张 0.1B/100B 规模；
- 不主张政治管理建议。
