# AMP Locomotion Experiment Diagnosis

## Executive Summary

这不是单纯“速度奖励太小”的问题，更像是 AMP 风格数据、命令采样、reset/playback 初态、以及控制输入策略共同造成的命令方向失配。当前证据最支持三个判断：

1. 纯前向 `(0.8,0,0)` 不起步，但 `(0.8,0.2,0)` 能起步，说明策略可能学到了一个带侧向分量或特定起步扰动的运动流形。
2. 原地转向需要 `|wz|` 到约 `1.4` rad/s 以上才顺滑，说明原地 yaw 能力存在速度阈值，可能来自训练采样覆盖、专家轨迹速度分布或控制端 ramp 设计。
3. 直接从 G1/BONES-SEED 做关节映射会导致手臂反关节，说明动作数据质量本身会直接影响 AMP 判别器，不应把错误定向轨迹放入专家数据。

## Evidence Inventory

| Evidence | Source |
| --- | --- |
| 纯前向不起步、混合侧向可以起步 | `examples/input/symptom.md` |
| 原地转向需要高 `wz` | `examples/input/symptom.md` |
| 右移需要 `vx=-0.25` 控制偏置 | `examples/input/symptom.md` |
| `error_vel_xy=1.6088`，`error_vel_yaw=1.9154` | `examples/input/train_log_excerpt.txt`, iteration 851 |
| `Mean amp reward after lerp=14.3835`，`Mean task reward after lerp=15.3289` | `examples/input/train_log_excerpt.txt`, iteration 1403 |
| 当前示例速度权重/std | `examples/input/env_cfg_excerpt.py` |
| 当前示例 AMP/task 混合 | `examples/input/rl_cfg_excerpt.py` |
| 21 条轨迹疑点、重定向手臂异常 | `examples/input/motion_inventory.txt` |

## Findings

| Finding | Evidence | Confidence | Human confirmation needed | Next experiment |
| --- | --- | --- | --- | --- |
| 纯前向失败不一定是策略完全不会走，而是特定命令方向下无法进入稳定 gait。 | `(0.8,0,0)` 不起步，`(0.8,0.2,0)` 可以起步。 | Medium | 需要 playback 测实际 `vx/vy/wz` 曲线。 | 做固定命令矩阵：`(0.8,0,0)`、`(0.8,0.2,0)`、`(1.0,0,0)`、`(0.6,0,0)`。 |
| 原地 yaw 可能存在学到的速度阈值。 | 用户观察 `|wz|` 约 1.4 以上才丝滑，训练采样范围示例为 `[-2,2]`。 | Medium | 需要测 `wz=0.5/1.0/1.4/1.8/2.0` 的实际 yaw 速度。 | 增加原地 yaw command 占比，或让控制端在 `vx=vy=0` 时快速拉到 `wz=1.5`。 |
| 速度跟踪还没有真正稳定。 | `error_vel_xy=1.6088`、`error_vel_yaw=1.9154`，后续 stillness 实验 yaw error 到 `2.5767`。 | High | 需要确认这些 error 是按 episode 平均还是全部环境平均。 | 增加 playback 指标：固定命令下 2-10 s 的实际速度均值和方差。 |
| AMP/task 奖励不能只看总 reward。 | iteration 1403 显式记录 AMP、task、outside penalty，三者数量级接近且外部 penalty 明显影响总 reward。 | High | 不需要。 | 保留 `Mean amp reward after lerp`、`Mean task reward after lerp`、`Mean outside start penalty` 三项日志。 |
| 动作数据加载数量需要重新审计。 | Direct17 命名与 19/21 条实际读取数量不一致；inventory 提到可能误读 backup 或旧转向轨迹。 | High | 需要打印 loader 实际读取的文件列表。 | 训练启动时输出完整 motion file list，并把 backup 移出 motion root。 |
| 错误重定向会污染 AMP 判别器。 | 直接映射导致手臂反关节，模板法修复。 | High | 需要视觉检查四条新转向轨迹。 | 新轨迹入库前先用轨迹浏览器逐帧检查脚接触、手臂、root yaw。 |

## Config Snapshot

| Item | Value |
| --- | --- |
| `amp_reward_coef` | `0.1` |
| `amp_task_reward_lerp` | `0.5` |
| linear tracking | weight `5.5`, std `0.3` |
| angular tracking | weight `3.5`, std `0.75` |
| foot slip | weight `-0.5` |
| command `vx` range | `(-0.84, 1.0)` |
| command `vy` range | `(-0.70, 0.70)` |
| command `wz` range | `(-2.0, 2.0)` |
| PPO epoch / mini-batch | `5 * 4` |

## Motion Dataset Audit

当前最需要确认的是实际加载轨迹数。研究假设是“删掉 2 条旧转向，加入 4 条新转向，所以应为 19 条”，但如果 loader 递归扫描 backup 或旧文件仍留在 motion root，就会出现 21 条。这个问题会直接影响判别器数据分布，因此要在训练启动时打印完整文件列表。

重定向上，不建议再使用纯 joint-name 直映射。对 Dittle 这种短腿小机器人，应使用已经验证过的 G1-to-Dittle retarget 模板，把 BONES-SEED 的路径、节奏、yaw 语义转成 Dittle 可行姿态，而不是强行保留 G1 的关节角。

## Playback/Test Matrix

| Command | Expected observation |
| --- | --- |
| `(0.8, 0.0, 0.0)` | 验证纯前向是否仍无法起步。 |
| `(0.8, 0.2, 0.0)` | 验证混合侧向是否更容易进入 gait。 |
| `(0.0, 0.0, 1.0)` | 验证低 yaw 指令是否卡住。 |
| `(0.0, 0.0, 1.5)` | 验证高 yaw 指令是否顺滑转动。 |
| `(0.0, -0.7, 0.0)` | 验证右移是否失败。 |
| `(-0.25, -0.7, 0.0)` | 验证右移加前向负偏置是否启动。 |

## Minimal Next Experiments

1. 先固定训练环境，只做 playback 矩阵，记录每个命令下 2-10 s 的实际 `vx/vy/wz`。
2. 若纯前向仍失败，优先检查动作数据中是否有干净的纯前向起步/行走片段，而不是直接继续加大速度奖励。
3. 若 yaw 低速失败但高速可行，可以单开一版原地 yaw 采样占比实验，例如 `vx=vy=0` 的 yaw-only command 占 40%。
4. 若 Direct17/Direct19 文件数不一致，先修正 motion root，再训练。不要让 backup 目录参与判别器数据。
5. 控制端可以做工程补偿，但要和训练诊断分开记录：`vx=vy=0` 时快速 ramp 到 `wz=1.5`；右移 `vy<0` 时临时加 `vx=-0.25`。

## Limitations

这里的报告基于示例日志和现象描述，不能直接证明判别器一定误判了速度方向。更严谨的证据需要两类实验：一是打印并可视化专家动作方向覆盖，二是固定命令 playback 下记录实际速度曲线。当前结论中，“速度跟踪误差高”和“动作数据加载数不一致”置信度高；“AMP 判别器方向覆盖导致纯前向不起步”属于中等置信度假设。
