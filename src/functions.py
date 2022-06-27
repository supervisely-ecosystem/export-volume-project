import os

import nrrd
import supervisely as sly
from supervisely.io.fs import mkdir
from supervisely.io.json import load_json_file
from supervisely.volume_annotation.volume_annotation import VolumeAnnotation


def create_class2idx_map(project_meta):
    return {
        obj_class.name: idx + 1
        for idx, obj_class in enumerate(project_meta.obj_classes)
    }


def get_volume_ann_from_path(project_meta, ann_dir, nrrd_file_name):
    ann_path = os.path.join(ann_dir, f"{nrrd_file_name}.json")
    ann_json = load_json_file(ann_path)
    return VolumeAnnotation.from_json(ann_json, project_meta)


def convert_to_bitmap(figure):
    obj_class = figure.volume_object.obj_class
    new_obj_class = obj_class.clone(geometry_type=sly.Bitmap)
    volume_object = figure.volume_object
    new_volume_object = volume_object.clone(obj_class=new_obj_class)
    new_geometry = figure.geometry.convert(sly.Bitmap)[0]
    return figure.clone(volume_object=new_volume_object, geometry=new_geometry)


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
        compression_level=1,
    )


def save_nrrd_mask_readable_name(nrrd_header, curr_obj_mask, output_save_path, object_name):
    output_dir = os.path.join(os.path.dirname(output_save_path), "human-readable-objects")
    if not os.path.exists(output_dir):
        mkdir(output_dir)

    output_save_path = os.path.join(output_dir, f"{object_name}.nrrd")
    output_save_path = get_nonexistent_path(output_save_path)

    nrrd.write(
        output_save_path,
        curr_obj_mask,
        header={
            "encoding": "gzip",
            "space": nrrd_header["space"],
            "space directions": nrrd_header["space directions"],
            "space origin": nrrd_header["space origin"],
        },
        compression_level=1,
    )


def get_nonexistent_path(file_path):
    filename, file_extension = os.path.splitext(file_path)
    i = 1
    new_fname = f"{filename}_object_{i:03d}{file_extension}"
    while os.path.exists(new_fname):
        i += 1
        new_fname = f"{filename}_object_{i:03d}{file_extension}"
    return new_fname
