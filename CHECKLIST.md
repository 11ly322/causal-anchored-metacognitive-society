# 七天清单与终检

这是七天压缩计划的收尾记录，不是新契约。当前行为以 `README.md`、`spec/`、`demo/`、`traces/` 为准；本文件只回答三件事：七天各交付了什么、终检跑了什么、还缺什么。

计划按工作包编号；实际执行集中在 2026-11-13 至 2026-11-14，不按自然日展开。这里没有 `[实测]`。

## 1. 终检结果

环境：Windows；本地 Python 3.12；`demo/run.py` 只用标准库，未联网。

| # | 验收项 | 结果 | 证据 |
|---|---|---|---|
| 1 | 新克隆能说清“是什么 / 怎么跑 / 不声称什么” | 结构通过；未做计时用户测试 | 本地 `git clone` 后根目录与 README 首屏一致；说明集中在 README 的“赌注 / 不声称什么 / 怎么跑” |
| 2 | `python demo/run.py --trace traces/accept.json` 离线跑通 | 通过 | `decision=accept`，退出码 0 |
| 3 | 3 条黄金 + 4 条失败各返回预期 | 通过（7/7） | 见 §2 |
| 4 | schema 可直接实现 | 通过（结构） | `spec/receipt.schema.json` 可解析；8 个必填字段、10 个属性 |
| 5 | 根目录无 `bench/`、`paper/`、`THEORY/` | 通过 | 根目录只有 README、LICENSE、.gitignore、HYPOTHESES、OPEN、CHECKLIST、archive、spec、demo、traces |
| 6 | git log 只有移动 / 重写 / 小修 | 通过 | 7 个提交：1 次归档移动 + 6 次文档、契约、demo、轨迹、终检的小步提交 |
| 7 | 公共面可评审 | 通过 | PR #1 为 draft、未合并；issues #2–#4 OPEN |

第 1 项的“10 分钟”是计划里的可读性目标，不是计时实验；第 4 项的“可直接实现”指字段与约束足够具体，不是已有第三方实现验证。

## 2. 轨迹终检

| trace | decision | detail_code | 退出码 |
|---|---|---|---|
| `traces/accept.json` | `accept` | `null` | 0 |
| `traces/measurement.json` | `MEASUREMENT_FAILURE` | `STALE` | 2 |
| `traces/insufficient.json` | `INSUFFICIENT_EVIDENCE` | `LOW_COVERAGE` | 3 |
| `traces/fail-tampered-stdout-hash.json` | `MEASUREMENT_FAILURE` | `INTEGRITY` | 2 |
| `traces/fail-replay-nonce.json` | `MEASUREMENT_FAILURE` | `REPLAY` | 2 |
| `traces/fail-empty-checksum.json` | `MEASUREMENT_FAILURE` | `SCHEMA` | 2 |
| `traces/fail-no-tool.json` | `MEASUREMENT_FAILURE` | `NO_RECEIPT` | 2 |

以上均为本地 fixture 运行，不是 live 证据。

## 3. 七天清单

| 工作包 | 交付 | 提交 | 状态 |
|---|---|---|---|
| Day 1 | 旧设计、原型、理论移入 `archive/`；根目录只留当前面 | `762d720` | 完成 |
| Day 2 | 一页 `README.md`：赌注、数据流、怎么跑、不声称什么 | `31fa716` | 完成 |
| Day 3 | `spec/RECEIPT.md` + `spec/receipt.schema.json` | `6a1440f` | 完成 |
| Day 4 | `spec/GATE.md` + 离线 `demo/run.py` + accept 轨迹 | `5acd990` | 完成 |
| Day 5 | 3 条黄金 + 4 条失败轨迹；`HYPOTHESES.md`、`OPEN.md` | `86f7cb9`、`16befaf` | 完成 |
| Day 6 | 公共面：PR #1（draft）+ issues #2–#4 | 无代码提交 | 完成（未合并） |
| Day 7 | 终检 + 本清单 + README/GATE 的日期与措辞收尾 | 本提交 | 完成 |

## 4. 还缺什么

- **#2 跨进程重放**：当前 nonce 只在单进程内去重；两次独立调用不会互相拒绝。
- **#3 contract-only 探针**：后续已新增 `demo/consume_contract.py`；`python tools/check_contract_consumer.py` 的七份真实 demo 输出、独立目录运行、四字段投影与异常输入检查通过。[合成] H2 的离线接口验收完成，真实框架接入和生产效度仍待检验。
- **#4 Ed25519 与密钥生命周期**：demo 只有 HMAC；没有 key id、轮换、吊销。
- **H1 / H4 没有 live 数据**：没有真实工具回执，也没有真实调用方延迟预算。
- **PR #1 保持 draft**：本计划不合并 `main`，不改仓库名，不做 force-push。

## 5. 复现

```bash
python demo/run.py --trace traces/accept.json
python demo/run.py --trace traces/measurement.json
python demo/run.py --trace traces/insufficient.json
python demo/run.py --trace traces/fail-tampered-stdout-hash.json
python demo/run.py --trace traces/fail-replay-nonce.json
python demo/run.py --trace traces/fail-empty-checksum.json
python demo/run.py --trace traces/fail-no-tool.json
```

demo 需要 Python 3.10+（用到 `dict[str, ...]` 与 `str | None`），只依赖标准库。Windows 上若 `python` 是应用商店占位符，改用真实解释器路径。

## 6. 不声称

- 不声称七天清单是效度证据，也不声称计划完成等于假设成立。
- 不声称回执不可伪造；只声称在可信根下可检测篡改与同 trace 重放。
- 不声称 H1、H4 或任何 live 结果；相关项继续标 `[假设]` 或 `[待定]`。
