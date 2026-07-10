#pragma once

#ifdef __APPLE__

#include <OpenGL/gl3.h>

#elif defined(__arm__) || defined(__aarch64__)

#include <GLES2/gl2.h>
#include <GLES2/gl2ext.h>

/*
 * OpenGL ES 2.0 exposes VAOs through
 * GL_OES_vertex_array_object.
 */

#define glGenVertexArrays    glGenVertexArraysOES
#define glBindVertexArray    glBindVertexArrayOES
#define glDeleteVertexArrays glDeleteVertexArraysOES

#else

#include <GL/gl.h>

#endif