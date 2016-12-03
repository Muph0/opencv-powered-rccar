from collections import deque
import math

class LinearWeightedFilter:
    _max_weight = 10.0

    def __init__(self, length):
        self._values = deque([0] * length)
        self._weights = deque([0] * length)
        self.results = deque([0] * length)

    def update(self, value):

        if (sum(self._weights) == 0):
            self._weights[-1] = self._weights[-2] = 1
            self._values[-1] = self._values[-2] = value

        square_error = (value - self._values[-1])**2

        self._values.append(value)
        self._weights.append(1 / max(1.0/_max_weight, square_error))
        self._values.popleft()
        self._weights.popleft()

        average = math.fsum([V*w for V,w in zip(self._values, self._weights)])
        average /= math.fsum(self._weights)

        self.results.append(average)
        self.results.popleft()

        return average

    def approximate_next(self):
        delta = self.results[-1] - self.results[-2]
        return self.results[-1] + delta

    def confidence(self):
        return (sum(self._weights) / len(self._weights) / _max_weight)

    def clear(self):
        self.__init__(len(self._values))



class InputLayer:

    def __init__(self):
        self.distance_cm = 1
        self.angle_deg = 0
        self.motor_busy = 1

        filter_len = 6
        self.distance_filter = LinearWeightedFilter(filter_len)
        self.angle_filter = LinearWeightedFilter(filter_len)

    def update(self, shape, motor_busy):

        self.motor_busy = motor_busy
        x,y,w,h = map(abs, shape)

        if shape != [-1,-1,-1,-1]:
            dist_cm = ((w*h)**-2 + 2*118/(w*h))**0.5
            self.distance_cm = self.distance_filter.update(dist_cm)
            #print("distance: %.2f" % dist_cm, "  filtered: %.2f" % self.distance_cm)

            angle = ((x+0.5*w) - 0.5) * 36.5
            self.angle_deg = self.angle_filter.update(angle)
        else:
            self.distance_cm = self.distance_filter.approximate_next()
            #print(" "*19 + "approximated: %.2f" % self.distance_cm)

            self.angle_deg = self.angle_filter.approximate_next()
