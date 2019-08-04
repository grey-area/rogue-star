import math
from collections import deque
import random


G = 6.674e-11


class Point:
    def __init__(self, x=0., y=0.):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(
            self.x + other.x,
            self.y + other.y
        )

    def __sub__(self, other):
        return Point(
            self.x - other.x,
            self.y - other.y
        )

    def __mul__(self, c):
        return Point(
            c * self.x,
            c * self.y
        )

    def __rmul__(self, c):
        return Point(
            c * self.x,
            c * self.y
        )

    def __truediv__(self, c):
        return Point(
            self.x / c,
            self.y / c
        )

    def __neg__(self):
        return Point(
            -self.x,
            -self.y
        )

    def __str__(self):
        return f'Point({self.x:.02e}, {self.y:.02e})'

    def copy(self):
        return Point(self.x, self.y)

    @property
    def norm(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalized(self):
        return self / self.norm

    def perpendicular(self):
        return Point(
            self.y,
            -self.x
        )


class Planet:
    def __init__(self, name, pos, vel, mass, color, trail_length=0):
        self.pos = pos
        self.vel = vel
        self.mass = mass
        self.accel = Point(0., 0.)
        self.name = name
        self.color = color
        self.trail_length = trail_length
        self.x_trail = deque()
        self.y_trail = deque()
        self.destroyed = False

    def update_planet(self, delta=1):
        self.pos = self.pos + delta * self.vel
        self.vel = self.vel + delta * self.accel
        self.accel = Point(0., 0.)

    def update_trail(self):
        self.x_trail.append(self.pos.x)
        self.y_trail.append(self.pos.y)

        if len(self.x_trail) > self.trail_length:
            self.x_trail.popleft()
            self.y_trail.popleft()

    @property
    def x(self):
        return self.pos.x

    @property
    def y(self):
        return self.pos.y

    @staticmethod
    def compute_forces(p1, p2):
        displace = p1.pos - p2.pos
        r = displace.norm
        direction = displace.normalized()

        F = (G * p1.mass * p2.mass) / r**2
        p1.accel = p1.accel - direction * F / p1.mass
        p2.accel = p2.accel + direction * F / p2.mass

        if r < 4e9:  # actual radius of the sun: 7e8
            if p1.mass < p2.mass:
                p1.destroyed = True
            else:
                p2.destroyed = True

    @staticmethod
    def in_orbit_of(parent, name, radius, mass, color, angle=None, days_per_frame=5):
        if angle is None:
            angle = random.uniform(0, 2*math.pi)

        pos = Point(radius * math.cos(angle), radius * math.sin(angle))
        direction = pos.perpendicular().normalized()
        speed = math.sqrt(G) * math.sqrt(parent.mass) / math.sqrt(radius)

        orbital_period = 365 * (radius / 1.496e11)**(3/2)
        orbital_period = max(min(365, orbital_period), 60)
        trail_length = int(0.8 * (orbital_period / days_per_frame))

        pos = pos + parent.pos
        vel = speed * direction + parent.vel

        return Planet(
            name,
            pos,
            vel,
            mass,
            color,
            trail_length
        )

    @staticmethod
    def produce_rogue(days_to_pass, solar_masses):
        speed = 2e4
        radius = speed * days_to_pass * 24 * 3600 + 778.5e9
        y = 5 * 149.6e9
        pos = Point(-radius, y)
        vel = Point(speed, 0.)

        return Planet(
            'rogue',
            pos,
            vel,
            1.989e30 * solar_masses,
            'yellow'
        )