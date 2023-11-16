import numpy as np
import supervisely as sly

import functions as f
import os

import nrrd
import numpy as np
import supervisely as sly
import copy
from uuid import UUID
from supervisely.io.fs import get_file_name_with_ext, file_exists
from supervisely.geometry.mask_3d import Mask3D
from supervisely.geometry.any_geometry import AnyGeometry

import functions as f
import globals as g


def segment_object(
    vol_seg_mask_shape,
    volume_annotation,
    volume_object,
    key_id_map,
):
    mask = np.zeros(vol_seg_mask_shape).astype(np.bool)
    mask_2d = segment_2d(volume_annotation, volume_object, key_id_map, vol_seg_mask_shape)
    mask = np.where(mask_2d != 0, mask_2d, mask)
    return mask


def segment_2d(volume_annotation, volume_object, key_id_map, vol_seg_mask_shape):
    mask = np.zeros(vol_seg_mask_shape).astype(np.bool)
    volume_object_key = key_id_map.get_object_id(volume_object._key)
    for plane in ["plane_sagittal", "plane_coronal", "plane_axial"]:
        for vol_slice in getattr(volume_annotation, plane):
            vol_slice_id = vol_slice.index
            for figure in vol_slice.figures:
                figure_vobj_key = key_id_map.get_object_id(figure.volume_object._key)
                if figure_vobj_key != volume_object_key:
                    continue
                if figure.volume_object.obj_class.geometry_type != sly.Bitmap:
                    figure = f.convert_to_bitmap(figure)
                try:
                    slice_geometry = figure.geometry
                    slice_bitmap = slice_geometry.data.astype(mask.dtype)
                    bitmap_origin = slice_geometry.origin

                    slice_bitmap = np.fliplr(slice_bitmap)
                    slice_bitmap = np.rot90(slice_bitmap, 1)

                    mask = draw_figure_on_slice(
                        mask, plane, vol_slice_id, slice_bitmap, bitmap_origin
                    )
                except Exception as e:
                    sly.logger.warn(
                        f"Skipped {plane} slice: {vol_slice_id} due to error: '{e}'",
                        extra={
                            "object_id": volume_object_key,
                            "figure_id": figure_vobj_key,
                        },
                    )
                    continue
    return mask


def draw_figure_on_slice(mask, plane, vol_slice_id, slice_bitmap, bitmap_origin):
    if plane == "plane_sagittal":
        cur_bitmap = mask[
            vol_slice_id,
            bitmap_origin.col : bitmap_origin.col + slice_bitmap.shape[0],
            bitmap_origin.row : bitmap_origin.row + slice_bitmap.shape[1],
        ]
        cur_bitmap = np.where(slice_bitmap != 0, slice_bitmap, cur_bitmap)
        mask[
            vol_slice_id,
            bitmap_origin.col : bitmap_origin.col + slice_bitmap.shape[0],
            bitmap_origin.row : bitmap_origin.row + slice_bitmap.shape[1],
        ] = cur_bitmap

    elif plane == "plane_coronal":
        cur_bitmap = mask[
            bitmap_origin.col : bitmap_origin.col + slice_bitmap.shape[0],
            vol_slice_id,
            bitmap_origin.row : bitmap_origin.row + slice_bitmap.shape[1],
        ]
        cur_bitmap = np.where(slice_bitmap != 0, slice_bitmap, cur_bitmap)
        mask[
            bitmap_origin.col : bitmap_origin.col + slice_bitmap.shape[0],
            vol_slice_id,
            bitmap_origin.row : bitmap_origin.row + slice_bitmap.shape[1],
        ] = cur_bitmap

    elif plane == "plane_axial":
        cur_bitmap = mask[
            bitmap_origin.col : bitmap_origin.col + slice_bitmap.shape[0],
            bitmap_origin.row : bitmap_origin.row + slice_bitmap.shape[1],
            vol_slice_id,
        ]
        cur_bitmap = np.where(slice_bitmap != 0, slice_bitmap, cur_bitmap)
        mask[
            bitmap_origin.col : bitmap_origin.col + slice_bitmap.shape[0],
            bitmap_origin.row : bitmap_origin.row + slice_bitmap.shape[1],
            vol_slice_id,
        ] = cur_bitmap

    return mask


def merge_masks(masks):
    mask = masks.pop(0)
    while masks:
        mask_add = masks.pop(0)
        mask = np.where(mask_add != 0, mask_add, mask)
    return mask


