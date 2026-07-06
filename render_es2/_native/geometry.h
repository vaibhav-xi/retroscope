#ifndef RETROSCOPE_GEOMETRY_H
#define RETROSCOPE_GEOMETRY_H

float geometry_length(
    float x,
    float y
);

void geometry_normalize(
    float *x,
    float *y
);

void geometry_perpendicular(
    float x,
    float y,
    float *px,
    float *py
);

#endif