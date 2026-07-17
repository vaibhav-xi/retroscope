#include "stroke.h"
#include "geometry.h"

static inline float ndc_x(float x, float screen_width)
{
    return (2.0f * x / screen_width) - 1.0f;
}

static inline float ndc_y(float y, float screen_height)
{
    return 1.0f - (2.0f * y / screen_height);
}

static inline void push5(
    float **dst,
    float x, float y,
    float u, float v,
    float len
)
{
    *(*dst)++ = x;
    *(*dst)++ = y;
    *(*dst)++ = u;
    *(*dst)++ = v;
    *(*dst)++ = len;
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

        float len = geometry_length(dx, dy);

        geometry_normalize(&dx, &dy);

        float px;
        float py;

        geometry_perpendicular(dx, dy, &px, &py);

        float ex = dx * half_width;
        float ey = dy * half_width;

        float nx = px * half_width;
        float ny = py * half_width;

        float l1x = x1 - ex + nx, l1y = y1 - ey + ny;
        float r1x = x1 - ex - nx, r1y = y1 - ey - ny;
        float l2x = x2 + ex + nx, l2y = y2 + ey + ny;
        float r2x = x2 + ex - nx, r2y = y2 + ey - ny;

        float u0 = -half_width;
        float u1 = len + half_width;
        float v0 = -half_width;
        float v1 = half_width;

        push5(&dst, ndc_x(l1x, screen_width), ndc_y(l1y, screen_height), u0, v0, len);
        push5(&dst, ndc_x(r1x, screen_width), ndc_y(r1y, screen_height), u0, v1, len);
        push5(&dst, ndc_x(l2x, screen_width), ndc_y(l2y, screen_height), u1, v0, len);

        push5(&dst, ndc_x(l2x, screen_width), ndc_y(l2y, screen_height), u1, v0, len);
        push5(&dst, ndc_x(r1x, screen_width), ndc_y(r1y, screen_height), u0, v1, len);
        push5(&dst, ndc_x(r2x, screen_width), ndc_y(r2y, screen_height), u1, v1, len);
    }

    return (int)(dst - vertices);
}
