from rosmaster_utils import sleep

from Rosmaster_Lib import Rosmaster

__all__ = [sleep]

class MoveMotors():
    def __init__(self, bot: Rosmaster):
        assert isinstance(bot, Rosmaster), "Please set bot as instances of Rosmaster."

        self.OFF_MOTOR_SPEED = 0 #stop motor value
        self.MAX_MOTOR_SPEED = 50

        self.bot = bot

        # stop motion begin reset
        self.stop()

    def gas(self):
        self.bot.set_motor(self.motor_front0_speed, self.motor_front1_speed, self.motor_back0_speed, self.motor_back1_speed)
    
    def stop(self):
        stop = self.OFF_MOTOR_SPEED
        self.set_all_motors(stop, is_move=True) # disable movement

    def set_motor(self, motor_front0_speed, motor_back0_speed, motor_front1_speed, motor_back1_speed, is_move:bool = False):
        self.motor_front0_speed = motor_front0_speed
        self.motor_back0_speed = motor_back0_speed
        self.motor_front1_speed = motor_front1_speed
        self.motor_back1_speed = motor_back1_speed
        if is_move:
            self.gas()
        

    def set_all_motors(self, speed, is_move:bool = False):
        self.set_motor(speed, speed, speed, speed, is_move)

    def set_turn_move(self, speed_side0, speed_side1, is_move:bool = False):
        self.set_motor(speed_side0, speed_side1, speed_side0, speed_side1, is_move)

    def set_turn_all_motors(self, speed, is_move:bool = False):
        self.set_turn_move(speed, -speed, is_move)


    def set_side_move(self, speed_front, speed_back, is_move:bool = False):
        self.set_motor(speed_front, speed_front, speed_back, speed_back, is_move)

    def set_side_all_motors(self, speed, is_move:bool = False):
        self.set_side_move(speed, -speed, is_move)

    def get_motor(self):
        return self.motor_front0_speed, self.motor_back0_speed, self.motor_front1_speed, self.motor_back1_speed


    def move_forward(self, is_move:bool = False):
        move = self.MAX_MOTOR_SPEED
        self.set_all_motors(move, is_move)

    def move_backward(self, is_move:bool = False):
        move = -self.MAX_MOTOR_SPEED
        self.set_all_motors(move, is_move)


    def move_turn0(self, is_move:bool = False):
        speed = -self.MAX_MOTOR_SPEED
        self.set_turn_all_motors(speed, is_move)

    def move_turn1(self, is_move:bool = False):
        speed = self.MAX_MOTOR_SPEED
        self.set_turn_all_motors(speed, is_move)

    def move_side0(self, is_move:bool = False):
        speed = -self.MAX_MOTOR_SPEED
        self.set_side_all_motors(speed, is_move)

    def move_side1(self, is_move:bool = False):
        speed = self.MAX_MOTOR_SPEED
        self.set_side_all_motors(speed, is_move)

    def close(self):
        # stop motion reset
        sleep()
        self.stop()
        

    def __del__(self):
        self.close()
