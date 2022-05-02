import globals as g
import os
import math
import nrrd
import trimesh
import numpy as np
import supervisely_lib as sly
from supervisely_lib.io.fs import get_file_name_with_ext, mkdir, get_file_name
from supervisely_lib.io.json import load_json_file
# from supervisely_lib.video_annotation.key_id_map import KeyIdMap
from sdk_part.volume_annotation.volume_annotation import VolumeAnnotation

stl_extension = '.stl'
nrrd_extension = '.nrrd'


def fill_class2idx_map(project_meta):
    return {
        obj_class.name: idx + 1
        for idx, obj_class in enumerate(project_meta.obj_classes)
    }


def get_nrrd_header_and_output_files_paths(project_meta, dataset_path, nrrd_path, nrrd_file_name):
    stl_file_dir = os.path.join(dataset_path, "interpolation", nrrd_file_name)
    mkdir(stl_file_dir)

    ann_path = os.path.join(dataset_path, "ann", f"{nrrd_file_name}.json")
    ann_json = load_json_file(ann_path)

    output_files_paths = []
    volume_annotation = VolumeAnnotation.from_json(ann_json, project_meta)
    for volume_object in volume_annotation.objects:
        output_file_name = f"{volume_object._key.hex}.nrrd"
        output_file_path = os.path.join(stl_file_dir, output_file_name)
        output_files_paths.append(output_file_path)

    nrrd_header = nrrd.read_header(nrrd_path)
    return nrrd_header, output_files_paths


def convert_all(dir_path, project_meta, key_id_map):
    datasets_paths = [os.path.join(dir_path, ds) for ds in os.listdir(dir_path) if
                      os.path.isdir(os.path.join(dir_path, ds))]
    for dataset_path in datasets_paths:
        volumes_dir = os.path.join(dataset_path, "volume")
        interpolation_dir = os.path.join(dataset_path, "interpolation")
        ann_dir = os.path.join(dataset_path, "ann")

        nrrd_paths = [os.path.join(volumes_dir, nrrd_file) for nrrd_file in os.listdir(volumes_dir)
                      if os.path.isfile(os.path.join(volumes_dir, nrrd_file))]

        for nrrd_path in nrrd_paths:
            nrrd_file_name = get_file_name_with_ext(nrrd_path)
            stl_dir = os.path.join(interpolation_dir, nrrd_file_name)
            if os.path.exists(stl_dir) and os.path.isdir(stl_dir):
                stl_paths = [os.path.join(stl_dir, stl_file) for stl_file in os.listdir(stl_dir)
                             if os.path.isfile(os.path.join(stl_dir, stl_file))]
                stl_masks = []
                for stl_path in stl_paths:
                    stl_name = get_file_name(stl_path)
                    output_file_path = stl_path.replace(stl_extension, nrrd_extension)
                    mask = convert_stl_to_nrrd(nrrd_path, stl_path, output_file_path)
                    stl_masks.append(mask)
                    if g.draw_flat_figures:
                        draw_object_mask(project_meta, key_id_map, ann_dir, nrrd_path, output_file_path, orig_mask=mask)
                if g.draw_objects_as_single_mask:
                    merge_single_mask(project_meta, ann_dir, nrrd_path, interpolation_dir, stl_masks=stl_masks)

            else:
                nrrd_header, output_files_paths = get_nrrd_header_and_output_files_paths(project_meta,
                                                                                         dataset_path,
                                                                                         nrrd_path, nrrd_file_name)
                for output_file_path in output_files_paths:
                    generate_empty_nrrd_mask(nrrd_header, output_file_path)
                if g.draw_flat_figures:
                    draw_object_mask(project_meta, key_id_map, ann_dir, nrrd_path, interpolation_dir, orig_mask=None)
                if g.draw_objects_as_single_mask:
                    draw_single_mask(project_meta, key_id_map, ann_dir, nrrd_path, interpolation_dir, mask=None)


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


