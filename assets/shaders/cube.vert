#version 330 core

layout (location = 0) in vec2 tex_coord;
layout (location = 1) in vec3 in_position;

uniform mat4 uProjection;
uniform mat4 uView;
uniform mat4 uModel;
uniform uint uMode;

const vec3 marker_colors[2] = vec3[2](vec3(1, 0, 0), vec3(0, 0, 1));

out vec3 marker_color;
out vec2 uv;


void main() {
    uv = tex_coord;
    marker_color = marker_colors[uMode];
    gl_Position = uProjection * uView * uModel * vec4((in_position - 0.5) * 1.01 + 0.5, 1.0);
}
