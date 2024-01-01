#version 330 core

layout (location = 0) out vec4 fragColor;

const vec3 gamma = vec3(2.2);
const vec3 invGamma = vec3(1.0 / 2.2);

uniform sampler2D uTexture;

in vec3 voxel_color;
in vec2 voxel_uv;
in float shade;

void main() {
    vec3 texColor = texture(uTexture, voxel_uv).rgb;
    texColor = pow(texColor, invGamma);
    texColor.rgb *= voxel_color;
    texColor *= shade;
    texColor = pow(texColor, gamma);
    fragColor = vec4(texColor, 1.0);
}
