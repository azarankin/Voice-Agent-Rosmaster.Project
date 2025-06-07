from rosmaster_utils import sleep

from Rosmaster_Lib import Rosmaster

__all__ = [sleep]

class MoveArm():
    def __init__(self, bot: Rosmaster):
        assert isinstance(bot, Rosmaster), "Please set bot as instance of Rosmaster."

        self.MIN_SERVO_VALUE = 0
        self.MIDDLE_SERVO_VALUE = 90
        self.MAX_SERVO_VALUE = 180
        self.SERVO_BEGIN = self.MIDDLE_SERVO_VALUE
        self.MIN_SERVO_CLAMP_OPEN_VALUE = 0
        self.SERVO_CLAMP_CLOSE_BEGIN = 160

        self.ARM_BENT_MIN_VALUE = 0
        self.ARM_BENT_MAX_VALUE = 100
        self.ARM_BENT_MOTORS = 3
        self.ARM_BENT_VALUE = self.MAX_SERVO_VALUE / self.ARM_BENT_MAX_VALUE
        self.MIN_SERVO_BENT_SERVO_COMBINATION = 36
        self.MIDDLE_SERVO_BENT_SERVO_COMBINATION = self.MIDDLE_SERVO_VALUE
        self.MAX_SERVO_BENT_SERVO_COMBINATION = 103

        self.SERVO_ROTATION_STEP = 15
        self.ARM_OPEN_VALUE_STEP = 1
        self.MIN_OPEN_VALUE = 2
        self.MAX_OPEN_VALUE = 10
        self.OPEN_VALUE_STEP = self.MAX_SERVO_VALUE / self.MAX_OPEN_VALUE

        self.arm_open_value = 0
        self.bot = bot

        self.base_rotation = self.SERVO_BEGIN
        self.arm_bottom = self.SERVO_BEGIN
        self.arm_middle = self.SERVO_BEGIN
        self.arm_top = self.SERVO_BEGIN
        self.clamp_rotation = self.SERVO_BEGIN
        self.clamp_close = self.SERVO_CLAMP_CLOSE_BEGIN

        print("arm reset")
        self.set_arm_clamp_openning(value=None, is_applied=False)
        self.reset_servo()

    def reset_servo(self):
        self.set_arm_servo(self.SERVO_BEGIN, self.SERVO_BEGIN, self.SERVO_BEGIN,
                           self.SERVO_BEGIN, self.SERVO_BEGIN, self.SERVO_CLAMP_CLOSE_BEGIN)

    def value_clamp(self, value, min_servo_value=None, max_servo_value=None):
        if min_servo_value is None:
            min_servo_value = self.MIN_SERVO_VALUE
        if max_servo_value is None:
            max_servo_value = self.MAX_SERVO_VALUE
        return max(min(value, max_servo_value), min_servo_value)

    def set_base_rotation(self, base_rotation, min_value=None, max_value=None):
        if base_rotation is not None:
            self.base_rotation = self.value_clamp(base_rotation, min_value, max_value)

    def set_arm_position(self, arm_bottom, arm_middle, arm_top, min_value=None, max_value=None):
        if min_value is None:
            min_value = self.MIN_SERVO_BENT_SERVO_COMBINATION
        if max_value is None:
            max_value = self.MAX_SERVO_BENT_SERVO_COMBINATION

        if arm_bottom is not None:
            self.arm_bottom = self.value_clamp(arm_bottom, min_value, max_value)
        if arm_middle is not None:
            self.arm_middle = self.value_clamp(arm_middle, min_value, max_value)
        if arm_top is not None:
            self.arm_top = self.value_clamp(arm_top, min_value, max_value)
        self.arm_position = self.arm_top + self.arm_middle + self.arm_bottom

    def set_clamp_rotation(self, clamp_rotation, min_value=None, max_value=None):
        if clamp_rotation is not None:
            self.clamp_rotation = self.value_clamp(clamp_rotation, min_value, max_value)

    def set_clamp_close(self, clamp_rotation, min_value=None, max_value=None):
        if clamp_rotation is not None:
            self.clamp_close = self.value_clamp(clamp_rotation, min_value, max_value)

    def set_arm_servo(self, base_rotation=None, arm_bottom=None, arm_middle=None,
                      arm_top=None, clamp_rotation=None, clamp_close=None):
        self.set_base_rotation(base_rotation)
        self.set_arm_position(arm_bottom, arm_middle, arm_top)
        self.set_clamp_rotation(clamp_rotation)
        self.set_clamp_close(clamp_close, self.MIN_SERVO_CLAMP_OPEN_VALUE)
        angle_s = [self.base_rotation, self.arm_bottom, self.arm_middle,
                   self.arm_top, self.clamp_rotation, self.clamp_close]
        print("[DEBUG] Sending angles to robot:", angle_s)
        self.bot.set_uart_servo_angle_array(angle_s)

    def set_arm_rotate(self, value):
        self.base_rotation = self.value_clamp(self.base_rotation + value)
        self.set_arm_servo()

    def set_arm_clamp_openning(self, value=None, is_applied=True):
        if value is not None:
            self.arm_open_value = self.value_clamp(value, self.MIN_OPEN_VALUE, self.MAX_OPEN_VALUE)
        value = self.arm_open_value

        if value <= self.MIN_OPEN_VALUE:
            self.clamp_close = self.SERVO_CLAMP_CLOSE_BEGIN
        elif value >= self.MAX_OPEN_VALUE:
            self.clamp_close = self.MIN_SERVO_CLAMP_OPEN_VALUE
        else:
            self.clamp_close = int(self.SERVO_CLAMP_CLOSE_BEGIN - self.OPEN_VALUE_STEP * value)

        if is_applied:
            self.set_arm_servo()

    def arm_rotate0(self):
        self.set_arm_rotate(-self.SERVO_ROTATION_STEP)

    def arm_rotate1(self):
        self.set_arm_rotate(self.SERVO_ROTATION_STEP)

    def arm_full_close(self):
        self.set_arm_clamp_openning(0)

    def arm_full_open(self, value=None):
        self.set_arm_clamp_openning(value or self.MAX_OPEN_VALUE)

    def arm_step_close(self):
        if self.arm_open_value > self.MIN_OPEN_VALUE:
            self.arm_open_value -= self.ARM_OPEN_VALUE_STEP
            self.set_arm_clamp_openning()

    def arm_step_open(self):
        if self.arm_open_value < self.MAX_OPEN_VALUE:
            self.arm_open_value += self.ARM_OPEN_VALUE_STEP
            self.set_arm_clamp_openning()

    def arm_bent_to(self, float_value):
        float_value = self.value_clamp(float_value, -1.0, 1.0)
        min2mid = self.MIDDLE_SERVO_BENT_SERVO_COMBINATION - self.MIN_SERVO_BENT_SERVO_COMBINATION
        mid2max = self.MAX_SERVO_BENT_SERVO_COMBINATION - self.MIDDLE_SERVO_BENT_SERVO_COMBINATION

        if -1.0 <= float_value < 0.0:
            value_per_motor = self.MIDDLE_SERVO_BENT_SERVO_COMBINATION + min2mid * float_value
            self.set_arm_position(value_per_motor - 1, value_per_motor, value_per_motor)
        elif 0.0 <= float_value <= 1.0:
            value_per_motor = self.MIDDLE_SERVO_BENT_SERVO_COMBINATION + mid2max * float_value
            self.set_arm_position(value_per_motor + 1, value_per_motor, value_per_motor)

        self.set_arm_servo()

    def set_arm_bent_by(self, value):
        value_per_motor = value / self.ARM_BENT_MOTORS
        self.set_arm_position(self.arm_bottom + value_per_motor,
                              self.arm_middle + value_per_motor,
                              self.arm_top + value_per_motor)
        self.set_arm_servo()

    def arm_bent_up(self, value = 1):
        self.set_arm_bent_by(self.ARM_BENT_VALUE * value)

    def arm_bent_down(self, value = 1):
        self.set_arm_bent_by(-self.ARM_BENT_VALUE * value)

    def close(self):
        sleep()
        print("arm reset")
        self.reset_servo()

    def __del__(self):
        self.close()
