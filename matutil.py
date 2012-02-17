"""
Decompose rotate&scale only (no shear) 2d matrices
"""
import math

import matrix
from matrix import Matrix

def e_vec(size, dim):
    if dim >= size:
        raise ValueError("Dimension %d is larger than or equal to size %d" % (dim, size))
        
    vec = matrix.column_vector([0 for x in range(size)])
    vec[(dim, 0)] = 1
    
    return vec

def decompose_scale(mat):
    """Decompose the scale factors from a transformation matrix without shear.
    """
    if not mat.is_square():
        raise ValueError("Can't decompose a non-square matrix.")
        
    dims = mat.rows()
    scales = []
    for dim in range(dims):
        vec = e_vec(dims, dim)
        vec_tag = mat * vec
        scale = math.sqrt(vec_tag.transpose().matrix_multiply(vec_tag))
        scales.append(scale)
        
    return scales

def scale_matrix(*scale):
    scale_vec = matrix.row_vector(list(scale))
    scale_mat = matrix.eye(len(scale))
    
    mat = matrix.Matrix(
        [
            [
                (scale[col] if col == row else 0) for
                col in range(len(scale))
            ] for
        row in range(len(scale))
        ]
    )
    
    return mat

def rotation_matrix2(rotation):
    cos = math.cos(rotation)
    sin = math.sin(rotation)
    return matrix.Matrix([
        [cos, -sin],
        [sin, cos]
        ])

def get_rotation_matrix(mat):
    scale = decompose_scale(mat)
    unscale_matrix = scale_matrix(*[1./s for s in scale])
    return mat * unscale_matrix

def get_scale_matrix(mat):
    return scale_matrix(decompose_scale(mat))

def decompose_rotation2(mat):
    """Decompose the rotation angles from a transformation matrix without shear.
    """
    if not mat.is_square():
        raise ValueError("Can't decompose a non-square matrix.")
    
    if not mat.rows() == 2:
        raise ValueError("Matrix is not 2x2")
        
    rotation_mat = get_rotation_matrix(mat)
    return math.atan2(rotation_mat[(1,0)], rotation_mat[(0,0)])

E_X = e_vec(2, 0)
E_Y = e_vec(2, 1)

def main():
    pass
    
if __name__ == "__main__":
    main()