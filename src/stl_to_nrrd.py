import os
import math
import nrrd
import trimesh
import numpy as np
from supervisely_lib.io.fs import get_file_name_with_ext


stl_extension = '.stl'
nrrd_extension = '.nrrd'


def convert_all(dir_path):
    datasets_paths = [os.path.join(dir_path, ds) for ds in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, ds))]
    for dataset_path in datasets_paths:
        volumes_dir = os.path.join(dataset_path, "volume")
        interpolation_dir = os.path.join(dataset_path, "interpolation")

        nrrd_paths = [os.path.join(volumes_dir, nrrd_file) for nrrd_file in os.listdir(volumes_dir)
                      if os.path.isfile(os.path.join(volumes_dir, nrrd_file))]
        for nnrd_path in nrrd_paths:
            nnrd_file_name = get_file_name_with_ext(nnrd_path)

            stl_dir = os.path.join(interpolation_dir, nnrd_file_name)
            if os.path.exists(stl_dir) and os.path.isdir(stl_dir):
                stl_paths = [os.path.join(stl_dir, stl_file) for stl_file in os.listdir(stl_dir)
                             if os.path.isfile(os.path.join(stl_dir, stl_file))]
                for stl_path in stl_paths:
                    output_file_path = stl_path.replace(stl_extension, nrrd_extension)
                    convert_stl_to_nrrd(nnrd_path, stl_path, output_file_path)


def matrix_from_nrrd_header(header):
    try:
        space_directions = header["space directions"]
        space_origin = header["space origin"]
    except KeyError as e:
        raise IOError(
            "Need the header's \"{}\" field to determine the mapping from voxels to world coordinates.".format(e))

    # "... the space directions field gives, one column at a time, the mapping from image space to world space
    # coordinates ... [1]_" -> list of columns, needs to be transposed
    trans_3x3 = np.array(space_directions).T
    trans_4x4 = np.eye(4)
    trans_4x4[:3, :3] = trans_3x3
    trans_4x4[:3, 3] = space_origin

    return trans_4x4


def vec3_mat4(vec, mat):
    v = mat @ [*vec, 1]

    return (v / v[3])[:-1]


def clamp_val(val, min_val, max_val):
    return max(min(val, min_val), max_val)


def convert_stl_to_nrrd(nrrd_path, stl_path, output_file_path):
    nrrd_header = nrrd.read_header(nrrd_path)

    voxel_to_world = matrix_from_nrrd_header(nrrd_header)
    world_to_voxel = np.linalg.inv(voxel_to_world)

    mesh = trimesh.load(stl_path)

    min_vec = [float('inf'), float('inf'), float('inf')]
    max_vec = [float('-inf'), float('-inf'), float('-inf')]

    mesh.apply_scale((-1, -1, 1))  # LPS to RAS
    mesh.apply_transform(world_to_voxel)

    for vert in mesh.vertices:
        min_vec[0] = min(min_vec[0], vert[0])
        min_vec[1] = min(min_vec[1], vert[1])
        min_vec[2] = min(min_vec[2], vert[2])

        max_vec[0] = max(max_vec[0], vert[0])
        max_vec[1] = max(max_vec[1], vert[1])
        max_vec[2] = max(max_vec[2], vert[2])

    center = [(min_v + max_v) / 2 for min_v, max_v in zip(min_vec, max_vec)]

    voxel = mesh.voxelized(pitch=1.0)
    voxel = voxel.fill()

    mask = voxel.matrix.astype(np.short)

    vol_shape = nrrd_header['sizes']
    padded_mask = np.zeros(vol_shape).astype(np.short)

    # find dimension coords
    start = [math.ceil(center_v - shape_v / 2) for center_v, shape_v in zip(center, mask.shape)]
    end = [math.ceil(center_v + shape_v / 2) for center_v, shape_v in zip(center, mask.shape)]

    # find intersections
    vol_inter_max = [max(start[0], 0), max(start[1], 0), max(start[2], 0)]
    vol_inter_min = [min(end[0], vol_shape[0]), min(end[1], vol_shape[1]), min(end[2], vol_shape[2])]

    padded_mask[
    vol_inter_max[0]:vol_inter_min[0],
    vol_inter_max[1]:vol_inter_min[1],
    vol_inter_max[2]:vol_inter_min[2],
    ] = mask[
        vol_inter_max[0] - start[0]:vol_inter_min[0] - start[0],
        vol_inter_max[1] - start[1]:vol_inter_min[1] - start[1],
        vol_inter_max[2] - start[2]:vol_inter_min[2] - start[2],
        ]

    mask = padded_mask

    # print('nrrd_header', nrrd_header)

    nrrd.write(
        output_file_path,
        mask,
        header={
            "encoding": 'gzip',
            "space": nrrd_header['space'],
            "space directions": nrrd_header['space directions'],
            "space origin": nrrd_header['space origin'],
        },
        compression_level=9
    )
