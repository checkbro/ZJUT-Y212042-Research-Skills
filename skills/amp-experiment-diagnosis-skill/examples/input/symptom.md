# Symptom Notes

Robot: Dittle small biped.

Task: `Dittle-AMP-FullBody-G1WalkRun-Air-DynamicPhase-Flat`.

Checkpoint under discussion: latest `model_4000.pt` from the Direct17/Direct19 AMP experiment.

Observed symptoms:

- Fixed command `(0.8, 0.0, 0.0)` sometimes fails to start from standing.
- Fixed command `(0.8, 0.2, 0.0)` can start more reliably than pure forward.
- In-place turning is weak unless `|wz|` is about `1.4` rad/s or higher.
- Right strafe command, where `vy` is negative, starts better if `vx=-0.25` is added as a control-side bias.
- A previous direct G1/BONES-SEED to Dittle conversion caused arm hyperextension. Template-based retargeting using the earlier G1-to-Dittle method fixed the visual joint issue.

Expected behavior:

- The policy should follow pure forward, lateral, and in-place yaw commands without needing a manual push or command bias.
- AMP style should remain close to expert data without suppressing task-specific velocity tracking.
