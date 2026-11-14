# Open

这些是尚未关闭的问题；不是待办清单，也不假装有结论。

## 1. 跨进程重放缓存（issue #2）

- 现状：同一 trace 内两个 receipt 共享 nonce 会被拒绝；两个独立进程不会。
- 要关闭：持久 nonce/receipt-id 存储，带 TTL、原子插入、并发语义；单节点不依赖第三方服务。
- 验收：两次独立 `demo/run.py` 调用，第二次返回 `REPLAY`。

## 2. Contract-only 三态探针（issue #3，离线验收完成）

- 现状：`demo/consume_contract.py` 仅使用 contract 的三种公开判定字段与一个 provenance 计数；输出 `accept` / `measurement` / `insufficient`。无 gate 导入、无模型内部信息依赖。[设计]
- 已验证：`python tools/check_contract_consumer.py` 将消费者复制到独立目录，在隔离 Python 中核对七份实际 demo 输出、标准输入/文件等价、四字段投影、无效输入拒绝。[合成]
- 尚未覆盖：真实框架接入与生产契约演进。离线三态分类通过不证明 producer 可信，也不改变 H1 的待检验状态。GitHub issue 的关闭由维护者决定。

## 3. Ed25519 与密钥生命周期（issue #4）

- 现状：demo 只验 HMAC；固定 demo key；没有 key id、轮换、吊销、信任锚。
- 要关闭：签名/验签向量、key id 绑定、轮换与吊销路径；明确信任从哪里来。
- 验收：固定测试向量通过；未知 key id 拒绝；吊销后的 key 拒绝。

## 4. Scope 语义

- 现状：claim 的 `scope` 只做字符串匹配；没有定义 scope 的包含、合并、过期。
- 要关闭：scope 语法与匹配规则；与 `allowed_scopes` 的关系；例子。
- 验收：至少一组“scope 更宽但覆盖不足”的反例。

## 5. 真实工具回执

- 现状：trace 里的 `stdout` 是录制的；没有从真实工具执行直接生成回执的适配器。
- 要关闭：一个只读的本地工具适配器，记录 argv、stdin、exit code、stdout/stderr hash。
- 验收：真实执行与录制回执在 gate 下产生同一 contract 结构。

## 6. 回执的隐私与最小披露

- 现状：`stdout_hash` 仍可能通过低熵输出被猜出；provenance summary 只放 id/hash。
- 要关闭：定义哪些字段可公开、哪些只给审计方；给出泄露分析。
- 验收：至少一个“hash 可被枚举还原”的反例，以及缓解方案。

## 7. 不做的声明

- 不声称理解、不声称不可伪造、不声称 H1 成立、不声称 10k 代理已跑。
- 没有 live 数据的地方继续写 `[待定]`。
