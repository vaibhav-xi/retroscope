#include "stroke.h"
#include "geometry.h"
#include <stdio.h>

static inline float ndc_x(float x, float screen_width)
{
    return (2.0f * x / screen_width) - 1.0f;
}

static inline float ndc_y(float y, float screen_height)
{
    return 1.0f - (2.0f * y / screen_height);
}

static inline void push2(
    float **dst,
    float x,
    float y
)
{
    *(*dst)++ = x;
    *(*dst)++ = y;
}

int stroke_build(

    const float *points,

    int point_count,

    float half_width,

    float screen_width,

    float screen_height,

    float *vertices

)
{
    float *dst = vertices;

    for (int i = 0; i < point_count - 1; ++i)
    {
        float x1 = points[i * 2 + 0];
        float y1 = points[i * 2 + 1];

        float x2 = points[(i + 1) * 2 + 0];
        float y2 = points[(i + 1) * 2 + 1];

        float dx = x2 - x1;
        float dy = y2 - y1;

        geometry_normalize(
            &dx,
            &dy
        );

        float px;
        float py;

        geometry_perpendicular(
            dx,
            dy,
            &px,
            &py
        );

        float l1x = x1 + px * half_width;
        float l1y = y1 + py * half_width;

        float r1x = x1 - px * half_width;
        float r1y = y1 - py * half_width;

        float l2x = x2 + px * half_width;
        float l2y = y2 + py * half_width;

        float r2x = x2 - px * half_width;
        float r2y = y2 - py * half_width;

        push2(&dst, ndc_x(l1x, screen_width), ndc_y(l1y, screen_height));
        push2(&dst, ndc_x(r1x, screen_width), ndc_y(r1y, screen_height));
        push2(&dst, ndc_x(l2x, screen_width), ndc_y(l2y, screen_height));

        push2(&dst, ndc_x(l2x, screen_width), ndc_y(l2y, screen_height));
        push2(&dst, ndc_x(r1x, screen_width), ndc_y(r1y, screen_height));
        push2(&dst, ndc_x(r2x, screen_width), ndc_y(r2y, screen_height));
    }

    int written = (int)(dst - vertices);

    return written;
}
