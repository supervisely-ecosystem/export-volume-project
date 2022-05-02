import os

import nrrd
import supervisely_lib as sly
from supervisely_lib.io.fs import mkdir
from supervisely_lib.io.json import load_json_file

from sdk_part.volume_annotation.volume_annotation import VolumeAnnotation


def create_class2idx_map(project_meta):
    return {
        obj_class.name: idx + 1
        for idx, obj_class in enumerate(project_meta.obj_classes)
    }


def get_volume_ann_from_path(project_meta, ann_dir, nrrd_file_name):
    ann_path = os.path.join(ann_dir, f"{nrrd_file_name}.json")
    ann_json = load_json_file(ann_path)
    return VolumeAnnotation.from_json(ann_json, project_meta)


def get_nrrd_header_and_output_files_paths(
    project_meta, dataset_path, nrrd_path, nrrd_file_name, volume_ann
):
    stl_file_dir = os.path.join(dataset_path, "interpolation", nrrd_file_name)
    mkdir(stl_file_dir)

    # ann_path = os.path.join(dataset_path, "ann", f"{nrrd_file_name}.json")
    # ann_json = load_json_file(ann_path)
    # volume_annotation = VolumeAnnotation.from_json(ann_json, project_meta)
    volume_annotation = volume_ann

    output_files_paths = []
    for volume_object in volume_annotation.objects:
        output_file_name = f"{volume_object._key.hex}.nrrd"
        output_file_path = os.path.join(stl_file_dir, output_file_name)
        output_files_paths.append(output_file_path)

    nrrd_header = nrrd.read_header(nrrd_path)
    return nrrd_header, output_files_paths


def convert_to_bitmap(figure):
    obj_class = figure.video_object.obj_class
    new_obj_class = obj_class.clone(geometry_type=sly.Bitmap)
    video_object = figure.video_object
    new_video_object = video_object.clone(obj_class=new_obj_class)
    new_geometry = figure.geometry.convert(sly.Bitmap)[0]
    return figure.clone(video_object=new_video_object, geometry=new_geometry)


def save_nrrd_mask(nrrd_header, curr_obj_mask, output_save_path):
    if not os.path.exists(os.path.dirname(output_save_path)):
        mkdir(os.path.dirname(output_save_path))
    nrrd.write(
        output_save_path,
        curr_obj_mask,
        header={
            "encoding": "gzip",
            "space": nrrd_header["space"],
            "space directions": nrrd_header["space directions"],
            "space origin": nrrd_header["space origin"],
        },
        compression_level=9,
    )
