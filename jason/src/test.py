import math

self_x, self_y = 0, 1
enemy_x, enemy_y = 0, 0

x_dist, y_dist = enemy_x - self_x, enemy_y - self_y
if x_dist == 0:
    angle = -90 if y_dist < 0 else 90
else:
    angle = math.degrees(math.atan(y_dist / x_dist))
    # Flip angle if x_dist is negative
    angle = 180 - angle if x_dist < 0 else angle

target_angle = angle % 360
print(target_angle)