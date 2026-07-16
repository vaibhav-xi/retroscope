"""
RetroScope

Shared "desktop GL" platform check.

macOS and Windows both need a desktop OpenGL Core Profile context
(with hand-written GLSL 410 shaders) instead of the native OpenGL
ES 2.0 context used on Raspberry Pi/Linux, since neither ships a
usable EGL/GLESv2 by default.
"""

import platform

IS_DESKTOP_GL = platform.system() in ("Darwin", "Windows")
