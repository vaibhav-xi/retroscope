from __future__ import annotations

import math

import numpy as np

try:

    from modules.audioreactive._native import _native as _native_audio

    NATIVE_AVAILABLE = True

except ImportError:

    _native_audio = None

    NATIVE_AVAILABLE = False


if NATIVE_AVAILABLE:

    class EmberField:

        def __init__(self, capacity: int, inner_radius: float, random):

            seed = random.getrandbits(32) if random is not None else 0

            self._native = _native_audio.EmberField(
                capacity,
                float(inner_radius),
                seed,
            )

            self.capacity = capacity
            self.inner_radius = inner_radius
            self.random = random

        def spawn(self, count: int):

            self._native.spawn(count)

        def update(self, dt: float):

            self._native.update(dt)

        def points(self):

            return self._native.points()

    def spectrum_ring(
        magnitudes,
        base_radius: float,
        amplitude: float,
        rotation: float = 0.0,
        mirror: bool = True,
    ):

        return _native_audio.spectrum_ring(
            magnitudes,
            float(base_radius),
            float(amplitude),
            float(rotation),
            bool(mirror),
        )

    class BurstField:

        def __init__(self, capacity: int, drag: float = 0.0, random=None):

            seed = random.getrandbits(32) if random is not None else 0

            self._native = _native_audio.BurstField(capacity, float(drag), seed)

            self.capacity = capacity
            self.drag = drag
            self.random = random

        def spawn(
            self,
            count: int,
            origin,
            angle_range,
            speed_range,
            lifetime_range,
            angular_velocity_range=(0.0, 0.0),
            distance_start: float = 0.0,
        ):

            ox, oy = origin

            self._native.spawn(
                count,
                origin_x=float(ox),
                origin_y=float(oy),
                angle_min=float(angle_range[0]),
                angle_max=float(angle_range[1]),
                speed_min=float(speed_range[0]),
                speed_max=float(speed_range[1]),
                lifetime_min=float(lifetime_range[0]),
                lifetime_max=float(lifetime_range[1]),
                angular_velocity_min=float(angular_velocity_range[0]),
                angular_velocity_max=float(angular_velocity_range[1]),
                distance_start=float(distance_start),
            )

        def update(self, dt: float):

            self._native.update(dt)

        def points(self):
            """Returns (positions, life, angle, speed)."""

            return self._native.points()

    class RingField:

        def __init__(self, capacity: int, random=None):

            seed = random.getrandbits(32) if random is not None else 0

            self._native = _native_audio.RingField(capacity, seed)

            self.capacity = capacity
            self.random = random

        def spawn(
            self,
            strength: float,
            speed: float,
            wobble: float = 0.0,
            start_radius: float = 6.0,
            spin_range=(0.0, 0.0),
            lifetime_base: float = 0.5,
            lifetime_coefficient: float = 0.03,
            randomize_rotation: bool = True,
            start_rotation: float = 0.0,
        ):

            self._native.spawn(
                strength=float(strength),
                speed=float(speed),
                wobble=float(wobble),
                start_radius=float(start_radius),
                spin_min=float(spin_range[0]),
                spin_max=float(spin_range[1]),
                lifetime_base=float(lifetime_base),
                lifetime_coefficient=float(lifetime_coefficient),
                randomize_rotation=bool(randomize_rotation),
                start_rotation=float(start_rotation),
            )

        def update(self, dt: float):

            self._native.update(dt)

        def rings(self, center, segments: int, wobble_scale: float = 6.0, wobble_frequency: float = 5.0):

            cx, cy = center

            return self._native.rings(
                cx=float(cx),
                cy=float(cy),
                segments=int(segments),
                wobble_scale=float(wobble_scale),
                wobble_frequency=float(wobble_frequency),
            )

        def shells(self, center, sides: int):

            cx, cy = center

            return self._native.shells(cx=float(cx), cy=float(cy), sides=int(sides))

        def kick(self, positions, center, gain: float = 1.0, band: float = 16.0):

            cx, cy = center

            return self._native.kick(
                positions, cx=float(cx), cy=float(cy), gain=float(gain), band=float(band)
            )

    class ChaosField:

        def __init__(self, capacity: int, random=None):

            seed = random.getrandbits(32) if random is not None else 0

            self._native = _native_audio.ChaosField(capacity, seed)

            self.capacity = capacity
            self.random = random

        def set_parameters(self, a: float, b: float, c: float, d: float):

            self._native.set_parameters(float(a), float(b), float(c), float(d))

        def detonate(self, strength: float):

            self._native.detonate(float(strength))

        def update(self, dt: float, reseed_fraction: float = 0.02):

            self._native.update(dt=float(dt), reseed_fraction=float(reseed_fraction))

        def points(self, center, scale: float):

            cx, cy = center

            return self._native.points(float(cx), float(cy), float(scale))
        
    class BoidSwarm:

        def __init__(self, capacity: int, random, neighbor_radius: float = 70.0):

            seed = random.getrandbits(32) if random is not None else 0

            self._native = _native_audio.BoidSwarm(
                capacity,
                neighbor_radius=float(neighbor_radius),
                seed=seed,
            )

            self.capacity = capacity
            self.random = random
            self.neighbor_radius = neighbor_radius

        def update(
            self,
            dt: float,
            focus,
            cohesion: float,
            alignment: float,
            separation: float,
            jitter: float,
            max_speed: float,
            threat=None,
            threat_strength: float = 0.0,
        ):

            fx, fy = focus

            has_threat = threat is not None

            tx, ty = threat if has_threat else (0.0, 0.0)

            self._native.update(
                dt=float(dt),
                focus_x=float(fx),
                focus_y=float(fy),
                cohesion=float(cohesion),
                alignment=float(alignment),
                separation=float(separation),
                jitter=float(jitter),
                max_speed=float(max_speed),
                has_threat=bool(has_threat),
                threat_x=float(tx),
                threat_y=float(ty),
                threat_strength=float(threat_strength),
            )

        def neighbor_links(self, max_links: int, link_radius: float | None = None, center=(0.0, 0.0)):

            radius = (
                link_radius if link_radius is not None
                else self.neighbor_radius * 0.55
            )

            cx, cy = center

            return self._native.neighbor_links(
                int(max_links), float(radius), center_x=float(cx), center_y=float(cy)
            )

        def render_points(self, center=(0.0, 0.0)):

            cx, cy = center

            return self._native.render_points(center_x=float(cx), center_y=float(cy))



    def lightning_bolt(origin, angle: float, length: float, depth: int, jitter=None, random=None):

        ox, oy = origin

        seed = random.getrandbits(32) if random is not None else 0

        kwargs = dict(
            origin_x=float(ox),
            origin_y=float(oy),
            angle=float(angle),
            length=float(length),
            depth=int(depth),
            seed=seed,
        )

        if jitter is not None:

            kwargs["jitter"] = float(jitter)

        return _native_audio.lightning_bolt(**kwargs)

    def subdivide_triangle(triangle, depth: int, jitter: float = 0.0, random=None):

        (ax, ay), (bx, by), (cx, cy) = triangle

        seed = random.getrandbits(32) if random is not None else 0

        return _native_audio.subdivide_triangle(
            ax=float(ax), ay=float(ay),
            bx=float(bx), by=float(by),
            cx=float(cx), cy=float(cy),
            depth=int(depth),
            jitter=float(jitter),
            seed=seed,
        )

    def radial_ring(radius, base_angle: float = 0.0, angle_span=None, center=(0.0, 0.0), close_loop: bool = True):

        cx, cy = center

        span = angle_span if angle_span is not None else 2.0 * math.pi

        return _native_audio.radial_ring(
            radius,
            base_angle=float(base_angle),
            angle_span=float(span),
            center_x=float(cx),
            center_y=float(cy),
            close_loop=bool(close_loop),
        )
        
    def fixed_dashes(positions, dx: float, dy: float, center=(0.0, 0.0)):

        cx, cy = center

        return _native_audio.fixed_dashes(
            positions,
            dx=float(dx),
            dy=float(dy),
            center_x=float(cx),
            center_y=float(cy),
        )

    def life_dashes(
        positions,
        life,
        center=(0.0, 0.0),
        size_base: float = 1.0,
        size_scale: float = 1.0,
    ):

        cx, cy = center

        return _native_audio.life_dashes(
            positions,
            life,
            center_x=float(cx),
            center_y=float(cy),
            size_base=float(size_base),
            size_scale=float(size_scale),
        )


