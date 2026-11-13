# CAMS Audit Layer

**给 Agent 的输出加可验证的证据指纹、协方差和可依赖的拒绝契约。模型无关，离线可复现。**

[设计] 研究原型；[假设] 待检验；[实测] 有可复算数据。当前无 live `[实测]`，合成基准单独标注。

## 它是什么

一个很小的审计层：工具回执 → 证据指纹/溯源树 → 覆盖与协方差门控 → `accept` 或结构化 `refuse`。它不训练模型、不模拟政治、不声称“理解”。

## 30 分钟路径

1. 本页 + [`docs/PROTOCOL.md`](docs/PROTOCOL.md)：H1–H4 协议与不变量。
2. [`PREREGISTRATION.md`](PREREGISTRATION.md)：唯一主假设 H1 与停止规则。
3. [`bench/README.md`](bench/README.md)：100 题合成审计基准与 7 类泄漏。
4. [`docs/FALSIFICATION.md`](docs/FALSIFICATION.md)：什么结果算失败。
5. [`docs/EXPERIMENT-10K.md`](docs/EXPERIMENT-10K.md)：从 10³ 到 live 的升级门槛。

## 快速开始

```bash
python -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
python examples/demo_code_agent.py --offline
python bench/run.py --split test
python experiments/run_10k.py --mock
```

## 证据状态

- **合成基准**：`[实测-合成]`，只证明审计代码在 100 个构造任务上的行为，不是外部效度。
- **live H1**：`[TBD]`；没有 provider key、预算和真实工具回执前，不报告效应量。
- **不做**：0.1B 分区训练、100B 部署、2000 轮引擎、政治管理叙事。三层分区只作 [`docs/APPENDIX-OPTIONAL.md`](docs/APPENDIX-OPTIONAL.md) 的可选说明。

## 文件树

```text
cams_lite/            # 审计层（无网络、无数据库）
bench/                # AgentAudit-Bench v0：100 题 + 7 checkers + 基线
experiments/          # mock-first 10k 管线
tests/                # pytest
docs/                 # 协议、证伪、10k、路线图、发布
paper/note.md         # 4 页论文骨架（正/负模板）
```

## 许可证

MIT；见 [`LICENSE`](LICENSE)。
