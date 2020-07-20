import math


def stay_velocity(ship):
    """
    Uses the velocity to estimate the right dircetion for the boost
    """
    dx, dy = ship.velocity
    dx = float(dx)
    dy = float(dy)
    dt = abs(dx) + abs(dy)
    dx = dx / dt
    dy = dy / dt

    vx = 0
    vy = 0
    if abs(dx) > 0.25:
        vx = -1 if dx < 0 else 1
    if abs(dy) > 0.25:
        vy = -1 if dy < 0 else 1

    vec = (vx, vy)
    return vec


def stay_position(ship, inital_pos):
    """
    Calculates the distance between current position, and intial pos,
    to estimate the right dircetion for the boost
    """
    xi, yi = inital_pos
    x, y = ship.position
    dx = float(x - xi)
    dy = float(y - yi)

    dt = abs(dx) + abs(dy)
    if dt == 0:
        return (0, 0)

    dx = dx / dt
    dy = dy / dt

    vx = 0
    vy = 0
    if abs(dx) > 0.25:
        vx = -1 if dx < 0 else 1
    if abs(dy) > 0.25:
        vy = -1 if dy < 0 else 1

    vec = (vx, vy)
    return vec


def orbit(ship, gamma):
    x, y = ship.position
    x = float(x)
    y = float(y)
    # The internet said so ^^
    # http://www.chemgapedia.de/vsengine/vlu/vsc/de/ma/1/mc/ma_11/ma_11_03/ma_11_03_02.vlu.html
    x_1 = x * math.cos(gamma) - y * math.sin(gamma)
    y_1 = x * math.sin(gamma) + y * math.cos(gamma)

    # normalise
    dt = abs(x_1) + abs(y_1)
    dx = x_1 / dt
    dy = y_1 / dt

    vx = 0
    vy = 0

    vx = -1 if dx < 0 else 1
    vy = -1 if dy < 0 else 1

    vec = (vx, vy)
    return vec


def distance(vec1, vec2=(0, 0)):
    x = vec1[0] - vec2[0]
    y = vec1[1] - vec2[1]
    return math.sqrt(x ** 2 + y ** 2)


def rad(alpha):
    return math.pi * alpha / 180


def shoot_direction(ship, target_ship, previous_target_states):
    if not previous_target_states:
        return target_ship.position
    else:
        # some kind of linear interpolation
        previous_pos = previous_target_states[-1].position
        current_pos = target_ship.position
        x_1 = previous_pos[0]
        y_1 = previous_pos[1]
        x_2 = current_pos[0]
        y_2 = current_pos[1]
        dx = x_2 - x_1
        dy = y_2 - y_1
        x_3 = x_2 + dx
        y_3 = y_2 + dy
        return (x_3, y_3)

