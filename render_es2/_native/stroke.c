#include "stroke.h"
#include "geometry.h"

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

        /*
        * Triangle 1
        */

        push2(&dst, l1x, l1y);
        push2(&dst, r1x, r1y);
        push2(&dst, l2x, l2y);

        /*
        * Triangle 2
        */

        push2(&dst, l2x, l2y);
        push2(&dst, r1x, r1y);
        push2(&dst, r2x, r2y);
    }

    return (int)(dst - vertices);
}