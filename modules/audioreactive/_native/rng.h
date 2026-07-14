#ifndef AUDIO_NATIVE_RNG_H
#define AUDIO_NATIVE_RNG_H

#include <stdint.h>

typedef struct
{
    uint32_t state;

} RngState;

static inline void
rng_seed(
    RngState *rng,
    uint32_t seed
)
{
    rng->state = seed ? seed : 0x9E3779B9u;
}

static inline uint32_t
rng_next(
    RngState *rng
)
{
    uint32_t x = rng->state;

    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;

    rng->state = x;

    return x;
}

static inline float
rng_uniform(
    RngState *rng,
    float lo,
    float hi
)
{
    float t =
        (float)(rng_next(rng) >> 8) /
        (float)(1 << 24);

    return lo + (hi - lo) * t;
}

#endif
