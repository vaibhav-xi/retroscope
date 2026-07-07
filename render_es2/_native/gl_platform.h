// gl_platform.h

#pragma once

#ifdef __APPLE__

#include <OpenGL/gl3.h>

#elif defined(__arm__) || defined(__aarch64__)

#include <GLES2/gl2.h>

#else

#include <GL/gl.h>

#endif