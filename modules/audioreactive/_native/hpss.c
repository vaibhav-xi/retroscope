/* modules/audioreactive/_native/hpss.c */
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define PY_ARRAY_UNIQUE_SYMBOL AUDIOREACTIVE_ARRAY_API
#define NO_IMPORT_ARRAY
#include <numpy/arrayobject.h>

#include "hpss.h"

#define HPSS_MAX_WINDOW 64

static inline float
median_of(float *buf, int n)
{
    /* Insertion sort - n is always small (<= HPSS_MAX_WINDOW), so
     * this beats a generic sort/selection algorithm here. */

    for (int i = 1; i < n; i++)
    {
        float key = buf[i];
        int j = i - 1;

        while (j >= 0 && buf[j] > key)
        {
            buf[j + 1] = buf[j];
            j--;
        }

        buf[j + 1] = key;
    }

    if (n % 2 == 1)
    {
        return buf[n / 2];
    }

    return 0.5f * (buf[n / 2 - 1] + buf[n / 2]);
}

/*
 * hpss_separate(magnitude, history, filled, freq_window)
 *
 * Replaces two numpy calls per audio callback:
 *   - np.median(history[:filled], axis=0)          (harmonic)
 *   - sliding np.median over `freq_window` bins     (percussive)
 *
 * `history` is the full (T, N) circular buffer (order doesn't
 * matter for a median), `filled` is how many of its rows are
 * valid so far - matches the existing Python fallback exactly.
 */

PyObject *
hpss_separate(
    PyObject *Py_UNUSED(self),
    PyObject *args,
    PyObject *kwds
)
{
    PyObject *magnitude_obj;
    PyObject *history_obj;
    int filled;
    int freq_window;

    static char *keywords[] = {
        "magnitude", "history", "filled", "freq_window", NULL
    };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "OOii", keywords,
            &magnitude_obj, &history_obj, &filled, &freq_window))
    {
        return NULL;
    }

    PyArrayObject *magnitude = (PyArrayObject *)PyArray_FROM_OTF(
        magnitude_obj, NPY_FLOAT32, NPY_ARRAY_IN_ARRAY | NPY_ARRAY_FORCECAST);

    PyArrayObject *history = (PyArrayObject *)PyArray_FROM_OTF(
        history_obj, NPY_FLOAT32, NPY_ARRAY_IN_ARRAY | NPY_ARRAY_FORCECAST);

    if (magnitude == NULL || history == NULL)
    {
        Py_XDECREF(magnitude);
        Py_XDECREF(history);
        return NULL;
    }

    npy_intp n = PyArray_DIM(magnitude, 0);

    float *mag = (float *)PyArray_DATA(magnitude);
    float *hist = (float *)PyArray_DATA(history);

    if (freq_window > HPSS_MAX_WINDOW)
    {
        freq_window = HPSS_MAX_WINDOW;
    }

    if (filled > HPSS_MAX_WINDOW)
    {
        filled = HPSS_MAX_WINDOW;
    }

    npy_intp dims[1] = { n };

    PyArrayObject *harmonic =
        (PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_FLOAT32);

    PyArrayObject *percussive =
        (PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_FLOAT32);

    if (harmonic == NULL || percussive == NULL)
    {
        Py_XDECREF(harmonic);
        Py_XDECREF(percussive);
        Py_DECREF(magnitude);
        Py_DECREF(history);
        return NULL;
    }

    float *harmonic_out = (float *)PyArray_DATA(harmonic);
    float *percussive_out = (float *)PyArray_DATA(percussive);

    float time_buf[HPSS_MAX_WINDOW];
    float freq_buf[HPSS_MAX_WINDOW];

    int half = freq_window / 2;

    for (npy_intp i = 0; i < n; i++)
    {
        /*
         * Harmonic: median of this bin across the last `filled`
         * history frames.
         */

        if (filled >= 3)
        {
            for (int t = 0; t < filled; t++)
            {
                time_buf[t] = hist[t * n + i];
            }

            harmonic_out[i] = median_of(time_buf, filled);
        }
        else
        {
            harmonic_out[i] = mag[i];
        }

        /*
         * Percussive: median of a `freq_window`-wide neighborhood
         * around bin i, edges clamped (matches np.pad(mode="edge")).
         */

        for (int w = 0; w < freq_window; w++)
        {
            npy_intp idx = i + w - half;

            if (idx < 0)
            {
                idx = 0;
            }
            else if (idx >= n)
            {
                idx = n - 1;
            }

            freq_buf[w] = mag[idx];
        }

        percussive_out[i] = median_of(freq_buf, freq_window);
    }

    Py_DECREF(magnitude);
    Py_DECREF(history);

    return Py_BuildValue(
        "(OO)",
        (PyObject *)harmonic,
        (PyObject *)percussive
    );
}
