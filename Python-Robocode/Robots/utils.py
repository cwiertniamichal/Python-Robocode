import math


def calculate_distance(pos_a, pos_b):
    return math.hypot(pos_a.x() - pos_b.x(), pos_a.y() - pos_b.y())
