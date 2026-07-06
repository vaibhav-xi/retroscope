#include <math.h>

#include "geometry.h"

/*----------------------------------------------------------*/

float geometry_length(
    float x,
    float y
)
{
    return sqrtf(
        x * x +
        y * y
    );
}

/*----------------------------------------------------------*/

void geometry_normalize(
    float *x,
    float *y
)
{
    float length = geometry_length(
        *x,
        *y
    );

    if (length == 0.0f)
    {
        return;
    }

    *x /= length;
    *y /= length;
}

/*----------------------------------------------------------*/

void geometry_perpendicular(
    float x,
    float y,
    float *px,
    float *py
)
{
    *px = -y;
    *py = x;
}