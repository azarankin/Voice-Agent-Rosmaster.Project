from rosmaster_utils import sleep


import pygame
from typing import List, Dict, Any

__all__ = [sleep]

class Gamepad():
    BUTTON_PRESS = 1
    BUTTON_RELEASE = 0

    def __init__(self, controller_id):
        pygame.init()
        pygame.joystick.init()

        # Check if there are any joysticks connected
        if pygame.joystick.get_count() == 0:
            raise RuntimeError("No joystick found.")
        

        self.joystick = pygame.joystick.Joystick(controller_id)
        self.joystick.init()
        print(f"Joystick detected: {self.joystick.get_name()}")


    def loop(self) -> List[Dict[str, Any]]:
        actions = []  # List to store actions and values
        
        # Process events
        pygame.event.pump()
        # Check for button and axis events
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                actions.append({"action": "button", "value": event.button, "mode": self.BUTTON_PRESS})
            elif event.type == pygame.JOYBUTTONUP:
                actions.append({"action": "button", "value": event.button, "mode": self.BUTTON_RELEASE})
            elif event.type == pygame.JOYAXISMOTION:
                actions.append({"action": "axis", "value": event.axis, "mode": event.value})
        
        # Check for D-pad (hat) movement
        num_hats = self.joystick.get_numhats()
        for i in range(num_hats):
            
            hat_value = self.joystick.get_hat(i)
            
            mode = self.get_dpad_direction(hat_value)
            if mode:  # Only append if there is a directional movement
                actions.append({"action": "dpad", "value": i, "mode": mode})
        
        sleep(0.1)  # Short delay to reduce CPU usage
        
        return actions

    def get_dpad_direction(self, hat_value: tuple) -> str:
        """Convert hat_value tuple to a string direction."""
        direction_map = {
            (0, 0): "neutral",
            (0, -1): "down",
            (0, 1): "up",
            (-1, 0): "left",
            (1, 0): "right",
            (-1, -1): "down-left",
            (1, -1): "down-right",
            (-1, 1): "up-left",
            (1, 1): "up-right"
        }
        return direction_map.get(hat_value, "")



    def close(self):
        pygame.joystick.quit()
        pygame.quit()

    def __del__(self):
        self.close()

