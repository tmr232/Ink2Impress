"""
Decompose rotate&scale only (no shear) 2d matrices
"""
import math

def matmul2(m1, m2):
    return [
        [
            m1[0][0] * m2[0][0] + m1[0][1] * m2[1][0],
            m1[0][0] * m2[0][1] + m1[0][1] * m2[1][1]
        ],
        [
            m1[1][0] * m2[0][0] + m1[1][1] * m2[1][0],
            m1[1][0] * m2[0][1] + m1[1][1] * m2[1][1]
        ]
    ]
    
def rotmat2(r):
    cos = math.cos(r)
    sin = math.sin(r)
    return [[cos, -sin],
            [sin, cos]]
    
def scalemat2(x, y=None):
    if y is None:
        y = x
        
    return [[x, 0],
            [0, y]]
    
def mat2(m11,m12,m21,m22):
    return [[m11,m12],
            [m21,m22]]
    
def det2(m):
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]

def mag2(v):
    return math.sqrt(v[0]**2 + v[1]**2)

def dist2(v1, v2):
    return mag2([v1[0] - v2[0], v1[1] - v2[1]])
    
def eye2():
    return mat2(1,0,0,1)
    
def matvec2(m, v):
    return [
        v[0] * m[0][0] + v[1] * m[0][1],
        v[0] * m[1][0] + v[1] * m[1][1]
    ]
    
def vec2(x, y):
    return [x, y]
    
def ex2():
    return vec2(1, 0)
    
def ey2():
    return vec2(0, 1)
    
def decomp_scale2(m):
    vx = matvec2(m, ex2())
    vy = matvec2(m, ey2())
    
    sx = mag2(vx)
    sy = mag2(vy)
    
    return sx, sy

def unscale2(m):
    sx, sy = decomp_scale2(m)
    us = scalemat2(1./sx, 1./sy)
    return matmul2(m, us)
    
getrotmat2 = unscale2
    
def decomp_rot2(m):
    rm = unscale2(m)
    return math.atan2(m[1][0], m[0][0])
    
def unrot2(m):
    sx, sy = decomp_scale2(m)
    return scalemat2(sx, sy)
    
getscalemat2 = unrot2


def main():
    import pprint    
    s = scalemat2(2,3)
    r = rotmat2(math.radians(30))
    
    t = matmul2(r, s)
    
    ex = vec2(1, 0)
    ey = vec2(0, 1)
    
    nx = matvec2(t, ex)
    ny = matvec2(t, ey)
    
    pprint.pprint(s)
    pprint.pprint(r)
    pprint.pprint(t)
    pprint.pprint(unscale2(t))
    print math.degrees(decomp_rot2(t))
    
if __name__ == "__main__":
    main()