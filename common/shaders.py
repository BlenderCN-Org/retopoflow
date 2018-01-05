import bgl
from ..lib.common_utilities import invert_matrix, matrix_normal, dprint
from ..lib.common_shader import Shader

# useful resources
# - http://antongerdelan.net/opengl/shaders.html
# - http://antongerdelan.net/opengl/vertexbuffers.html

# note: not all supported by user system, but we don't need latest functionality
# https://github.com/mattdesl/lwjgl-basics/wiki/GLSL-Versions
# OpenGL  GLSL    OpenGL  GLSL
#  2.0    110      2.1    120
#  3.0    130      3.1    140
#  3.2    150      3.3    330
#  4.0    400      4.1    410
#  4.2    420      4.3    430
dprint('GLSL Version: ' + bgl.glGetString(bgl.GL_SHADING_LANGUAGE_VERSION))


edgeShortenShader = Shader('''
    #version 130
    
    uniform vec2 uScreenSize;
    
    in vec4  vPos;
    in vec4  vFrom;
    in vec4  vColor;
    in float vRadius;
    
    out vec4 aColor;
    
    void main() {
        vec4 p0 = gl_ModelViewProjectionMatrix * vPos;
        vec4 p1 = gl_ModelViewProjectionMatrix * vFrom;
        
        vec2 s0 = uScreenSize * p0.xy / p0.w;
        vec2 s1 = uScreenSize * p1.xy / p1.w;
        vec2 d = normalize(s1 - s0);
        vec2 s2 = s0 + d * vRadius;
        
        gl_Position = vec4(s2 / uScreenSize * p0.w, p0.z, p0.w);
        aColor = vColor;
    }
    ''', '''
    #version 130
    
    in vec4 aColor;
    
    void main() {
        gl_FragColor = aColor;
    }
    ''', checkErrors=False)


circleShader = Shader('''
    #version 130
    
    in vec4 vPos;
    in vec4 vInColor;
    in vec4 vOutColor;
    
    out vec4 aInColor;
    out vec4 aOutColor;
    
    void main() {
        gl_Position = gl_ModelViewProjectionMatrix * vPos;
        aInColor    = vInColor;
        aOutColor   = vOutColor;
    }
    ''', '''
    #version 130
    
    in vec4 aInColor;
    in vec4 aOutColor;
    
    uniform float uInOut;
    
    void main() {
        float d = 2.0 * distance(gl_PointCoord, vec2(0.5, 0.5));
        if(d > 1.0) discard;
        gl_FragColor = (d > uInOut) ? aOutColor : aInColor;
    }
    ''', checkErrors=False)


arrowShader = Shader('''
    #version 130

    in vec4 vPos;
    in vec4 vFrom;
    in vec4 vInColor;
    in vec4 vOutColor;

    out float aRot;
    out vec4 aInColor;
    out vec4 aOutColor;

    float angle(vec2 d) { return atan(d.y, d.x); }

    void main() {
        vec4 p0 = gl_ModelViewProjectionMatrix * vFrom;
        vec4 p1 = gl_ModelViewProjectionMatrix * vPos;
        gl_Position = p1;
        aRot = angle((p1.xy / p1.w) - (p0.xy / p0.w));
        aInColor = vInColor;
        aOutColor = vOutColor;
    }
    ''', '''
    #version 130

    in float aRot;
    in vec4 aInColor;
    in vec4 aOutColor;

    uniform float uInOut;

    float alpha(vec2 dir) {
        vec2 d0 = dir - vec2(1,1);
        vec2 d1 = dir - vec2(1,-1);
        
        float d0v = -d0.x/2.0 - d0.y;
        float d1v = -d1.x/2.0 + d1.y;
        float dv0 = length(dir);
        float dv1 = distance(dir, vec2(-2,0));
        
        if(d0v < 1.0 || d1v < 1.0) return -1.0;
        // if(dv0 > 1.0) return -1.0;
        if(dv1 < 1.3) return -1.0;
        
        if(d0v - 1.0 < (1.0 - uInOut) || d1v - 1.0 < (1.0 - uInOut)) return 0.0;
        //if(dv0 > uInOut) return 0.0;
        if(dv1 - 1.3 < (1.0 - uInOut)) return 0.0;
        return 1.0;
    }

    void main() {
        vec2 d = 2.0 * (gl_PointCoord - vec2(0.5, 0.5));
        vec2 dr = vec2(cos(aRot)*d.x - sin(aRot)*d.y, sin(aRot)*d.x + cos(aRot)*d.y);
        float a = alpha(dr);
        if(a < 0.0) discard;
        gl_FragColor = mix(aOutColor, aInColor, a);
    }
    ''', checkErrors=False)