def get_sp_figure_mask(
    volume_object_key: UUID,
    volume_annotation_cp: sly.VolumeAnnotation,
    mask_dir: str,
    nrrd_file_name: str,
):
    masks = []
    for sp_figure in volume_annotation_cp.spatial_figures:
        if sp_figure.volume_object.key() == volume_object_key:
            mask3d_path = os.path.join(mask_dir, nrrd_file_name, sp_figure.key().hex + ".nrrd")
            if file_exists(mask3d_path):
                # for the new storage format
                mask_data, _ = nrrd.read(mask3d_path)
                # to reset greyscale values
                mask_data = (mask_data != 0).astype(bool)
                mask_data = mask_data.astype(np.int16)
                masks.append(mask_data)
            else:
                # for the old storage format
                masks.append(sp_figure.geometry.data)
    return masks


def convert_all(dir_path, project_meta, key_id_map: sly.KeyIdMap):
    datasets_paths = [
        os.path.join(dir_path, ds)
        for ds in os.listdir(dir_path)
        if os.path.isdir(os.path.join(dir_path, ds))
    ]
    for dataset_path in datasets_paths:
        volumes_dir = os.path.join(dataset_path, "volume")
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

            volume_annotation = f.get_volume_ann_from_path(project_meta, ann_dir, nrrd_file_name)

            vol_seg_mask = None
            if g.save_semantic_segmentation:
                vol_seg_mask = np.zeros(nrrd_header["sizes"]).astype(np.short)
            for v_object in volume_annotation.objects:
                output_file_name = f"{v_object.key().hex}.nrrd"
                output_save_path = os.path.join(mask_dir, nrrd_file_name, output_file_name)

                v_object_id = g.class2idx[v_object.obj_class.name]

                save_nrrd_status = (
                    True  # to prevent NRRD duplicates from being stored for Mask3D objects
                )

                if v_object.obj_class.geometry_type == Mask3D:
                    save_nrrd_status = False  # already have this file in mask dir
                    masks = get_sp_figure_mask(
                        v_object.key(),
                        volume_annotation,
                        mask_dir,
                        nrrd_file_name,
                    )
                    if len(masks) > 1:
                        curr_obj_mask = merge_masks(masks)
                    if len(masks) == 1:
                        curr_obj_mask = masks[0]
                    if len(masks) == 0:
                        continue

                elif v_object.obj_class.geometry_type == AnyGeometry:
                    volume_annotation_cp = copy.deepcopy(volume_annotation)
                    masks = get_sp_figure_mask(
                        v_object.key(),
                        volume_annotation_cp,
                        mask_dir,
                        nrrd_file_name,
                    )
                    if len(masks) > 1:
                        mask3d_obj_mask = merge_masks(masks)
                    if len(masks) == 1:
                        mask3d_obj_mask = masks[0]
                    if len(masks) == 0:
                        mask3d_obj_mask = 0

                    volume_annotation_cp.spatial_figures.clear()

                    other_obj_mask = segment_object(
                        nrrd_header["sizes"],
                        volume_annotation_cp,
                        v_object,
                        key_id_map,
                    )

                    curr_obj_mask = merge_masks([mask3d_obj_mask, other_obj_mask])

                else:
                    curr_obj_mask = segment_object(
                        nrrd_header["sizes"],
                        volume_annotation,
                        v_object,
                        key_id_map,
                    )

                # change grayscale values for each object to have visual differences on the common mask
                # for backward compatibility in Import Volumes with Masks
                curr_obj_mask = curr_obj_mask.astype(np.short) * v_object_id

                if g.save_instance_segmentation:
                    if save_nrrd_status is True:
                        f.save_nrrd_mask(nrrd_header, curr_obj_mask, output_save_path)
                        v_object_name = v_object.obj_class.name
                        f.save_nrrd_mask_readable_name(
                            nrrd_header, curr_obj_mask, output_save_path, v_object_name
                        )

                if vol_seg_mask is not None:
                    vol_seg_mask = np.where(curr_obj_mask != 0, curr_obj_mask, vol_seg_mask)

            if vol_seg_mask is not None:
                output_file_name = "semantic_segmentation.nrrd"
                output_save_path = os.path.join(mask_dir, nrrd_file_name, output_file_name)
                f.save_nrrd_mask(nrrd_header, vol_seg_mask, output_save_path)
