# RELEASE — CAMS Audit Layer v0

## 发布前检查

- [ ] `pytest -q` 全绿；coverage ≥80%
- [ ] `python examples/demo_code_agent.py --offline` 可跑
- [ ] `python bench/run.py --split test` 可跑
- [ ] `python experiments/run_10k.py --mock` 可跑
- [ ] `PREREGISTRATION.md` 没有 live 假数
- [ ] README 首屏 ≤200 字，无 SOTA/领先/首次
- [ ] 结果文件明确标 `[实测-合成]` / `[TBD]`
- [ ] 不 force-push；PR 描述包含“没做什么”

## 博客/HN 大纲

1. 问题：Agent 的置信度不是证据；拒绝不是空值。
2. 机制：receipt → hash → supports → contract。
3. 合成基准：100 题；不要把合成数字写成 live H1。
4. 失败：minority_evidence 是已知泄漏；语义蕴含未解决。
5. 邀请：拿真实 tool receipts 来复现或反驳。

## Workshop 目标

- 目标：audit/agent safety/evals workshop；deadline `[TBD]`；
- 不声称“理解”“AGI”“100B”；
- 负结果也投。

## 不发布

- 没有 live 的 H1 数字；
- 没有机器可判 ground truth 的“用户反馈”；
- 任何政治建议/真实政治数据。
