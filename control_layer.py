from input_layer import InputLayer

class ControlLayer:
    def __init__(self):
        self.max_speed = 0.5 # cps

        self.desired_cm = 0
        self.desired_angle = 0
        self.input_layer = None

    def get_control_vector(self):

        desired_steps = 0
        desired_steering = self.desired_angle * 4

        if (not self.input_layer.motor_busy) and self.input_layer.distance_filter.confidence() > 0.85:
            # one wheel cycle is approx. 30 cm long, which is 4 steps
            desired_steps = self.desired_cm / 30.0 * 4
            self.input_layer.distance_filter.clear()

        return [desired_steering, desired_steps, self.max_speed]

    def update(self, input_layer):

        self.input_layer = input_layer
        self.desired_cm = input_layer.distance_cm - 60
        self.desired_angle = input_layer.angle_deg
