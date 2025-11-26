# Migration from 7-DOF to 6-DOF Robot Arm

## Overview

This document describes the changes made to convert the robotic arm control system from a 7 degrees of freedom (DOF) configuration to a 6 DOF configuration.

## What Changed

### 1. New 6-DOF Wrapper (`utils/six_dof_wrapper.py`)

A custom Gymnasium wrapper has been created that:
- **Reduces the action space** from 7 dimensions to 6 dimensions
- **Fixes joint 3** (index 2, the redundant elbow joint) at a neutral position (0.0)
- **Maintains full compatibility** with the existing observation space
- **Transparently converts** 6-DOF actions to 7-DOF actions for the underlying Panda environment

#### Key Features:
```python
# The wrapper automatically:
# 1. Takes a 6D action from your agent
# 2. Inserts a fixed value (0.0) at position 2 (joint 3)
# 3. Passes the resulting 7D action to the Panda environment
# 4. Returns the observation unchanged
```

### 2. Updated Training Scripts

All training and execution scripts have been updated to use the 6-DOF wrapper:

- **`main.py`**: Visualization/inference script
- **`training/ddpg_her.py`**: DDPG training with HER
- **`training/td3_her_training.py`**: TD3 training with HER

#### Changes in each file:
```python
# Added import
from utils.six_dof_wrapper import SixDOFWrapper

# Wrapped the environment
env = gym.make('PandaReach-v3')
env = SixDOFWrapper(env)  # This line converts 7-DOF to 6-DOF
```

### 3. Updated README

The README has been updated to reflect:
- The robot is now 6 DOF (converted from 7 DOF)
- Explanation of the wrapper mechanism
- Which joint is fixed and why

## Why These Changes?

### Advantages of 6-DOF Configuration:

1. **Simplified Control**: Fewer dimensions to control makes the learning problem simpler
2. **Faster Training**: Reduced action space can lead to faster convergence
3. **Sufficient for Many Tasks**: 6 DOF is often enough for reaching tasks (3 for position, 3 for orientation)
4. **Reduced Computational Cost**: Smaller neural networks and action spaces

### Which Joint Was Fixed?

**Joint 3 (index 2)** - the redundant elbow joint - was chosen because:
- The Panda robot's 7th DOF provides elbow redundancy
- This joint is primarily used for obstacle avoidance in cluttered environments
- Fixing it still allows the end-effector to reach most positions in the workspace
- Setting it to 0.0 (neutral position) provides a balanced configuration

## How to Use

### Training with 6-DOF

Simply run the training scripts as before:

```bash
# Train with DDPG + HER
python training/ddpg_her.py

# Train with TD3 + HER
python training/td3_her_training.py
```

The wrapper is automatically applied, and your agents will work with 6-DOF actions.

### Inference/Visualization

```bash
python main.py
```

Make sure your trained models were trained with the 6-DOF configuration!

### Testing the Wrapper

A test script is provided to verify the wrapper works correctly:

```bash
python test_six_dof.py
```

This will:
- Create both 7-DOF and 6-DOF environments
- Verify action space dimensions
- Test random actions
- Confirm the wrapper works correctly

## Customization

### Changing the Fixed Joint

If you want to fix a different joint, modify the wrapper initialization:

```python
# Fix joint 4 (index 3) instead
env = SixDOFWrapper(env, fixed_joint_idx=3, fixed_joint_value=0.0)
```

### Changing the Fixed Joint Value

To fix the joint at a different angle:

```python
# Fix joint 3 at 0.5 radians
env = SixDOFWrapper(env, fixed_joint_idx=2, fixed_joint_value=0.5)
```

## Backward Compatibility

### If you want to revert to 7-DOF:

Simply remove or comment out the wrapper line:

```python
env = gym.make('PandaReach-v3')
# env = SixDOFWrapper(env)  # Comment this out
```

**Note**: Models trained with 6-DOF won't work with 7-DOF environments and vice versa, as the action space dimensions are different.

## Technical Details

### Action Space Transformation

- **Original (7-DOF)**: `Box(shape=(7,), dtype=float32)`
- **Wrapped (6-DOF)**: `Box(shape=(6,), dtype=float32)`

### Fixed Joint Behavior

- **Fixed Joint Index**: 2 (joint 3 in 1-indexed notation)
- **Fixed Value**: 0.0 radians (neutral position)
- **Transformation**: `action_7d = [a0, a1, 0.0, a2, a3, a4, a5]` where `a0-a5` come from the 6D input

### Observation Space

The observation space remains unchanged:
- `observation`: Robot joint angles, velocities, and gripper state
- `achieved_goal`: Current end-effector position
- `desired_goal`: Target position to reach

## Performance Considerations

### Expected Changes:

- ✅ **Faster training**: Smaller action space typically converges faster
- ✅ **Simpler networks**: Actor network has fewer output neurons (6 vs 7)
- ⚠️ **Slightly reduced workspace**: Some configurations may be unreachable
- ⚠️ **No redundancy**: Cannot avoid obstacles using elbow redundancy

### When to Use 7-DOF Instead:

- Cluttered environments with obstacles
- Tasks requiring specific elbow configurations
- Applications needing maximum workspace coverage
- When redundancy is beneficial for avoiding singularities

## Files Modified

1. ✅ `utils/six_dof_wrapper.py` - **NEW** wrapper class
2. ✅ `main.py` - Added wrapper usage
3. ✅ `training/ddpg_her.py` - Added wrapper usage
4. ✅ `training/td3_her_training.py` - Added wrapper usage
5. ✅ `README.md` - Updated documentation
6. ✅ `test_six_dof.py` - **NEW** test script
7. ✅ `6DOF_MIGRATION.md` - **NEW** this document

## Summary

The migration to 6-DOF is complete and fully functional. All training scripts now use the 6-DOF configuration by default. The wrapper approach ensures:
- ✅ Minimal code changes
- ✅ Easy to customize or revert
- ✅ Compatible with existing code structure
- ✅ Transparent to the RL algorithms

The system is now ready to train 6-DOF control policies!

