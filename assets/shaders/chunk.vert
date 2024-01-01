#version 330 core

layout (location = 0) in uint packed_data;

int x, y, z, voxel_id, face_id, ao_id, flip_id;

uniform mat4 uProjection;
uniform mat4 uView;
uniform mat4 uModel;

out vec3 voxel_color;
out vec2 voxel_uv;
out float shade;

const float ao_shades[4] = float[](
    0.7, 0.8, 0.9, 1.0
);
const vec2 uv_coords[4] = vec2[](
    vec2(0, 0), vec2(0, 1), vec2(1, 0), vec2(1, 1)
);
const int uv_indices[24] = int[](
    1, 0, 2, 1, 2, 3,
    3, 0, 2, 3, 1, 0,
    3, 1, 0, 3, 0, 2,
    1, 2, 3, 1, 0, 2
);
const float shading[6] = float[](
    // top bottom right left back front
    1.0, 0.7, 0.8, 0.8, 0.7, 0.9
);

vec3 colorHash(float idx) {
    // vibrant colors
    float r = fract(sin(idx * 12.9898) * 43758.5453);
    float g = fract(sin(idx * 4.1414) * 43758.5453);
    float b = fract(sin(idx * 7.1414) * 43758.5453);
    return vec3(r, g, b);
}

void unpack(uint packed_data) {
    // x: 6 bits, y: 6 bits, z: 6 bits, voxel_id: 8 bits, face_id: 3 bits, ao: 2 bits, flip: 1 bit
    x = int(packed_data >> 26) & 0x3F;
    y = int(packed_data >> 20) & 0x3F;
    z = int(packed_data >> 14) & 0x3F;
    voxel_id = int(packed_data >> 6) & 0xFF;
    face_id = int(packed_data >> 3) & 0x7;
    ao_id = int(packed_data >> 1) & 0x3;
    flip_id = int(packed_data) & 0x1;
}

void main() {
    unpack(packed_data);
    vec3 in_position = vec3(x, y, z);
    voxel_color = colorHash(float(voxel_id));
    int uv_idx = gl_VertexID % 6 + ((face_id & 1) + flip_id * 2) * 6;
    voxel_uv = uv_coords[uv_indices[uv_idx]];
    shade = shading[face_id] * ao_shades[ao_id];
    gl_Position = uProjection * uView * uModel * vec4(in_position, 1.0);
}
