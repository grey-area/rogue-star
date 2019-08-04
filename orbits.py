from itertools import combinations
import random
import math
import argparse
import os
import time
from tqdm import tqdm
from planets import Point, Planet
import matplotlib.pyplot as plt


plt.style.use('dark_background')


def parse_args():
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
    return parser.parse_args()


def update_planets(planets, center_on='sun', delta=1):
    for p1, p2 in combinations(planets.values(), 2):
        Planet.compute_forces(p1, p2)

    deleted = []

    sun_pos = planets[center_on].pos.copy()
    sun_vel = planets[center_on].vel.copy()
    for k, p in planets.items():
        p.update_planet(delta)

        p.pos = p.pos - sun_pos
        p.vel = p.vel - sun_vel

    for k in deleted:
        del planets[k]


def plot_planets(fig, planets, args, frame_i, day):
    fig.clf()

    for p in planets.values():
        p.update_trail()
        plt.scatter([p.x], [p.y], c=p.color, s=4e-4 * p.mass**(1/6))
        plt.plot(p.x_trail, p.y_trail, c=p.color, alpha=0.8)

    lim = 1.0 * 1.434e12
    #lim = 1.6e9  # for close-up moon visualization
    plt.xlim((-lim, lim))
    plt.ylim((-lim, lim))

    plt.text(
        0.6*lim,
        0.7*lim,
        f'Day {day:04d}'
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
    planets['mercury'] = Planet.in_orbit_of(
        planets['sun'],
        'mercury',
        radius=57.91e9,
        mass=3.285e23,
        color='gray',
        days_per_frame=args.days_per_frame
    )
    planets['venus'] = Planet.in_orbit_of(
        planets['sun'],
        'venus',
        radius=108.2e9,
        mass=4.867e24,
        color='white',
        days_per_frame=args.days_per_frame
    )
    planets['earth'] = Planet.in_orbit_of(
        planets['sun'],
        'earth',
        radius=149.6e9,
        mass=5.972e24,
        color='c',
        days_per_frame=args.days_per_frame
    )
    planets['mars'] = Planet.in_orbit_of(
        planets['sun'],
        'mars',
        radius=227.9e9,
        mass=6.39e23,
        color='r',
        days_per_frame=args.days_per_frame
    )
    planets['jupiter'] = Planet.in_orbit_of(
        planets['sun'],
        'jupiter',
        radius=778.5e9,
        mass=1.898e27,
        color='brown',
        days_per_frame=args.days_per_frame
    )
    planets['saturn'] = Planet.in_orbit_of(
        planets['sun'],
        'saturn',
        radius=1.434e12,
        mass=5.68e26,
        color='yellow',
        days_per_frame=args.days_per_frame
    )
    '''
    planets['moon'] = Planet.in_orbit_of(
        planets['earth'],
        'moon',
        radius=3.8e8,
        mass=7.35e22,
        color='white',
        days_per_frame=args.days_per_frame
    )
    '''

    return planets

def simulate(args, center_on='sun', initial_frame=0):
    random.seed(args.seed)

    days_to_pass = 600
    days = int(5 * days_to_pass)
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
    args = parse_args()

    time_str = f'{int(time.time())}'[-4:]
    args.directory = f'{time_str}_{args.solar_mass}_{args.seed}'
    directory = os.path.join('frames', args.directory)
    os.makedirs(directory, exist_ok=True)

    frame = simulate(args, center_on='sun')
    frame = 0
    simulate(args, center_on='rogue', initial_frame=frame)

    