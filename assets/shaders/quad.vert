#version 330 core

layout(location = 0) in vec3 in_position;
layout(location = 1) in vec3 in_color;

uniform mat4 uProjection;
uniform mat4 uView;
uniform mat4 uModel;

out vec3 color;

void main() {
    color = in_color;
    gl_Position = uProjection * uView * uModel * vec4(in_position, 1.0);
}
