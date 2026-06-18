# Demo excerpt only. Values should be verified against the active AMP_mjlab config.

DITTLE_LINEAR_VELOCITY_REWARD_WEIGHT = 5.5
DITTLE_LINEAR_VELOCITY_REWARD_STD = 0.3

DITTLE_ANGULAR_VELOCITY_REWARD_WEIGHT = 3.5
DITTLE_ANGULAR_VELOCITY_REWARD_STD = 0.75

DITTLE_FOOT_SLIP_REWARD_WEIGHT = -0.5

DITTLE_G1WALKRUN17_DIRECT_LIN_VEL_X_RANGE = (-0.84, 1.0)
DITTLE_G1WALKRUN17_DIRECT_LIN_VEL_Y_RANGE = (-0.70, 0.70)
DITTLE_G1WALKRUN17_DIRECT_ANG_VEL_Z_RANGE = (-2.0, 2.0)

# Special command preprocessing observed during manual control tests:
# - in-place yaw should ramp quickly to about +/-1.5 rad/s when vx=vy=0
# - right strafe, vy<0, may need vx=-0.25 bias to start
