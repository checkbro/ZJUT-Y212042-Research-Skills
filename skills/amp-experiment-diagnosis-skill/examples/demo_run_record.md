# Demo Run Record

## 运行目标

验证 `amp-experiment-diagnosis-skill` 是否能基于真实 AMP 机器人训练材料，输出一份有证据链的实验诊断报告，而不是只给泛泛的调参建议。

## 运行方式

本次 demo 以 `SKILL.md` 作为执行规则，读取 `examples/input/` 中的材料，并生成 `examples/output/diagnosis_report.md`。

这相当于一次离线运行：输入材料、执行规则和输出结果都保存在 skill 文件夹中，其他人可以复用同样输入检查输出是否满足要求。

## 输入文件

| 文件 | 内容 |
| --- | --- |
| `examples/input/symptom.md` | Dittle AMP 的实际异常现象，包括纯前向不起步、原地转向阈值、右移偏置、重定向异常。 |
| `examples/input/train_log_excerpt.txt` | 训练日志片段，包括速度误差、AMP/task reward、outside penalty 等指标。 |
| `examples/input/env_cfg_excerpt.py` | 环境配置片段，包括速度奖励权重/std、命令采样范围、foot slip 权重。 |
| `examples/input/rl_cfg_excerpt.py` | RL 配置片段，包括 `amp_reward_coef`、`amp_task_reward_lerp`、PPO epoch/mini-batch。 |
| `examples/input/motion_inventory.txt` | 动作数据审计线索，包括 Direct17/Direct19/21 条轨迹疑点和重定向方法。 |

## 输出文件

`examples/output/diagnosis_report.md`

输出报告包含：

- 核心结论摘要
- 证据清单
- 问题-证据-置信度-人工确认-下一步实验表
- 当前配置快照
- 动作数据审计
- playback 测试矩阵
- 最小下一步实验设计
- 局限性说明

## 运行结果摘要

Skill 识别出的主要问题不是单一奖励数值错误，而是 AMP 专家数据、速度命令采样、reset/playback 初态、控制输入策略之间存在方向失配。

高置信度结论包括：

- 训练日志中的速度误差仍然较高，说明速度跟踪没有完全解决。
- AMP/task/outside penalty 需要分开看，不能只看总 reward。
- 动作数据加载数量需要审计，因为 Direct17/Direct19 命名和实际读取数量可能不一致。
- 错误重定向会污染 AMP 判别器，视觉检查是入库前的必要步骤。

中等置信度假设包括：

- 纯前向不起步可能和专家数据方向覆盖或 AMP 判别器对速度方向的区分能力有关。
- 原地转向需要高 `wz` 可能来自专家轨迹速度分布、采样比例或控制端 ramp 设计。

## 可靠性检查

- 每条高置信度结论都在输出表中绑定了输入证据。
- 对机制性解释使用了“可能”“一致于”等表述，没有把假设写成事实。
- 下一步实验以固定命令 playback 矩阵和单变量训练修改为主，便于复现。
- 需要人工确认的内容单独列出，例如实际速度曲线、轨迹视觉质量和脚步滑动。

## 可复现方式

复现者只需要打开 `SKILL.md`，按照其中的 workflow 读取 `examples/input/` 中的材料，即可生成同结构的诊断报告。对照 `examples/output/diagnosis_report.md` 可以检查输出是否包含证据表、配置快照、动作数据审计和下一步实验设计。
