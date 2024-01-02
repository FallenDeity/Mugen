#version 330 core

layout (location = 0) in vec3 in_position;

uniform mat4 uProjection;
uniform mat4 uView;
uniform int center;
uniform float uTime;
uniform float cloudScale;

void main() {
    vec3 pos = vec3(in_position);
    pos.xz -= center;
    pos.xz *= cloudScale;
    pos.xz += center;
    float time = 300 * sin(0.01 * uTime);
    pos.xz += time;
    gl_Position = uProjection * uView * vec4(pos, 1.0);
}
