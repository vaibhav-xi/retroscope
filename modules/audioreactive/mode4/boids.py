
from __future__ import annotations

import numpy as np


class BoidSwarm:

    def __init__(
        self,
        capacity: int,
        random,
        neighbor_radius: float = 70.0,
    ):

        self.capacity = capacity
        self.random = random
        self.neighbor_radius = neighbor_radius

        angle = np.array(
            [
                self.random.uniform(0.0, 2.0 * np.pi)
                for _ in range(capacity)
            ],
            dtype=np.float32,
        )

        radius = np.array(
            [
                self.random.uniform(20.0, 120.0)
                for _ in range(capacity)
            ],
            dtype=np.float32,
        )

        self.pos_x = (radius * np.cos(angle)).astype(np.float32)
        self.pos_y = (radius * np.sin(angle)).astype(np.float32)

        self.vel_x = np.array(
            [
                self.random.uniform(-20.0, 20.0)
                for _ in range(capacity)
            ],
            dtype=np.float32,
        )

        self.vel_y = np.array(
            [
                self.random.uniform(-20.0, 20.0)
                for _ in range(capacity)
            ],
            dtype=np.float32,
        )

    # ---------------------------------------------------------

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

        dx = self.pos_x[:, None] - self.pos_x[None, :]
        dy = self.pos_y[:, None] - self.pos_y[None, :]

        dist2 = dx * dx + dy * dy

        np.fill_diagonal(dist2, np.inf)

        neighbor_mask = dist2 < (self.neighbor_radius ** 2)

        counts = np.maximum(neighbor_mask.sum(axis=1), 1)

        avg_x = (
            np.where(neighbor_mask, self.pos_x[None, :], 0.0).sum(axis=1)
            / counts
        )

        avg_y = (
            np.where(neighbor_mask, self.pos_y[None, :], 0.0).sum(axis=1)
            / counts
        )

        cohesion_x = (avg_x - self.pos_x) * cohesion
        cohesion_y = (avg_y - self.pos_y) * cohesion

        avg_vx = (
            np.where(neighbor_mask, self.vel_x[None, :], 0.0).sum(axis=1)
            / counts
        )

        avg_vy = (
            np.where(neighbor_mask, self.vel_y[None, :], 0.0).sum(axis=1)
            / counts
        )

        align_x = (avg_vx - self.vel_x) * alignment
        align_y = (avg_vy - self.vel_y) * alignment

        close_mask = dist2 < (self.neighbor_radius * 0.35) ** 2

        inv_dist = np.where(
            close_mask,
            1.0 / np.sqrt(np.maximum(dist2, 1e-6)),
            0.0,
        )

        separation_x = (dx * inv_dist).sum(axis=1) * separation
        separation_y = (dy * inv_dist).sum(axis=1) * separation

        fx, fy = focus

        focus_x = (fx - self.pos_x) * 0.015
        focus_y = (fy - self.pos_y) * 0.015

        jitter_x = np.random.uniform(-jitter, jitter, self.capacity)
        jitter_y = np.random.uniform(-jitter, jitter, self.capacity)
        
        if threat is not None and threat_strength > 0.0:

            tx, ty = threat

            tdx = self.pos_x - tx
            tdy = self.pos_y - ty

            tdist = np.sqrt(tdx * tdx + tdy * tdy) + 1e-6

            flee_radius = 160.0

            influence = np.clip(1.0 - tdist / flee_radius, 0.0, 1.0)
            influence = influence * influence

            flee_x = (tdx / tdist) * influence * threat_strength
            flee_y = (tdy / tdist) * influence * threat_strength

        else:

            flee_x = 0.0
            flee_y = 0.0

        dist_from_center = np.hypot(self.pos_x, self.pos_y) + 1e-6

        leash = np.clip((dist_from_center - 200.0) * 0.4, 0.0, None)

        leash_x = -(self.pos_x / dist_from_center) * leash
        leash_y = -(self.pos_y / dist_from_center) * leash

        self.vel_x += (
            cohesion_x
            + align_x
            + separation_x
            + focus_x
            + jitter_x
            + leash_x
            + flee_x
        ) * dt

        self.vel_y += (
            cohesion_y
            + align_y
            + separation_y
            + focus_y
            + jitter_y
            + leash_y
            + flee_y
        ) * dt

        speed = np.hypot(self.vel_x, self.vel_y)

        too_fast = speed > max_speed

        scale = np.where(
            too_fast,
            max_speed / np.maximum(speed, 1e-6),
            1.0,
        )

        self.vel_x *= scale
        self.vel_y *= scale

        self.pos_x += self.vel_x * dt
        self.pos_y += self.vel_y * dt

    # ---------------------------------------------------------

    def neighbor_links(self, max_links: int, link_radius: float | None = None, center=(0.0, 0.0)):

        cx, cy = center

        radius = link_radius if link_radius is not None else self.neighbor_radius * 0.55

        dx = self.pos_x[:, None] - self.pos_x[None, :]
        dy = self.pos_y[:, None] - self.pos_y[None, :]

        dist2 = dx * dx + dy * dy

        i_idx, j_idx = np.triu_indices(self.capacity, k=1)

        pair_dist2 = dist2[i_idx, j_idx]

        mask = pair_dist2 < (radius * radius)

        i_idx = i_idx[mask]
        j_idx = j_idx[mask]
        pair_dist2 = pair_dist2[mask]

        if len(i_idx) > max_links:

            order = np.argsort(pair_dist2)[:max_links]

            i_idx = i_idx[order]
            j_idx = j_idx[order]

        for i, j in zip(i_idx, j_idx):

            yield np.array(
                [
                    [self.pos_x[i] + cx, self.pos_y[i] + cy],
                    [self.pos_x[j] + cx, self.pos_y[j] + cy],
                ],
                dtype=np.float32,
            )

    # ---------------------------------------------------------

    def render_points(self, center=(0.0, 0.0)):

        cx, cy = center

        speed = np.hypot(self.vel_x, self.vel_y) + 1e-6

        dir_x = self.vel_x / speed
        dir_y = self.vel_y / speed

        perp_x = -dir_y
        perp_y = dir_x

        size = 6.0

        for i in range(self.capacity):

            nose = (
                cx + self.pos_x[i] + dir_x[i] * size,
                cy + self.pos_y[i] + dir_y[i] * size,
            )

            left = (
                cx + self.pos_x[i] - dir_x[i] * size * 0.6 + perp_x[i] * size * 0.5,
                cy + self.pos_y[i] - dir_y[i] * size * 0.6 + perp_y[i] * size * 0.5,
            )

            right = (
                cx + self.pos_x[i] - dir_x[i] * size * 0.6 - perp_x[i] * size * 0.5,
                cy + self.pos_y[i] - dir_y[i] * size * 0.6 - perp_y[i] * size * 0.5,
            )

            yield np.array(
                [nose, left, right, nose],
                dtype=np.float32,
            )
