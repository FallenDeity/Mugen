#version 330 core

layout (location = 0) in vec2 tex_coord;
layout (location = 1) in vec3 in_position;

uniform mat4 uProjection;
uniform mat4 uView;
uniform int waterArea;
uniform float waterLine;

out vec2 uv;


void main() {
    vec3 pos = in_position;
    pos.xz *= waterArea;
    pos.xz -= 0.33 * waterArea;

    pos.y += waterLine;
    uv = tex_coord * waterArea;
    gl_Position = uProjection * uView * vec4(pos, 1.0);
}