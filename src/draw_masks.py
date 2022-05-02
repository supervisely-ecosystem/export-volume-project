import os

import numpy as np
import supervisely_lib as sly

import functions as f
import globals as g
import stl_to_nrrd

stl_extension = ".stl"
nrrd_extension = ".nrrd"


def segment_interpolation(
    nrrd_header,
    volume_annotation,
    volume_object,
    key_id_map,
    mask,
    vol_seg_mask_shape,
    nrrd_matrix,
    stl_dir,
):
    volume_object_key = key_id_map.get_object_id(volume_object._key)
    for sp_figure in volume_annotation.spatial_figures:
        figure_vobj_key = key_id_map.get_object_id(sp_figure.video_object._key)
        if figure_vobj_key != volume_object_key:
            continue
        stl_path = os.path.join(stl_dir, f"{sp_figure._key.hex}.stl")
        interpolation_mask = stl_to_nrrd.convert_stl_to_nrrd(
            vol_seg_mask_shape, nrrd_matrix, stl_path
        )

        output_save_path = os.path.join(stl_dir, f"{sp_figure._key.hex}.nrrd")
        if g.convert_surface_to_mask:
            f.save_nrrd_mask(
                nrrd_header, interpolation_mask.astype(np.short), output_save_path
            )
        mask = np.where(interpolation_mask != 0, interpolation_mask, mask)
    return mask


def segment_object(
    nrrd_header,
    nrrd_matrix,
    vol_seg_mask_shape,
    stl_dir,
    volume_annotation,
    volume_object,
    key_id_map,
):
    mask = np.zeros(vol_seg_mask_shape).astype(np.bool)
    mask = segment_interpolation(
        nrrd_header,
        volume_annotation,
        volume_object,
        key_id_map,
        mask,
        vol_seg_mask_shape,
        nrrd_matrix,
        stl_dir,
    )
    mask_2d = segment_2d(
        volume_annotation, volume_object, key_id_map, vol_seg_mask_shape
    )
    mask = np.where(mask_2d != 0, mask_2d, mask)
    return mask


def segment_2d(volume_annotation, volume_object, key_id_map, vol_seg_mask_shape):
    mask = np.zeros(vol_seg_mask_shape).astype(np.bool)
    volume_object_key = key_id_map.get_object_id(volume_object._key)
    for plane in ["sagittal", "coronal", "axial"]:
        for vol_slice in getattr(volume_annotation, plane):
            vol_slice_id = vol_slice.index
            for figure in vol_slice.figures:
                figure_vobj_key = key_id_map.get_object_id(figure.video_object._key)
                if figure_vobj_key != volume_object_key:
                    continue
                if figure.video_object.obj_class.geometry_type != sly.Bitmap:
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
    if plane == "sagittal":
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

    elif plane == "coronal":
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

    elif plane == "axial":
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
