#pragma once

#ifdef __APPLE__

#include <OpenGL/gl3.h>

#elif defined(__arm__) || defined(__aarch64__)

#include <GLES2/gl2.h>

#define GL_GLEXT_PROTOTYPES
#include <GLES2/gl2ext.h>

#define glGenVertexArrays    glGenVertexArraysOES
#define glBindVertexArray    glBindVertexArrayOES
#define glDeleteVertexArrays glDeleteVertexArraysOES

#else

#include <GL/gl.h>

#endif