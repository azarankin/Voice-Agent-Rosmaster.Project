
from Rosmaster_Lib import Rosmaster

from rosmaster_motor import MoveMotors, sleep
from rosmaster_arm import MoveArm
#from rosmaster_gamepad import Gamepad

from  config import GAMEPAD_CONTROLLER_ID, EXTENSION_BOARD_ADDRESS

__all__ = [sleep, GAMEPAD_CONTROLLER_ID, EXTENSION_BOARD_ADDRESS]


class CreateBot:
    def __init__(self, address = EXTENSION_BOARD_ADDRESS):
        self.bot = Rosmaster(com=address)
        #init methods
        self.arm = MoveArm(self.bot)
        self.motor = MoveMotors(self.bot)

        #first commad
        self._first_commands()

    def beep(self, on_time = 100):
        self.bot.set_beep(on_time)

    def terminate(self):
        self.__del__()

    def __del__(self):
        self.motor.stop()
        del self.bot
        del self.arm
        del self.motor

    def _first_commands(self):
        self.arm.arm_bent_down(10)



# -------------------------------------------------------
# Example usage
if __name__ == "__main__":
    # check with:   ls /dev/ttyUSB*
    extension_board_address = "/dev/ttyUSB0"  or EXTENSION_BOARD_ADDRESS 
    bot = CreateBot(extension_board_address)

    move_arm = bot.arm
    move_motor = bot.motor


    def sample_running():
        #preset
        move_arm.arm_bent_down(70)
        sleep()

        turning_time = 1.5
        move_motor.move_turn0(is_move=True)
        sleep(turning_time)  #timing for turning around
        move_motor.stop()
        sleep()

        move_motor.move_forward(is_move=True)
        sleep()
        move_motor.stop()
        sleep()


        move_arm.arm_bent_up(70)
        sleep()
        move_arm.arm_bent_down(70)
        sleep()

        #restore
        move_arm.arm_bent_up(70)
        sleep()
