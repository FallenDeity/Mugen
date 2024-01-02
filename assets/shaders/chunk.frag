#version 330 core

layout (location = 0) out vec4 fragColor;

const vec3 gamma = vec3(2.2);
const vec3 invGamma = vec3(1.0 / 2.2);

uniform sampler2DArray uTexture;
uniform vec3 bgColor;
uniform float waterLine;

in vec3 voxel_color;
in vec2 voxel_uv;
in float shade;
in vec3 frag_world_pos;
flat in int voxel_id, face_id;

void main() {
    vec2 face_uv = voxel_uv;
    face_uv.x = voxel_uv.x / 3.0 - min(face_id, 2) / 3.0;
    vec3 texColor = texture(uTexture, vec3(face_uv, voxel_id)).rgb;
    texColor = pow(texColor, gamma);
    texColor *= shade;
    // underwater effect
    if (frag_world_pos.y < waterLine) texColor *= vec3(0.0, 0.3, 1.0);
    //fog
    float fog_dist = gl_FragCoord.z / gl_FragCoord.w;
    texColor = mix(texColor, bgColor, (1.0 - exp2(-0.00001 * fog_dist * fog_dist)));
    texColor = pow(texColor, invGamma);
    fragColor = vec4(texColor, 1.0);
}
