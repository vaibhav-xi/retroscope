#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define PY_ARRAY_UNIQUE_SYMBOL AUDIOREACTIVE_ARRAY_API
#define NO_IMPORT_ARRAY
#include <numpy/arrayobject.h>

#include <math.h>
#include <time.h>

#include "fractal.h"
#include "rng.h"

static void
displace(
    float p0x, float p0y,
    float p1x, float p1y,
    int depth,
    float jitter,
    RngState *rng,
    float *out,
    int *index
)
{
    if (depth <= 0)
    {
        out[(*index) * 2 + 0] = p1x;
        out[(*index) * 2 + 1] = p1y;
        (*index)++;
        return;
    }

    float mx = (p0x + p1x) * 0.5f;
    float my = (p0y + p1y) * 0.5f;

    float dx = p1x - p0x;
    float dy = p1y - p0y;

    float length = sqrtf(dx * dx + dy * dy);

    float nx = 0.0f, ny = 0.0f;

    if (length > 1e-6f)
    {
        nx = -dy / length;
        ny = dx / length;
    }

    float offset = rng_uniform(rng, -jitter, jitter);

    float midx = mx + nx * offset;
    float midy = my + ny * offset;

    displace(p0x, p0y, midx, midy, depth - 1, jitter * 0.55f, rng, out, index);
    displace(midx, midy, p1x, p1y, depth - 1, jitter * 0.55f, rng, out, index);
}

/* --------------------------------------------------------- */

PyObject *
fractal_lightning_bolt(
    PyObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    double origin_x, origin_y, angle, length;
    int depth;
    double jitter = -1.0; /* sentinel: default to length * 0.18 */
    unsigned long seed = 0;

    static char *keywords[] = {
        "origin_x", "origin_y", "angle", "length", "depth",
        "jitter", "seed", NULL
    };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "ddddi|dk", keywords,
            &origin_x, &origin_y, &angle, &length, &depth, &jitter, &seed))
    {
        return NULL;
    }

    if (jitter < 0.0)
    {
        jitter = length * 0.18;
    }

    RngState rng;

    if (seed == 0)
    {
        seed = (unsigned long)time(NULL);
    }

    rng_seed(&rng, (uint32_t)seed);

    float tip_x = (float)origin_x + cosf((float)angle) * (float)length;
    float tip_y = (float)origin_y + sinf((float)angle) * (float)length;

    int point_count = 1;

    for (int i = 0; i < depth; i++)
    {
        point_count *= 2;
    }

    point_count += 1;

    npy_intp dims[2] = { point_count, 2 };

    PyArrayObject *result =
        (PyArrayObject *)PyArray_SimpleNew(2, dims, NPY_FLOAT32);

    if (result == NULL)
    {
        return NULL;
    }

    float *out = (float *)PyArray_DATA(result);

    out[0] = (float)origin_x;
    out[1] = (float)origin_y;

    int index = 1;

    displace(
        (float)origin_x, (float)origin_y,
        tip_x, tip_y,
        depth,
        (float)jitter,
        &rng,
        out,
        &index
    );

    return (PyObject *)result;
}

/* --------------------------------------------------------- */

static void
subdivide(
    float ax, float ay,
    float bx, float by,
    float cx, float cy,
    int depth,
    float jitter,
    RngState *rng,
    float *out,
    int *index
)
{
    if (depth <= 0)
    {
        return;
    }

    float abx = (ax + bx) * 0.5f;
    float aby = (ay + by) * 0.5f;

    float bcx = (bx + cx) * 0.5f;
    float bcy = (by + cy) * 0.5f;

    float cax = (cx + ax) * 0.5f;
    float cay = (cy + ay) * 0.5f;

    if (jitter > 0.0f)
    {
        abx += rng_uniform(rng, -jitter, jitter);
        aby += rng_uniform(rng, -jitter, jitter);
        bcx += rng_uniform(rng, -jitter, jitter);
        bcy += rng_uniform(rng, -jitter, jitter);
        cax += rng_uniform(rng, -jitter, jitter);
        cay += rng_uniform(rng, -jitter, jitter);
    }

    out[(*index) * 4 + 0] = abx;
    out[(*index) * 4 + 1] = aby;
    out[(*index) * 4 + 2] = bcx;
    out[(*index) * 4 + 3] = bcy;
    (*index)++;

    out[(*index) * 4 + 0] = bcx;
    out[(*index) * 4 + 1] = bcy;
    out[(*index) * 4 + 2] = cax;
    out[(*index) * 4 + 3] = cay;
    (*index)++;

    out[(*index) * 4 + 0] = cax;
    out[(*index) * 4 + 1] = cay;
    out[(*index) * 4 + 2] = abx;
    out[(*index) * 4 + 3] = aby;
    (*index)++;

    /*
     * Jitter is intentionally NOT decayed per level here - unlike
     * displace() above, the pure-Python subdivide_triangle() this
     * replaces passes the same jitter value at every recursion depth.
     */

    subdivide(ax, ay, abx, aby, cax, cay, depth - 1, jitter, rng, out, index);
    subdivide(abx, aby, bx, by, bcx, bcy, depth - 1, jitter, rng, out, index);
    subdivide(cax, cay, bcx, bcy, cx, cy, depth - 1, jitter, rng, out, index);
}

/* --------------------------------------------------------- */

PyObject *
fractal_subdivide_triangle(
    PyObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    double ax, ay, bx, by, cx, cy;
    int depth;
    double jitter = 0.0;
    unsigned long seed = 0;

    static char *keywords[] = {
        "ax", "ay", "bx", "by", "cx", "cy", "depth", "jitter", "seed", NULL
    };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "ddddddi|dk", keywords,
            &ax, &ay, &bx, &by, &cx, &cy, &depth, &jitter, &seed))
    {
        return NULL;
    }

    RngState rng;

    if (seed == 0)
    {
        seed = (unsigned long)time(NULL);
    }

    rng_seed(&rng, (uint32_t)seed);

    int segment_count = 0;
    int power = 1;

    for (int i = 0; i < depth; i++)
    {
        segment_count += 3 * power;
        power *= 3;
    }

    if (segment_count < 1)
    {
        npy_intp empty_dims[3] = { 0, 2, 2 };
        return PyArray_SimpleNew(3, empty_dims, NPY_FLOAT32);
    }

    npy_intp dims[3] = { segment_count, 2, 2 };

    PyArrayObject *result =
        (PyArrayObject *)PyArray_SimpleNew(3, dims, NPY_FLOAT32);

    if (result == NULL)
    {
        return NULL;
    }

    float *out = (float *)PyArray_DATA(result);

    int index = 0;

    subdivide(
        (float)ax, (float)ay,
        (float)bx, (float)by,
        (float)cx, (float)cy,
        depth,
        (float)jitter,
        &rng,
        out,
        &index
    );

    return (PyObject *)result;
}
