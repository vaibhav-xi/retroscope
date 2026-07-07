#include "stroke.h"
#include "geometry.h"
#include <stdio.h>

#define WIDTH 800.0f
#define HEIGHT 480.0f

static inline float ndc_x(float x)
{
    return (2.0f * x / WIDTH) - 1.0f;
}

static inline float ndc_y(float y)
{
    return 1.0f - (2.0f * y / HEIGHT);
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

        push2(&dst, ndc_x(l1x), ndc_y(l1y));
        push2(&dst, ndc_x(r1x), ndc_y(r1y));
        push2(&dst, ndc_x(l2x), ndc_y(l2y));

        push2(&dst, ndc_x(l2x), ndc_y(l2y));
        push2(&dst, ndc_x(r1x), ndc_y(r1y));
        push2(&dst, ndc_x(r2x), ndc_y(r2y));
    }

    int written = (int)(dst - vertices);

    printf(
        "written=%d max=%d\n",
        written,
        (point_count - 1) * 12
    );

    return written;
}