def generate_empty_nrrd_mask(nrrd_header, output_file_path):
    mask = np.zeros(nrrd_header['sizes']).astype(np.short)
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

    try:
        voxel = mesh.voxelized(pitch=1.0)
    except Exception as e:
        sly.logger.error(e)
        sly.logger.warning(
            "Couldn't voxelize file {!r}, empty mask will be generated".format(get_file_name_with_ext(stl_path)),
            extra={'file_path': stl_path})
        generate_empty_nrrd_mask(nrrd_header, output_file_path)
        return

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
    return mask


def convert_to_bitmap(figure):
    obj_class = figure.video_object.obj_class
    new_obj_class = obj_class.clone(geometry_type=sly.Bitmap)
    video_object = figure.video_object
    new_video_object = video_object.clone(obj_class=new_obj_class)
    new_geometry = figure.geometry.convert(sly.Bitmap)[0]
    return figure.clone(video_object=new_video_object, geometry=new_geometry)


def draw_figure_on_slice(mask, plane, vol_slice_id, slice_bitmap, bitmap_origin):
    if plane == 'sagittal':
        cur_bitmap = mask[
                     vol_slice_id,
                     bitmap_origin.col:bitmap_origin.col + slice_bitmap.shape[0],
                     bitmap_origin.row:bitmap_origin.row + slice_bitmap.shape[1],
                     ]
        cur_bitmap = np.where(slice_bitmap != 0, slice_bitmap, cur_bitmap)
        mask[
        vol_slice_id,
        bitmap_origin.col:bitmap_origin.col + slice_bitmap.shape[0],
        bitmap_origin.row:bitmap_origin.row + slice_bitmap.shape[1],
        ] = cur_bitmap

    elif plane == 'coronal':
        cur_bitmap = mask[
                     bitmap_origin.col:bitmap_origin.col + slice_bitmap.shape[0],
                     vol_slice_id,
                     bitmap_origin.row:bitmap_origin.row + slice_bitmap.shape[1],
                     ]
        cur_bitmap = np.where(slice_bitmap != 0, slice_bitmap, cur_bitmap)
        mask[
        bitmap_origin.col:bitmap_origin.col + slice_bitmap.shape[0],
        vol_slice_id,
        bitmap_origin.row:bitmap_origin.row + slice_bitmap.shape[1],
        ] = cur_bitmap

    elif plane == 'axial':
        cur_bitmap = mask[
                     bitmap_origin.col:bitmap_origin.col + slice_bitmap.shape[0],
                     bitmap_origin.row:bitmap_origin.row + slice_bitmap.shape[1],
                     vol_slice_id,
                     ]
        cur_bitmap = np.where(slice_bitmap != 0, slice_bitmap, cur_bitmap)
        mask[
        bitmap_origin.col:bitmap_origin.col + slice_bitmap.shape[0],
        bitmap_origin.row:bitmap_origin.row + slice_bitmap.shape[1],
        vol_slice_id,
        ] = cur_bitmap

    return mask


def draw_object_mask(project_meta, key_id_map, ann_dir, nrrd_path, orig_output_file_path, orig_mask=None):
    nrrd_header = nrrd.read_header(nrrd_path)
    nrrd_mask_file_name = get_file_name_with_ext(nrrd_path)
    ann_path = os.path.join(ann_dir, f"{nrrd_mask_file_name}.json")
    ann_json = load_json_file(ann_path)
    volume_annotation = VolumeAnnotation.from_json(ann_json, project_meta)

    for volume_object in volume_annotation.objects:
        mask = orig_mask
        output_file_path = orig_output_file_path

        if mask is None:
            mask = np.zeros(nrrd_header['sizes']).astype(np.short)
            output_file_name = f"{volume_object._key.hex}.nrrd"
            output_file_path = os.path.join(orig_output_file_path, nrrd_mask_file_name, output_file_name)

        volume_object_key = key_id_map.get_object_id(volume_object._key)
        for plane in ['sagittal', 'coronal', 'axial']:
            for vol_slice in getattr(volume_annotation, plane):
                vol_slice_id = vol_slice.index
                for figure in vol_slice.figures:
                    figure_vobj_key = key_id_map.get_object_id(figure.video_object._key)
                    if figure_vobj_key != volume_object_key: continue
                    if figure.video_object.obj_class.geometry_type != sly.Bitmap:
                        figure = convert_to_bitmap(figure)
                    try:
                        slice_geometry = figure.geometry
                        slice_bitmap = slice_geometry.data.astype(mask.dtype)
                        bitmap_origin = slice_geometry.origin

                        slice_bitmap = np.fliplr(slice_bitmap)
                        slice_bitmap = np.rot90(slice_bitmap, 1)

                        mask = draw_figure_on_slice(mask, plane, vol_slice_id, slice_bitmap, bitmap_origin)
                    except Exception as e:
                        sly.logger.warn(
                            f"Skipped {plane} slice: {vol_slice_id} in {nrrd_mask_file_name} due to error: '{e}'")
                        continue

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


