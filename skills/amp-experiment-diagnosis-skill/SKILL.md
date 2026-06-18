---
name: amp-experiment-diagnosis-skill
description: Diagnose AMP/RL locomotion training failures from symptoms, training logs, environment/RL configs, motion inventories, playback notes, and code changes. Use this skill when the task is to explain why a robot cannot follow velocity commands, loses turning or strafing ability, overfits to AMP motion data, shows retargeting artifacts, or needs an evidence-backed next-experiment plan.
---

# AMP Experiment Diagnosis Skill

## Overview

This skill produces evidence-backed diagnosis reports for AMP locomotion experiments. It is designed for research debugging, not generic RL advice: every conclusion should be tied to logs, configs, motion data, playback observations, or explicit uncertainty.

Typical targets include small biped or humanoid AMP training runs where the policy learns style but fails a command direction, such as pure forward `vx` not starting, in-place `wz` turning requiring a high threshold, lateral commands needing a bias, or newly retargeted expert trajectories causing implausible joints.

## Required Inputs

Collect or ask for these materials before making strong claims. If any item is missing, state the gap and lower confidence.

- Symptom notes: command, expected behavior, observed behavior, checkpoint, and whether the issue is reproducible.
- Training log excerpts: reward terms, velocity errors, episode length, termination counts, AMP losses, and any custom diagnostic metrics.
- Environment config: reward weights/stds, command sampling ranges, heading/gait settings, reset events, initial velocity/pose policy, penalties outside the AMP/task lerp path, torque/action/motor limits.
- RL config: `amp_reward_coef`, `amp_task_reward_lerp`, rollout length, epochs, mini-batches, learning rate, resume checkpoint, run name.
- Motion inventory: expert motion directory, number of usable clips, direction coverage, left/right pairing, retarget source/method, accidental backup folders, fps/duration/schema notes.
- Playback notes: fixed-command tests, actual measured `vx/vy/wz`, manual push/bias behavior, and any UI/control preprocessing.
- Optional but useful: git diff, checkpoint lineage, TensorBoard screenshots, retarget scripts, exported motion stats.

## Workflow

1. Normalize the symptom.
   - Rewrite each issue as `command -> observed behavior -> expected behavior`.
   - Preserve the command coordinate convention. For this AMP_mjlab setup, `vx/vy` are body-frame forward/lateral commands; reward code may rotate them by robot yaw before comparing with world-frame linear velocity. `wz` is yaw angular velocity.

2. Snapshot the current experiment.
   - Record task name, run directory, checkpoint, resume source, and command-line flags.
   - Extract AMP/task blend: `amp_reward_coef`, `amp_task_reward_lerp`, and any reward terms added outside that blend.
   - Extract velocity tracking terms: linear/angular weights, stds, formulas, and whether yaw, lateral, or forward components are mixed.
   - Extract regularizers and safety terms: foot slip, action rate, joint acceleration, joint limits, termination penalties, torque/velocity/motor curve restrictions.
   - Extract training dynamics: rollout steps, epochs, mini-batches, learning rate, action noise, reset strategy, command curriculum or special sampling ratios.

3. Audit the expert motion data.
   - Count only the files the loader will actually read, not backups unless the loader recurses into them.
   - Check direction coverage: forward, backward, left, right, in-place yaw left/right, curved motion, idle/start clips.
   - Check balance: left/right pairs, mirrored clips, duration distribution, and whether the clips imply a speed floor.
   - Check retargeting quality: joint order, root orientation, scale/Froude changes, contact height, arm posture, and known artifacts such as hyperextended arms.
   - If discriminator data lacks a command direction, treat failures in that direction as plausible style-data coverage issues, not proven facts.

4. Read training and playback evidence.
   - Compare `Mean reward` with explicit `Mean amp reward after lerp`, `Mean task reward after lerp`, and outside penalties when available.
   - Inspect velocity errors alongside tracking rewards; high reward does not prove good tracking if std/weight or task blend makes the term weak.
   - Use fixed-command playback matrices to separate training-log averages from command-specific failures.
   - Note cases where a manual push, bias, or mixed command starts the robot. These are strong clues about start-state, command distribution, or learned gait manifold.

5. Build hypotheses with confidence.
   Use this canonical hypothesis set and add project-specific items as needed:
   - AMP/task reward conflict: AMP style reward dominates or discourages task-specific corrections.
   - Expert coverage gap: the discriminator has weak or ambiguous evidence for a requested direction or speed.
   - Command sampling mismatch: training rarely samples the problematic command, or mixes it with other axes.
   - Reset/playback mismatch: training starts from motion frames or nonzero velocities, but playback starts from standing still.
   - Retargeting artifact: converted expert clips contain wrong joint signs, root axes, contact height, or infeasible limbs.
   - Motor/action constraint: torque limits, motor velocity curves, or action scale prevent the required start impulse.
   - Control-interface mismatch: keyboard/joystick preprocessing adds thresholds, ramps, or biases that differ from training.

6. Write the diagnosis report.
   Produce the sections below. Keep facts and hypotheses separate.

```markdown
# AMP Locomotion Experiment Diagnosis

## Executive Summary
Short answer: what is most likely happening and what to test next.

## Evidence Inventory
List every file/log/playback note used, with paths or run names.

## Findings
| Finding | Evidence | Confidence | Human confirmation needed | Next experiment |
| --- | --- | --- | --- | --- |

## Config Snapshot
Reward blend, tracking weights/stds, command ranges, reset policy, PPO settings.

## Motion Dataset Audit
Clip count, direction coverage, retarget notes, suspicious files/folders.

## Playback/Test Matrix
Commands tested, observed speeds, pass/fail notes.

## Minimal Next Experiments
One-variable changes only, with run names and expected outcomes.

## Limitations
Missing evidence and claims that remain uncertain.
```

7. Verification pass.
   Before finalizing, check:
   - Every high-confidence conclusion has direct evidence.
   - Every uncertain mechanism is labeled as hypothesis.
   - The report names the exact config values, checkpoint, and run directory where possible.
   - Proposed experiments change one major factor at a time.
   - The output includes what a human should inspect in simulation, not only scalar metrics.

## Evidence Rules

- Cite exact file paths and line numbers when available.
- Cite training logs by iteration and metric name.
- Cite playback results by fixed command and measured actual velocity.
- Do not infer that the discriminator "knows" command direction unless the experiment logs or data design support it. Phrase this as: "consistent with a discriminator/data coverage issue".
- Do not collapse AMP reward, task reward, and outside penalties into one number if the code logs them separately.
- Do not trust the motion count from a folder name such as `Direct17`; inspect the actual loaded files and recursive loader behavior.
- If a retarget result is visually wrong, include the visual symptom, the source clip, and the retarget method before recommending more training.

## Good Output Style

- Be specific and experimental: name the next command, run name, checkpoint, or metric.
- Prefer compact tables for evidence and configurations.
- Use Chinese if the user is working in Chinese.
- Avoid generic advice such as "increase reward" without stating which term, why, and what failure mode it is expected to affect.
