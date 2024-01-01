#version 330 core

layout (location = 0) out vec4 fragColor;

in vec3 marker_color;
in vec2 uv;

uniform sampler2D uTexture;

void main() {
    fragColor = texture(uTexture, uv);
    fragColor.rgb += marker_color;
    fragColor.a = (fragColor.r + fragColor.b > 1.0) ? 0.0 : 1.0;
}
