precision highp float;
precision highp int;

uniform sampler2D  inTexture;
uniform float      dt, dx, dy; // assuming uniform names: uniform_dt, uniform_dx, uniform_dy

in vec2 cc;
layout (location = 0) out vec4 ocolor;

void main() {
    vec2 size = textureSize(inTexture, 0);
    vec2 ii = vec2(1., 0.) / size;
    vec2 jj = vec2(0., 1.) / size;

    float r_prev = texture(inTexture, cc).r;
    float v_prev = texture(inTexture, cc).g;
    float w_prev = texture(inTexture, cc).a;

    // Compute Laplacian in x-direction using centered differences
    vec2 delta_left_x = ii.x * -dt; 
    vec2 left_pos_x = clamp(cc + delta_left_x, 0.0, 1.0);
    vec2 right_pos_x = cc + ii.x * dt;
    
    float r_left = texture(inTexture, left_pos_x).r;
    float r_right = texture(inTexture, right_pos_x).r;

    // Adjust for Neumann (clamp) boundary conditions
    if (!left_pos_x.y) {
        left_pos_x.y += 1.0; // clamp y to [0,1]
    }
    if (!right_pos_x.y) {
        right_pos_x.y += 1.0;
    }

    float lapx = (r_right - 2.0 * r_prev + r_left) / ((dx * ii.x)^2);

    // Compute Laplacian in y-direction
    delta_y_left = jj.y * -dt; 
    left_pos_y = clamp(cc + delta_y_left, 0.0, 1.0);
    right_pos_y = cc + jj.y * dt;

    float ly = (texture(inTexture, right_pos_y).g - 2.0 * v_prev + texture(inTexture, left_pos_y).g) / ((dy * jj.y)^2);

    // Reaction term and Euler update
    float reaction_r = C_m * r_prev * (1.0f - v_prev);
    float new_r = r_prev + dt * (D * (lapx + ly) + reaction_r);

    float reaction_v = C_m * v_prev * (1.0f - w_prev);
    float new_v = v_prev + dt * (-D * (lapx + ly) + reaction_v);

    float reaction_w = C_m * w_prev * (1.0f - r_prev);
    float new_w = w_prev + dt * (-D * (lapx + ly) + reaction_w);

    // Pack the result into ocolor and clamp to [0, 1]
    vec3 color_out = vec3(new_r, new_v, new_w);
    OColor ocolor;
    ocolor.x = 0.0;
    ocolor.y = 0.0;
    ocolor.r = clamp(color_out.r, 0., 1.);
    ocolor.g = clamp(color_out.g, 0., 1.);
    ocolor.a = new_w;
    
    return OColor(OColor(x=ocolor.x, y=ocolor.y, z=ocolor.z, r=new_r, g=new_v, a=new_w));
}
```

```null
// Code implementation for the PDE solver with Neumann boundary conditions.
void main() {
    vec2 size = textureSize(inTexture, 0);
    vec2 ii = vec2(1., 0.) / size;
    
    float r_prev = texture(inTexture, cc).r;
    float v_prev = texture(inTexture, cc).g;
    float w_prev = texture(inTexture, cc).a;
    
    // Compute Laplacian in x-direction
    vec2 delta_left_x = ii.x * -dt;
    vec2 left_pos_x = clamp(cc + delta_left_x, 0.0, 1.0);
    if (!left_pos_x.y) {
        left_pos_x.y += 1.0; // Neumann boundary adjustment for y
    }
    
    float r_left = texture(inTexture, left_pos_x).r;
    
    vec2 right_pos_x = cc + ii.x * dt;
    if (!right_pos_x.y) {
        right_pos_x.y += 1.0;
    }
    
    float lapx = (texture(inTexture, right_pos_x).r - 2.0f * r_prev + r_left) / ((dx * ii.x)^2);
    
    // Compute Laplacian in y-direction
    vec2 delta_y_left = jj.y * -dt;
    left_pos_y = clamp(cc + delta_y_left, 0.0, 1.0);
    if (!left_pos_y.y) {
        left_pos_y.y += 1.0; // Neumann adjustment for y
    }
    
    float ly = (texture(inTexture, right_pos_x).g - 2.0f * v_prev + texture(inTexture, left_pos_y).g) / ((dy * jj.y)^2);
    
    // Reaction terms and Euler update
    new_r += dt * (D * (lapx + ly) + C_m * r_prev * (1.0f - v_prev));
    new_v += dt * (-D * (lapx + ly) + C_m * v_prev * (1.0f - w_prev));
    new_w += dt * (-D * (lapx + ly) + C_m * w_prev * (1.0f - r_prev));
    
    OColor ocolor;
    ocolor.r = clamp(new_r, 0., 1.);
    return OColor(OColor(x=ocolor.x, y=ocolor.y, z=ocolor.z, r=new_r, g=new_v, a=new_w));
}
```

```null
// Correct code with periodic boundaries using fract for x and clamping for y (simplified)
void main() {
    vec2 size = textureSize(inTexture, 0);
    ii = vec2(1., 0.) / size;
    
    float r_prev = texture(inTexture, cc).r;
    float v_prev = texture(...);

    // Periodic BC in x-direction using fract
    vec2 left_pos_x = cc.x - dt * uniform_dx.x * ii.x;
    if (left_pos_x.y < 0.00000001f) {
        left_pos_x.y += 1.0f;
    } else if (left_pos_x.y > 0.99999999f) {
        left_pos_x.y -= 1.0f;
    }
    
    float r_left = texture(inTexture, clamp(left_pos_x, 0., 1.).xy).r;

    vec2 right_pos_x = cc.x + dt * uniform_dx.x * ii.x;
    if (right_pos_x.y < 0.00000001f) {
        right_pos_x.y += 1.0f;
    } else if (right_pos_x.y > 0.99999999f) {
        right_pos_x.y -= 1.0f;
    }
    
    float lapx = (texture(inTexture, right_pos_x).r - 2.0f * r_prev + r_left) / ((uniform_dx.x * ii.x)^2);
    
    // Neumann BC in y-direction using clamp
    delta_y_left = jj.y * -dt;
    left_pos_y = clamp(cc + delta_y_left, 0., 1.);
    float ly = (texture(inTexture, right_pos_x).g - 2.0f * v_prev + texture(...)).g / ((uniform_dy.y * jj.y)^2);
    
    new_r += dt * (D * lapx + C_m * r_prev * (1.0f - v_prev));
    return OColor(OColor(x=..., y=..., z=..., r=new_r, g=new_v, a=new_w));
}
```

```glsl
// Final code implementation with periodic and Neumann BCs handled as per problem statement.
void main() {
    vec2 size = textureSize(inTexture, 0);
    ii = vec2(1., 0.) / size;
    
    float r_prev = texture(...).r;
    float v_prev = ...g;

    // Periodic boundary in x-direction using fract
    vec2 left_pos_x = cc.x - dt * uniform_dx.x * ii.x;
    if (left_pos_x.y < 0.00000001f) {
        left_pos_x.y += 1.0f;
    } else if (left_pos_x.y > 0.99999999f) {
        left_pos_x.y -= 1.0f;
    }
    float r_left = texture(inTexture, clamp(left_pos_x, 0., 1.).xy).r;

    vec2 right_pos_x = cc.x + dt * uniform_dx.x * ii.x;
    if (right_pos_x.y < 0.00000001f) {
        right_pos_x.y += 1.0f;
    } else if (right_pos_x.y > 0.99999999f) {
        right_pos_x.y -= 1.0f;
    }
    float r_right = texture(inTexture, clamp(right_pos_x, 0., 1.).xy).r;

    // Neumann boundary in y-direction using clamp
    delta_y_left = jj.y * -dt;
    left_pos_y = clamp(cc + delta_y_left, 0., 1.);
    float ly = (texture(..., right_pos_x.xy).g - 2.0f * v_prev + texture(..., left_pos_y.xy).g) / ((uniform_dy.y * jj.y)^2);

    new_r += dt * (D * (r_right - 2.0f * r_prev + r_left)/((uniform_dx.x * ii.x)^2) + D * ly/((uniform_dy.y * jj.y)^2) + C_m * r_prev*(1.0f-v_prev));

    OColor ocolor;
    return OColor(OColor(x=..., y=..., z=..., r=new_r, g=new_v, a=new_w));
}