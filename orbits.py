from collections import namedtuple, deque
from itertools import combinations
import random
import math
import argparse
import os
import time
from tqdm import tqdm
import matplotlib.pyplot as plt


plt.style.use('dark_background')

G = 6.674e-11

parser = argparse.ArgumentParser()
parser.add_argument(
    '--solar-mass',
    type=float,
    default=1.0
)
parser.add_argument(
    '--days-per-frame',
    type=int,
    default=5
)
parser.add_argument(
    '--seed',
    type=int,
    default=12345
)
args = parser.parse_args()


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

min_observed = 1e20

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
        global min_observed
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
    def in_orbit(name, radius, mass, color, angle=None, days_per_frame=5):
        if angle is None:
            angle = random.uniform(0, 2*math.pi)

        pos = Point(radius * math.cos(angle), radius * math.sin(angle))
        direction = pos.perpendicular().normalized()
        speed = math.sqrt(G) * math.sqrt(1.989e30) / math.sqrt(radius)

        orbital_period = 365 * (radius / 1.496e11)**(3/2)
        orbital_period = min(365, orbital_period)
        trail_length = int(0.8 * (orbital_period / days_per_frame))

        return Planet(
            name,
            pos,
            speed * direction,
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


def update_planets(planets, center_on='sun', delta=1):
    for p1, p2 in combinations(planets.values(), 2):
        Planet.compute_forces(p1, p2)

    deleted = []

    sun_pos = planets[center_on].pos.copy()
    sun_vel = planets[center_on].vel.copy()
    for k, p in planets.items():
        p.update_planet(delta)

        # Keep sun-centric!
        p.pos = p.pos - sun_pos
        p.vel = p.vel - sun_vel

        if p.destroyed:
            deleted.append(k)

    for k in deleted:
        del planets[k]


def plot_planets(fig, planets, args, frame_i, day):
    fig.clf()

    for p in planets.values():
        p.update_trail()
        plt.scatter([p.x], [p.y], c=p.color, s=4e-4 * p.mass**(1/6))
        plt.plot(p.x_trail, p.y_trail, c=p.color, alpha=0.8)

    lim = 1.0 * 1.434e12
    plt.xlim((-lim, lim))
    plt.ylim((-lim, lim))

    plt.text(
        0.6*lim,
        0.7*lim,
        f'Day {day:04d}'
        #f'Day {day:04d}\n{args.solar_mass} solar masses'
    )

    plt.axis('off')
    plt.tight_layout()
    plt.axes().set_aspect('equal')

    path = os.path.join(
        'frames',
        args.directory,
        f'{frame_i:05d}.png'
    )

    plt.savefig(path, dpi=200)


def initialize_planets(args):
    planets = {}
    planets['sun'] = Planet(
        'sun',
        Point(0., 0.),
        Point(0., 0.),
        mass=1.989e30,
        color='yellow'
    )
    planets['mercury'] = Planet.in_orbit(
        'mercury',
        radius=57.91e9,
        mass=3.285e23,
        color='gray',
        days_per_frame=args.days_per_frame
    )
    planets['venus'] = Planet.in_orbit(
        'venus',
        radius=108.2e9,
        mass=4.867e24,
        color='white',
        days_per_frame=args.days_per_frame
    )
    planets['earth'] = Planet.in_orbit(
        'earth',
        radius=149.6e9,
        mass=5.972e24,
        color='c',
        days_per_frame=args.days_per_frame
    )
    planets['mars'] = Planet.in_orbit(
        'mars',
        radius=227.9e9,
        mass=6.39e23,
        color='r',
        days_per_frame=args.days_per_frame
    )
    planets['jupiter'] = Planet.in_orbit(
        'jupiter',
        radius=778.5e9,
        mass=1.898e27,
        color='brown',
        days_per_frame=args.days_per_frame
    )
    planets['saturn'] = Planet.in_orbit(
        'saturn',
        radius=1.434e12,
        mass=5.68e26,
        color='yellow',
        days_per_frame=args.days_per_frame
    )
    '''
    planets['uranus'] = Planet.in_orbit(
        radius=2.871e12,
        mass=8.681e25,
    )
    planets['neptune'] = Planet.in_orbit(
        radius=4.495e12,
        mass=1.024e26,
    )
    '''

    return planets

def simulate(args, center_on='sun', initial_frame=0):
    random.seed(args.seed)

    days_to_pass = 600  # 600
    days = int(5 * days_to_pass)  # 5 *
    days_elapsed = 0
    frame_i = initial_frame

    planets = initialize_planets(args)

    planets['rogue'] = Planet.produce_rogue(
        days_to_pass,
        args.solar_mass
    )

    pbar = tqdm(total=days)
    fig = plt.figure(figsize=(6, 6))

    while days_elapsed < days:
        for j in range(args.days_per_frame * 24):
            update_planets(planets, center_on=center_on, delta=3600)

        plot_planets(fig, planets, args, frame_i, days_elapsed)

        frame_i += 1
        days_elapsed += args.days_per_frame
        pbar.update(args.days_per_frame)

    pbar.close()

    return frame_i

if __name__ == '__main__':
    time_str = f'{int(time.time())}'[-4:]
    args.directory = f'{time_str}_{args.solar_mass}_{args.seed}'
    directory = os.path.join('frames', args.directory)
    os.makedirs(directory, exist_ok=True)

    frame = simulate(args, center_on='sun')
    simulate(args, center_on='rogue', initial_frame=frame)

    