else:

    print(
        "[modules.audioreactive.native] native extension not built - "
        "falling back to pure-Python implementations."
    )

    from modules.audioreactive.mode1.particles import EmberField
    from modules.audioreactive.mode1.spectrum import spectrum_ring
    from modules.audioreactive.mode4.boids import BoidSwarm

    class BurstField:

        def __init__(self, capacity: int, drag: float = 0.0, random=None):

            self.capacity = capacity
            self.drag = drag
            self.random = random

            self.origin_x = np.zeros(capacity, dtype=np.float32)
            self.origin_y = np.zeros(capacity, dtype=np.float32)
            self.angle = np.zeros(capacity, dtype=np.float32)
            self.angular_velocity = np.zeros(capacity, dtype=np.float32)
            self.distance = np.zeros(capacity, dtype=np.float32)
            self.speed = np.zeros(capacity, dtype=np.float32)
            self.age = np.zeros(capacity, dtype=np.float32)
            self.lifetime = np.ones(capacity, dtype=np.float32)
            self.alive = np.zeros(capacity, dtype=bool)

            self._cursor = 0

        def spawn(
            self,
            count: int,
            origin,
            angle_range,
            speed_range,
            lifetime_range,
            angular_velocity_range=(0.0, 0.0),
            distance_start: float = 0.0,
        ):

            ox, oy = origin

            for _ in range(count):

                i = self._cursor

                self._cursor = (self._cursor + 1) % self.capacity

                self.origin_x[i] = ox
                self.origin_y[i] = oy
                self.angle[i] = self.random.uniform(*angle_range)
                self.angular_velocity[i] = self.random.uniform(*angular_velocity_range)
                self.distance[i] = distance_start
                self.speed[i] = self.random.uniform(*speed_range)
                self.age[i] = 0.0
                self.lifetime[i] = self.random.uniform(*lifetime_range)
                self.alive[i] = True

        def update(self, dt: float):

            active = self.alive

            self.age[active] += dt

            expired = self.alive & (self.age >= self.lifetime)

            self.alive[expired] = False

            active = self.alive

            if self.drag > 0.0:

                self.speed[active] *= np.exp(-self.drag * dt)

            self.angle[active] += self.angular_velocity[active] * dt
            self.distance[active] += self.speed[active] * dt

        def points(self):

            active = self.alive

            x = self.origin_x[active] + self.distance[active] * np.cos(self.angle[active])
            y = self.origin_y[active] + self.distance[active] * np.sin(self.angle[active])

            lifetime = np.maximum(self.lifetime[active], 1e-6)

            life = 1.0 - (self.age[active] / lifetime)

            return (
                np.column_stack([x, y]).astype(np.float32),
                life.astype(np.float32),
                self.angle[active].astype(np.float32),
                self.speed[active].astype(np.float32),
            )

    class RingField:

        def __init__(self, capacity: int, random=None):

            self.capacity = capacity
            self.random = random

            self.radius = np.zeros(capacity, dtype=np.float32)
            self.speed = np.zeros(capacity, dtype=np.float32)
            self.strength = np.zeros(capacity, dtype=np.float32)
            self.wobble = np.zeros(capacity, dtype=np.float32)
            self.rotation = np.zeros(capacity, dtype=np.float32)
            self.spin = np.zeros(capacity, dtype=np.float32)
            self.age = np.zeros(capacity, dtype=np.float32)
            self.lifetime = np.ones(capacity, dtype=np.float32)
            self.alive = np.zeros(capacity, dtype=bool)

            self._cursor = 0

        def spawn(
            self,
            strength: float,
            speed: float,
            wobble: float = 0.0,
            start_radius: float = 6.0,
            spin_range=(0.0, 0.0),
            lifetime_base: float = 0.5,
            lifetime_coefficient: float = 0.03,
            randomize_rotation: bool = True,
            start_rotation: float = 0.0,
        ):

            i = self._cursor

            self._cursor = (self._cursor + 1) % self.capacity

            self.radius[i] = start_radius
            self.speed[i] = speed
            self.strength[i] = strength
            self.wobble[i] = wobble

            self.rotation[i] = (
                self.random.uniform(0.0, 2.0 * math.pi)
                if randomize_rotation
                else start_rotation
            )

            self.spin[i] = self.random.uniform(*spin_range)
            self.age[i] = 0.0
            self.lifetime[i] = lifetime_base + strength * lifetime_coefficient
            self.alive[i] = True

        def update(self, dt: float):

            active = self.alive

            self.age[active] += dt

            expired = self.alive & (self.age >= self.lifetime)

            self.alive[expired] = False

            active = self.alive

            self.radius[active] += self.speed[active] * dt
            self.rotation[active] += self.spin[active] * dt

        def rings(self, center, segments: int, wobble_scale: float = 6.0, wobble_frequency: float = 5.0):

            cx, cy = center

            out = []

            for i in np.nonzero(self.alive)[0]:

                life = 1.0 - (self.age[i] / max(self.lifetime[i], 1e-6))

                wobble_amount = self.wobble[i] * wobble_scale * life

                angles = self.rotation[i] + np.linspace(0.0, 2.0 * math.pi, segments + 1)

                radius = self.radius[i] + wobble_amount * np.sin(angles * wobble_frequency)

                x = cx + radius * np.cos(angles)
                y = cy + radius * np.sin(angles)

                out.append((np.column_stack([x, y]).astype(np.float32), float(life)))

            return out

        def shells(self, center, sides: int):

            cx, cy = center

            out = []

            for i in np.nonzero(self.alive)[0]:

                life = 1.0 - (self.age[i] / max(self.lifetime[i], 1e-6))

                visible_sides = max(3, int(sides * min(life * 1.4, 1.0)))

                angles = self.rotation[i] + np.linspace(0.0, 2.0 * math.pi, visible_sides + 1)

                x = cx + self.radius[i] * np.cos(angles)
                y = cy + self.radius[i] * np.sin(angles)

                out.append((np.column_stack([x, y]).astype(np.float32), float(life)))

            return out

        def kick(self, positions, center, gain: float = 1.0, band: float = 16.0):

            positions = np.array(positions, dtype=np.float32, copy=True)

            if positions.shape[0] == 0:

                return positions

            cx, cy = center

            dx = positions[:, 0] - cx
            dy = positions[:, 1] - cy

            dist = np.hypot(dx, dy) + 1e-6

            for i in np.nonzero(self.alive)[0]:

                hit = np.abs(dist - self.radius[i]) < band

                if not np.any(hit):
                    continue

                push = self.strength[i] * gain

                positions[hit, 0] += (dx[hit] / dist[hit]) * push
                positions[hit, 1] += (dy[hit] / dist[hit]) * push

            return positions


    class ChaosField:

        def __init__(self, capacity: int, random=None):

            self.capacity = capacity
            self.random = random

            self.x = np.array(
                [random.uniform(-1.5, 1.5) for _ in range(capacity)], dtype=np.float32
            )

            self.y = np.array(
                [random.uniform(-1.5, 1.5) for _ in range(capacity)], dtype=np.float32
            )

            self.a = 1.1
            self.b = -1.8
            self.c = 1.9
            self.d = -1.5

            self._kick = 0.0

        def set_parameters(self, a: float, b: float, c: float, d: float):

            self.a = a
            self.b = b
            self.c = c
            self.d = d

        def detonate(self, strength: float):

            self._kick = max(self._kick, strength)

        def update(self, dt: float, reseed_fraction: float = 0.02):

            self._kick *= math.exp(-dt * 3.0)

            x, y = self.x, self.y

            self.x = (np.sin(self.a * y) - np.cos(self.b * x)).astype(np.float32)
            self.y = (np.sin(self.c * x) - np.cos(self.d * y)).astype(np.float32)

            reseed_count = max(1, int(self.capacity * reseed_fraction))

            indices = self.random.sample(
                range(self.capacity), min(reseed_count, self.capacity)
            )

            for i in indices:

                self.x[i] = self.random.uniform(-1.5, 1.5)
                self.y[i] = self.random.uniform(-1.5, 1.5)

        def points(self, center, scale: float):

            cx, cy = center

            effective_scale = scale * (1.0 + self._kick)

            px = cx + self.x * effective_scale
            py = cy + self.y * effective_scale

            return np.column_stack([px, py]).astype(np.float32)

    def lightning_bolt(origin, angle: float, length: float, depth: int, jitter=None, random=None):

        ox, oy = origin

        if jitter is None:

            jitter = length * 0.18

        tip = (
            ox + math.cos(angle) * length,
            oy + math.sin(angle) * length,
        )

        points = [origin]

        def _displace(p0, p1, level, j):

            if level <= 0:

                points.append(p1)

                return

            mx, my = (p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5

            dx, dy = p1[0] - p0[0], p1[1] - p0[1]

            seg_length = math.hypot(dx, dy)

            if seg_length > 1e-6:

                nx, ny = -dy / seg_length, dx / seg_length

            else:

                nx, ny = 0.0, 0.0

            offset = random.uniform(-j, j)

            mid = (mx + nx * offset, my + ny * offset)

            _displace(p0, mid, level - 1, j * 0.55)
            _displace(mid, p1, level - 1, j * 0.55)

        _displace(origin, tip, depth, jitter)

        return np.array(points, dtype=np.float32)

    def subdivide_triangle(triangle, depth: int, jitter: float = 0.0, random=None):

        p0, p1, p2 = (np.asarray(p, dtype=np.float32) for p in triangle)

        segments = []

        def _mid(a, b):

            m = (a + b) * 0.5

            if jitter and random is not None:

                m = m + np.array(
                    [random.uniform(-jitter, jitter), random.uniform(-jitter, jitter)],
                    dtype=np.float32,
                )

            return m

        def _recurse(a, b, c, level):

            if level <= 0:

                return

            ab = _mid(a, b)
            bc = _mid(b, c)
            ca = _mid(c, a)

            segments.append((ab, bc))
            segments.append((bc, ca))
            segments.append((ca, ab))

            _recurse(a, ab, ca, level - 1)
            _recurse(ab, b, bc, level - 1)
            _recurse(ca, bc, c, level - 1)

        _recurse(p0, p1, p2, depth)

        return segments

    def radial_ring(radius, base_angle: float = 0.0, angle_span=None, center=(0.0, 0.0), close_loop: bool = True):

        span = angle_span if angle_span is not None else 2.0 * math.pi

        cx, cy = center

        n = len(radius)

        angles = base_angle + (np.arange(n) / n) * span

        x = cx + radius * np.cos(angles)
        y = cy + radius * np.sin(angles)

        points = np.column_stack([x, y]).astype(np.float32)

        if close_loop:

            points = np.vstack([points, points[0]])

        return points

    def fixed_dashes(positions, dx: float, dy: float, center=(0.0, 0.0)):

        cx, cy = center

        positions = np.asarray(positions, dtype=np.float32)

        offset = np.array([cx, cy], dtype=np.float32)

        starts = positions + offset
        ends = starts + np.array([dx, dy], dtype=np.float32)

        return np.stack([starts, ends], axis=1).astype(np.float32)

    def life_dashes(
        positions,
        life,
        center=(0.0, 0.0),
        size_base: float = 1.0,
        size_scale: float = 1.0,
    ):

        cx, cy = center

        positions = np.asarray(positions, dtype=np.float32)
        life = np.asarray(life, dtype=np.float32)

        x = positions[:, 0] + cx
        y = positions[:, 1] + cy

        size = size_base + life * size_scale

        starts = np.column_stack([x - size, y]).astype(np.float32)
        ends = np.column_stack([x + size, y]).astype(np.float32)

        return np.stack([starts, ends], axis=1).astype(np.float32)



__all__ = [
    "EmberField",
    "spectrum_ring",
    "BurstField",
    "RingField",
    "ChaosField",
    "lightning_bolt",
    "subdivide_triangle",
    "radial_ring",
    "NATIVE_AVAILABLE",
    "BoidSwarm",
    "fixed_dashes",
    "life_dashes"
]

