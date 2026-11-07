# 架构与机器契约

遵循 agent-cli-creator 2.1.0 的 design-contract、machine-contract、execution-gateway、acceptance-tests。纯标准库 Python，单文件可分发，内部按 registry/parser、policy/planner、backend、verifier、emitter 分层。

## 命令

`python scripts/herdr_agent.py RESOURCE ACTION [--input JSON|--file PATH|-] [OPTIONS]`

发现命令：version、schema、errors、doctor。业务命令由同一注册表生成 help/schema/argv。
统一标志：--output json|jsonl、--timeout 1..60（秒）、--limit 1..100、--offset >=0、--fields 逗号路径、--dry-run、--commit、--confirm HASH、--quiet、--no-input、--no-color。
没有输入文件时不读取 stdin；--file - 显式读取且最大 64 KiB。不提供 raw arbitrary argv、shell 文本或 Agent 原生参数入口。

读命令直接执行，写命令默认预演。预演与提交均执行同一套类型、目录、目标存在/占用者状态验证及官方只读前置查询。dry-run 输出规范化计划摘要和 hash，提交需重新计算相同 hash；目标、环境或 binary 变化后要求重新预演。
hash 是不可变计划一致性检查，不是访问控制凭证或 cryptographic user identity；计划绑定当前五分钟窗口结束时间，到期重新预演。没有服务器级幂等键，也不伪装 exactly-once。已授权的 Agent 可以在同一任务自动预演、核对、提交，不引入每次人工确认流程。适配层拒绝关闭调用者继承的 workspace/tab/pane，不扩张为 group close。前置查询与执行非原子，不能替代服务器端并发条件写入，执行后仍须核对。

## 输出

成功 `{schema_version,ok:true,type:result,data,meta:{request_id,duration_ms,...}}`；失败同层 error `{code,message,retryable,outcome,details,next_actions}`。JSONL 仅终结 envelope，无进度事件。quiet 不去掉终结结果。输出 encode 非 ASCII，保持 UTF-8 JSON 无 ANSI 控制字节；字符串中的终端控制被清理。
list 输出 items/pagination{offset,limit,returned,total,truncated,next_offset,consistency}；offset 是本次完整原生列表的本地切片，不是稳定 snapshot cursor。projection 仅对 items 字段应用，保留标识字段并声明。read 返回 text、line_limit、字符截断状态，不能截断 JSON 字节。

## 退出与 outcome

0 success；1 internal/backend malformed；2 invalid input；3 dependency/environment/resource；4 timeout/connectivity；5 state/plan/conflict；130 interrupt。官方 error.code 另保留，不通过英文/中文 message 猜业务状态。
read timeout 不影响业务状态；write timeout/output-limit/取消在 dispatch 后均 outcome unknown，停止本次 CLI 子进程但不停止已创建的 Herdr pane/Agent，返回 reconciliation。
成功写入但后续验证失败=committed 或 unknown，绝不把它报告为 not_started。start 被审批阻挡可能已启动进程，保留 name/pane；prompt 已提交不等于完成。

## 后端与输出界限

只从 HERDR_BIN_PATH 或 PATH 找 herdr，解析 realpath，检查 exe 名称及版本 0.9.5，计划包含二进制文件 SHA-256。不是对恶意本机用户的签名信任边界。读取 stdout/stderr 各有硬上限（默认 1 MiB），后台线程有界排水，超限终止本次 CLI 子进程并报告 structured error；不返回部分 JSON 当成功。
环境继承是 Herdr/Agent 本机兼容所需，计划仅保存环境摘要不保存明文。适配工具不是沙箱，不隔离现有 Herdr server/Agent 的 CPU、网络、文件或权限；不声称限制已启动 Agent 的后续行为。

## 验证器

workspace/tab create：解析官方 ID，get 确认；close：先 get 确认目标、提交后对应 list 确认不存在；agent start：get 确认 name/kind/pane 与就绪；prompt：仅确认 submitted，提供状态/输出命令；wait：返回 settled 及原始生命周期，不能报告业务完成。

## 未纳入 v1 的增强项

原始 Windows pipe 客户端、长期事件订阅、自动审批、exactly-once 消息、跨机器分发、Agent 内容自动判分、系统 PATH 安装和独立无 Python 二进制。本机有 Python 且已复用，便携技能入口足以交付本次目标，其他平台不作实测声明。
