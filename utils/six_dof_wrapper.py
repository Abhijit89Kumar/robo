import gymnasium as gym
import numpy as np


class SixDOFWrapper(gym.Wrapper):
    """
    Wrapper to convert a 7-DOF Panda robot to a 6-DOF robot by fixing one joint.
    
    This wrapper:
    - Reduces the action space from 7D to 6D
    - Fixes joint 3 (index 2, the redundant elbow joint) at a neutral position
    - Maintains compatibility with the original observation space
    """
    
    def __init__(self, env, fixed_joint_idx=2, fixed_joint_value=0.0):
        """
        Initialize the 6-DOF wrapper.
        
        Args:
            env: The original 7-DOF Panda environment
            fixed_joint_idx: Index of the joint to fix (default: 2, which is joint 3)
            fixed_joint_value: Value to fix the joint at (default: 0.0, neutral position)
        """
        super().__init__(env)
        self.fixed_joint_idx = fixed_joint_idx
        self.fixed_joint_value = fixed_joint_value
        
        # Get original action space bounds
        original_low = env.action_space.low
        original_high = env.action_space.high
        
        # Create new 6D action space by removing the fixed joint
        new_low = np.delete(original_low, fixed_joint_idx)
        new_high = np.delete(original_high, fixed_joint_idx)
        
        # Update action space to 6 DOF
        self.action_space = gym.spaces.Box(
            low=new_low,
            high=new_high,
            dtype=np.float32
        )
        
        print(f"[SixDOFWrapper] Converted 7-DOF robot to 6-DOF")
        print(f"[SixDOFWrapper] Fixed joint {fixed_joint_idx} at value {fixed_joint_value}")
        print(f"[SixDOFWrapper] New action space shape: {self.action_space.shape}")
    
    def step(self, action):
        """
        Execute a step with the 6D action, converting it to 7D for the underlying env.
        
        Args:
            action: 6D action array
            
        Returns:
            observation, reward, terminated, truncated, info
        """
        # Convert 6D action to 7D by inserting the fixed joint value
        action_7d = np.insert(action, self.fixed_joint_idx, self.fixed_joint_value)
        
        # Execute the action in the underlying 7-DOF environment
        observation, reward, terminated, truncated, info = self.env.step(action_7d)
        
        return observation, reward, terminated, truncated, info
    
    def reset(self, **kwargs):
        """Reset the environment."""
        return self.env.reset(**kwargs)

