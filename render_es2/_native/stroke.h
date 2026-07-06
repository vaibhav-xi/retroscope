#ifndef RETROSCOPE_STROKE_H
#define RETROSCOPE_STROKE_H

#ifdef __cplusplus
extern "C" {
#endif

int stroke_build(

    const float *points,

    int point_count,

    float half_width,

    float *vertices

);

#ifdef __cplusplus
}
#endif

#endif