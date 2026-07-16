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

#elif defined(_WIN32)

/*
 * Windows' opengl32.dll only statically exports OpenGL 1.1.
 * Everything newer - VBOs (1.5), shaders (2.0), VAOs (3.0) - has
 * to be fetched at runtime via wglGetProcAddress() once a GL
 * context exists. gl_platform_init() (gl_platform.c) does that;
 * it must run once, right after the context is created and made
 * current, before any Mesh/Shader object is used (Window.__init__
 * calls it via _native.init_gl()).
 *
 * mesh_object.c / shader_object.c keep calling these by their
 * normal GL names with zero changes - the names below just
 * resolve to function-pointer variables instead of directly
 * linked symbols.
 */

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <GL/gl.h>

typedef char GLchar;
typedef ptrdiff_t GLsizeiptr;

#define GL_ARRAY_BUFFER     0x8892
#define GL_DYNAMIC_DRAW     0x88E8
#define GL_FRAGMENT_SHADER  0x8B30
#define GL_VERTEX_SHADER    0x8B31
#define GL_COMPILE_STATUS   0x8B81
#define GL_LINK_STATUS      0x8B82

typedef void    (WINAPI *PFNGLGENVERTEXARRAYSPROC)(GLsizei, GLuint *);
typedef void    (WINAPI *PFNGLBINDVERTEXARRAYPROC)(GLuint);
typedef void    (WINAPI *PFNGLDELETEVERTEXARRAYSPROC)(GLsizei, const GLuint *);
typedef void    (WINAPI *PFNGLGENBUFFERSPROC)(GLsizei, GLuint *);
typedef void    (WINAPI *PFNGLBINDBUFFERPROC)(GLenum, GLuint);
typedef void    (WINAPI *PFNGLBUFFERDATAPROC)(GLenum, GLsizeiptr, const void *, GLenum);
typedef void    (WINAPI *PFNGLDELETEBUFFERSPROC)(GLsizei, const GLuint *);
typedef void    (WINAPI *PFNGLENABLEVERTEXATTRIBARRAYPROC)(GLuint);
typedef void    (WINAPI *PFNGLVERTEXATTRIBPOINTERPROC)(GLuint, GLint, GLenum, GLboolean, GLsizei, const void *);
typedef void    (WINAPI *PFNGLUSEPROGRAMPROC)(GLuint);
typedef void    (WINAPI *PFNGLUNIFORM3FPROC)(GLint, GLfloat, GLfloat, GLfloat);
typedef GLuint  (WINAPI *PFNGLCREATESHADERPROC)(GLenum);
typedef void    (WINAPI *PFNGLSHADERSOURCEPROC)(GLuint, GLsizei, const GLchar *const *, const GLint *);
typedef void    (WINAPI *PFNGLCOMPILESHADERPROC)(GLuint);
typedef void    (WINAPI *PFNGLGETSHADERIVPROC)(GLuint, GLenum, GLint *);
typedef void    (WINAPI *PFNGLGETSHADERINFOLOGPROC)(GLuint, GLsizei, GLsizei *, GLchar *);
typedef void    (WINAPI *PFNGLDELETESHADERPROC)(GLuint);
typedef GLuint  (WINAPI *PFNGLCREATEPROGRAMPROC)(void);
typedef void    (WINAPI *PFNGLATTACHSHADERPROC)(GLuint, GLuint);
typedef void    (WINAPI *PFNGLLINKPROGRAMPROC)(GLuint);
typedef void    (WINAPI *PFNGLGETPROGRAMIVPROC)(GLuint, GLenum, GLint *);
typedef void    (WINAPI *PFNGLGETPROGRAMINFOLOGPROC)(GLuint, GLsizei, GLsizei *, GLchar *);
typedef void    (WINAPI *PFNGLDELETEPROGRAMPROC)(GLuint);
typedef GLint   (WINAPI *PFNGLGETUNIFORMLOCATIONPROC)(GLuint, const GLchar *);

extern PFNGLGENVERTEXARRAYSPROC glGenVertexArrays;
extern PFNGLBINDVERTEXARRAYPROC glBindVertexArray;
extern PFNGLDELETEVERTEXARRAYSPROC glDeleteVertexArrays;
extern PFNGLGENBUFFERSPROC glGenBuffers;
extern PFNGLBINDBUFFERPROC glBindBuffer;
extern PFNGLBUFFERDATAPROC glBufferData;
extern PFNGLDELETEBUFFERSPROC glDeleteBuffers;
extern PFNGLENABLEVERTEXATTRIBARRAYPROC glEnableVertexAttribArray;
extern PFNGLVERTEXATTRIBPOINTERPROC glVertexAttribPointer;
extern PFNGLUSEPROGRAMPROC glUseProgram;
extern PFNGLUNIFORM3FPROC glUniform3f;
extern PFNGLCREATESHADERPROC glCreateShader;
extern PFNGLSHADERSOURCEPROC glShaderSource;
extern PFNGLCOMPILESHADERPROC glCompileShader;
extern PFNGLGETSHADERIVPROC glGetShaderiv;
extern PFNGLGETSHADERINFOLOGPROC glGetShaderInfoLog;
extern PFNGLDELETESHADERPROC glDeleteShader;
extern PFNGLCREATEPROGRAMPROC glCreateProgram;
extern PFNGLATTACHSHADERPROC glAttachShader;
extern PFNGLLINKPROGRAMPROC glLinkProgram;
extern PFNGLGETPROGRAMIVPROC glGetProgramiv;
extern PFNGLGETPROGRAMINFOLOGPROC glGetProgramInfoLog;
extern PFNGLDELETEPROGRAMPROC glDeleteProgram;
extern PFNGLGETUNIFORMLOCATIONPROC glGetUniformLocation;

void gl_platform_init(void);

#else

#include <GL/gl.h>

#endif
