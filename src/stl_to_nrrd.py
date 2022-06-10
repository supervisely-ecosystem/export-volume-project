import math
import os

import nrrd
import numpy as np
import supervisely as sly
import trimesh
from supervisely.io.fs import get_file_name, get_file_name_with_ext

import draw_masks
import functions as f
import globals as g


def convert_all(dir_path, project_meta, key_id_map):
    datasets_paths = [
        os.path.join(dir_path, ds)
        for ds in os.listdir(dir_path)
        if os.path.isdir(os.path.join(dir_path, ds))
    ]
    for dataset_path in datasets_paths:
        volumes_dir = os.path.join(dataset_path, "volume")
        interpolation_dir = os.path.join(dataset_path, "interpolation")
        ann_dir = os.path.join(dataset_path, "ann")
        mask_dir = os.path.join(dataset_path, "mask")

        nrrd_paths = [
            os.path.join(volumes_dir, nrrd_file)
            for nrrd_file in os.listdir(volumes_dir)
            if os.path.isfile(os.path.join(volumes_dir, nrrd_file))
        ]
        for nrrd_path in nrrd_paths:
            nrrd_file_name = get_file_name_with_ext(nrrd_path)
            nrrd_header = nrrd.read_header(nrrd_path)
            nrrd_matrix = matrix_from_nrrd_header(nrrd_header)

            volume_annotation = f.get_volume_ann_from_path(
                project_meta, ann_dir, nrrd_file_name
            )

            vol_seg_mask = None
            if g.save_semantic_segmentation:
                vol_seg_mask = np.zeros(nrrd_header["sizes"]).astype(np.short)
            for v_object in volume_annotation.objects:
                output_file_name = f"{v_object._key.hex}.nrrd"
                output_save_path = os.path.join(
                    mask_dir, nrrd_file_name, output_file_name
                )

                v_object_id = g.class2idx[v_object.obj_class.name]
                stl_path = os.path.join(interpolation_dir, nrrd_file_name)
                curr_obj_mask = draw_masks.segment_object(
                    nrrd_header,
                    nrrd_matrix,
                    nrrd_header["sizes"],
                    stl_path,
                    mask_dir,
                    volume_annotation,
                    v_object,
                    key_id_map,
                )
                if g.save_instance_segmentation:
                    f.save_nrrd_mask(
                        nrrd_header, curr_obj_mask.astype(np.short), output_save_path
                    )
                else:
                    f.save_nrrd_mask(
                        nrrd_header,
                        np.zeros(nrrd_header["sizes"]).astype(np.short),
                        output_save_path,
                    )
                if vol_seg_mask is not None:
                    curr_obj_mask = curr_obj_mask.astype(np.short) * v_object_id
                    vol_seg_mask = np.where(
                        curr_obj_mask != 0, curr_obj_mask, vol_seg_mask
                    )

            if vol_seg_mask is not None:
                output_file_name = "semantic_segmentation.nrrd"
                output_save_path = os.path.join(
                    mask_dir, nrrd_file_name, output_file_name
                )
                f.save_nrrd_mask(nrrd_header, vol_seg_mask, output_save_path)


def matrix_from_nrrd_header(header):
    try:
        space_directions = header["space directions"]
        space_origin = header["space origin"]
    except KeyError as e:
        raise IOError(
            'Need the header\'s "{}" field to determine the mapping from voxels to world coordinates.'.format(
                e
            )
        )

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


def convert_stl_to_nrrd(mask_shape, voxel_to_world, stl_path):
    world_to_voxel = np.linalg.inv(voxel_to_world)

    mesh = trimesh.load(stl_path)

    min_vec = [float("inf"), float("inf"), float("inf")]
    max_vec = [float("-inf"), float("-inf"), float("-inf")]

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

    try:
        voxel = mesh.voxelized(pitch=1.0)
    except Exception as e:
        sly.logger.error(e)
        sly.logger.warning(
            "Couldn't voxelize file {!r}".format(get_file_name_with_ext(stl_path)),
            extra={"file_path": stl_path},
        )
        return np.zeros(mask_shape).astype(np.bool)

    voxel = voxel.fill()
    mask = voxel.matrix.astype(np.bool)
    padded_mask = np.zeros(mask_shape).astype(np.bool)

    # find dimension coords
    start = [
        math.ceil(center_v - shape_v / 2)
        for center_v, shape_v in zip(center, mask.shape)
    ]
    end = [
        math.ceil(center_v + shape_v / 2)
        for center_v, shape_v in zip(center, mask.shape)
    ]

    # find intersections
    vol_inter_max = [max(start[0], 0), max(start[1], 0), max(start[2], 0)]
    vol_inter_min = [
        min(end[0], mask_shape[0]),
        min(end[1], mask_shape[1]),
        min(end[2], mask_shape[2]),
    ]

    padded_mask[
        vol_inter_max[0] : vol_inter_min[0],
        vol_inter_max[1] : vol_inter_min[1],
        vol_inter_max[2] : vol_inter_min[2],
    ] = mask[
        vol_inter_max[0] - start[0] : vol_inter_min[0] - start[0],
        vol_inter_max[1] - start[1] : vol_inter_min[1] - start[1],
        vol_inter_max[2] - start[2] : vol_inter_min[2] - start[2],
    ]

    return padded_mask
