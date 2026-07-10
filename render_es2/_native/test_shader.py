from render_es2._native import Shader

vertex_source = """
attribute vec2 position;

void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
}
"""

fragment_source = """
precision mediump float;

void main()
{
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
"""

shader = Shader()

shader.create(
    vertex_source,
    fragment_source,
)

print("compiled")