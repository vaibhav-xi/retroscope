precision mediump float;

uniform vec3 u_color;
uniform float u_alpha;
uniform float u_size;
uniform float u_intensity;

varying vec3 v_texcoord;

void main()
{
    float u = v_texcoord.x;
    float v = v_texcoord.y;
    float len = v_texcoord.z;

    float sigma = max(u_size * 0.6, 0.5);

    float perpendicular = exp(-(v * v) / (2.0 * sigma * sigma));
    float longitudinal = clamp(min(u, len - u) / sigma + 1.0, 0.0, 1.0);
    float density = u_intensity / max(len, sigma);

    float glow = clamp(perpendicular * mix(0.4, 1.0, longitudinal) * density, 0.0, 1.0);

    gl_FragColor = vec4(u_color, u_alpha * glow);
}