def draw_single_mask(project_meta, key_id_map, ann_dir, nrrd_path, orig_output_file_path, mask=None):
    nrrd_header = nrrd.read_header(nrrd_path)
    nrrd_mask_file_name = get_file_name_with_ext(nrrd_path)
    ann_path = os.path.join(ann_dir, f"{nrrd_mask_file_name}.json")
    ann_json = load_json_file(ann_path)
    volume_annotation = VolumeAnnotation.from_json(ann_json, project_meta)

    if mask is None:
        mask = np.zeros(nrrd_header['sizes']).astype(np.short)
        output_file_name = f"{volume_annotation._key.hex}_single_mask.nrrd"
        output_file_path = os.path.join(orig_output_file_path, nrrd_mask_file_name, output_file_name)
    else:
        mask = np.zeros(nrrd_header['sizes']).astype(np.short)
        output_file_name = f"{volume_annotation._key.hex}_single_mask.nrrd"
        output_file_path = os.path.join(os.path.dirname(orig_output_file_path), output_file_name)

    for volume_object in volume_annotation.objects:
        mask = mask
        volume_object_key = key_id_map.get_object_id(volume_object._key)
        for plane in ['sagittal', 'coronal', 'axial']:
            for vol_slice in getattr(volume_annotation, plane):
                vol_slice_id = vol_slice.index
                for figure in vol_slice.figures:
                    figure_vobj_key = key_id_map.get_object_id(figure.video_object._key)
                    if figure_vobj_key != volume_object_key:
                        continue
                    if figure.video_object.obj_class.geometry_type != sly.Bitmap:
                        figure = convert_to_bitmap(figure)
                    try:
                        slice_geometry = figure.geometry
                        slice_bitmap = slice_geometry.data.astype(mask.dtype)
                        bitmap_origin = slice_geometry.origin

                        slice_bitmap = np.fliplr(slice_bitmap)
                        slice_bitmap = np.rot90(slice_bitmap, 1)

                        mask = draw_figure_on_slice(mask, plane, vol_slice_id, slice_bitmap, bitmap_origin)
                    except Exception as e:
                        sly.logger.warn(
                            f"Skipped {plane} slice: {vol_slice_id} in {nrrd_mask_file_name} due to error: '{e}'")
                        continue

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


def merge_single_mask(project_meta, ann_dir, nrrd_path, interpolation_dir, stl_masks):
    nrrd_header = nrrd.read_header(nrrd_path)
    nrrd_mask_file_name = get_file_name_with_ext(nrrd_path)
    ann_path = os.path.join(ann_dir, f"{nrrd_mask_file_name}.json")
    ann_json = load_json_file(ann_path)
    volume_annotation = VolumeAnnotation.from_json(ann_json, project_meta)

    output_file_name = f"{volume_annotation._key.hex}_single_mask.nrrd"
    output_file_path = os.path.join(interpolation_dir, nrrd_mask_file_name, output_file_name)

    mask = np.array([(ai*1) + (bi*2) + (ci*3) for ai, bi, ci in zip(stl_masks[0], stl_masks[1], stl_masks[2])])

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
