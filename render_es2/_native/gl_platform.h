#pragma once

#ifdef __APPLE__

#include <OpenGL/gl3.h>

#elif defined(__arm__) || defined(__aarch64__)

#include <GLES2/gl2.h>
#include <GLES2/gl2ext.h>

/*
 * Raspberry Pi Mesa exports the core VAO symbols:
 *
 *     glGenVertexArrays
 *     glBindVertexArray
 *     glDeleteVertexArrays
 *
 * but GLES2 headers only declare the OES versions.
 *
 * Declare the core entry points ourselves.
 */

#ifdef __cplusplus
extern "C" {
#endif

GL_APICALL void GL_APIENTRY
glGenVertexArrays(
    GLsizei n,
    GLuint *arrays
);

GL_APICALL void GL_APIENTRY
glBindVertexArray(
    GLuint array
);

GL_APICALL void GL_APIENTRY
glDeleteVertexArrays(
    GLsizei n,
    const GLuint *arrays
);

#ifdef __cplusplus
}
#endif

#else

#include <GL/gl.h>

#endif