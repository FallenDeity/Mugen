#version 330 core

layout (location = 0) in ivec3 in_position;
layout (location = 1) in int voxel_id;
layout (location = 2) in int face_id;

uniform mat4 uProjection;
uniform mat4 uView;
uniform mat4 uModel;

out vec3 voxel_color;
out vec2 voxel_uv;

const vec2 uv_coords[4] = vec2[](
    vec2(0, 0), vec2(0, 1), vec2(1, 0), vec2(1, 1)
);
const int uv_indices[12] = int[](
    1, 0, 2, 1, 2, 3,
    3, 0, 2, 3, 1, 0
);

vec3 colorHash(float id) {
    float r = fract(sin(id) * 43758.5453);
    float g = fract(sin(id + 1.0) * 43758.5453);
    float b = fract(sin(id + 2.0) * 43758.5453);
    return vec3(r, g, b);
}

void main() {
    voxel_color = colorHash(float(voxel_id));
    int uv_idx = gl_VertexID % 6 + (face_id & 1) * 6;
    voxel_uv = uv_coords[uv_indices[uv_idx]];
    gl_Position = uProjection * uView * uModel * vec4(in_position, 1.0);
}
