import os

import nrrd
import supervisely as sly
from supervisely.io.fs import mkdir
from supervisely.io.json import load_json_file
from supervisely.volume_annotation.volume_annotation import VolumeAnnotation


def create_class2idx_map(project_meta: sly.ProjectMeta):
    return {obj_class.name: idx + 1 for idx, obj_class in enumerate(project_meta.obj_classes)}


def get_volume_ann_from_path(project_meta, ann_dir, nrrd_file_name):
    ann_path = os.path.join(ann_dir, f"{nrrd_file_name}.json")
    ann_json = load_json_file(ann_path)
    return VolumeAnnotation.from_json(ann_json, project_meta)


def convert_to_bitmap(figure: sly.VolumeFigure):
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
        compression_level=9,
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
        compression_level=9,
    )


def get_nonexistent_path(file_path):
    filename, file_extension = os.path.splitext(file_path)
    i = 1
    new_fname = f"{filename}_object_{i:03d}{file_extension}"
    while os.path.exists(new_fname):
        i += 1
        new_fname = f"{filename}_object_{i:03d}{file_extension}"
    return new_fname



def convert_nrrd_to_nifti(nrrd_path: str, nifti_path: str) -> None:
    """
    Convert a NRRD volume to NIfTI format.
    Preserve the original header information.

    Args:
        nrrd_path (str): Path to the input NRRD file.
        nifti_path (str): Path to the output NIfTI file.
    """

    import SimpleITK as sitk

    img = sitk.ReadImage(nrrd_path)
    sitk.WriteImage(img, nifti_path)


def convert_volume_project(local_project_dir: str, segmentation_type: str) -> str:
    """
    Convert a volume project to NIfTI format.

    Args:
        local_project_dir (str): Path to the local project directory.

    Returns:
        str: Path to the converted project directory.
    """

    # nifti structure type 1:
    #  📂 'dataset 2025-03-05 12:17:16'
    #   ├── 📂 CTChest
    #   │   ├── 🩻 lung.nii.gz
    #   │   └── 🩻 tumor.nii.gz
    #   ├── 🩻 CTChest.nii.gz
    #   └── 🩻 Spine.nii.gz
    # nifti structure type 2 (special case):
    # 📂 'dataset 2025-03-05 12:17:16'
    # ├── 🩻 axl_anatomic_1.nii
    # ├── 🩻 axl_inference_1.nii
    # ├── 🩻 cor_anatomic_1.nii
    # ├── 🩻 cor_inference_1.nii
    # ├── 🩻 sag_anatomic_1.nii
    # └── 🩻 sag_inference_1.nii

    import nibabel as nib
    import globals as g
    from globals import PlanePrefix
    import numpy as np
    from pathlib import Path


    project_id = g.get_project_id()

    project_fs = sly.VolumeProject(local_project_dir, mode=sly.OpenMode.READ)
    new_suffix = "_nifti"
    new_name = f"{project_fs.name}{new_suffix}"
    new_project_dir = Path(local_project_dir).parent / new_name
    new_project_dir.mkdir(parents=True, exist_ok=True)

    meta = project_fs.meta

    ds_infos = g.api.dataset.get_list(project_id, recursive=True)

    for ds in project_fs.datasets:
        ds: sly.VolumeDataset

        ds_name = ds.name
        if "/" in ds_name:
            ds_name = ds.name.split("/")[-1]
        curr_ds_info = next(info for info in ds_infos if info.name == ds_name)

        ds_path = new_project_dir / ds.name
        ds_path.mkdir(parents=True, exist_ok=True)

        ds_structure_type = 1
        prefixes = [PlanePrefix.AXIAL, PlanePrefix.CORONAL, PlanePrefix.SAGITTAL]
        if all(name[:3] in prefixes for name in ds.get_items_names()):
            ds_structure_type = 2

        for name in ds.get_items_names():
            volume_path = ds.get_item_path(name)
            ann_path = ds.get_ann_path(name)
            ann_json = sly.json.load_json_file(ann_path)
            ann = sly.VolumeAnnotation.from_json(ann_json, meta)

            short_name = name if not name.endswith(".nrrd") else name[:-5]
            ext = ".nii.gz"
            res_name = short_name + ext
            res_path = ds_path / res_name

            volume_info = g.api.volume.get_info_by_name(curr_ds_info.id, name)
            use_remote_link = volume_info.meta is not None and "remote_path" in volume_info.meta
            if use_remote_link:
                remote_path = volume_info.meta["remote_path"]
                if Path(remote_path).suffix not in [".nii", ".gz"]:
                    use_remote_link = False
            if use_remote_link:
                sly.logger.info(f"Found remote path for {name}")
                sly.logger.info(f"Downloading from remote storage: {remote_path}")

                remote_ext = Path(remote_path).suffixes
                if remote_ext != res_path.suffixes:
                    remote_ext = "".join(Path(remote_path).suffixes)
                    res_path = Path(str(res_path)[: -len(ext)]).with_suffix(remote_ext)
                g.api.storage.download(g.TEAM_ID, remote_path, res_path)
            else:
                sly.logger.info(f"Converting {name} to NIfTI")
                convert_nrrd_to_nifti(volume_path, res_path)

            if len(ann.objects) > 0:
                volume_np, volume_meta = sly.volume.read_nrrd_serie_volume_np(volume_path)

                cls_to_npy = {
                    obj.obj_class.name: np.zeros(volume_np.shape, dtype=np.uint8)
                    for obj in ann.objects
                }

                mask_dir = ds.get_mask_dir(name)
                geometries_dict = {}

                if mask_dir is not None and sly.fs.dir_exists(mask_dir):
                    mask_paths = sly.fs.list_files(mask_dir, valid_extensions=[".nrrd"])
                    geometries_dict.update(sly.Mask3D._bytes_from_nrrd_batch(mask_paths))

                for sf in ann.spatial_figures:
                    try:
                        geometry_bytes = geometries_dict[sf.key().hex]
                        mask3d = sly.Mask3D.from_bytes(geometry_bytes)
                    except Exception as e:
                        sly.logger.warning(
                            f"Skipping spatial figure for class '{sf.volume_object.obj_class.name}': {str(e)}"
                        )
                        continue

                    val = 1
                    if segmentation_type != "semantic":
                        val = cls_to_npy[sf.volume_object.obj_class.name].max() + 1
                    cls_to_npy[sf.volume_object.obj_class.name][mask3d.data] = val

                def _get_label_path(entity_name, ext):
                    if ds_structure_type == 1:
                        labels_dir = ds_path / short_name
                        labels_dir.mkdir(parents=True, exist_ok=True)
                        label_path = labels_dir / f"{entity_name}{ext}"
                    else:
                        prefix = PlanePrefix(short_name[:3])
                        idx = 1
                        label_path = ds_path / f"{prefix}_inference_{idx}{ext}"
                        while label_path.exists():
                            idx += 1
                            label_path = ds_path / f"{prefix}_inference_{idx}{ext}"

                    return label_path

                def _save_ann(ent_to_npy, ext, volume_meta, affine=None):
                    for entity_name, npy in ent_to_npy.items():
                        label_path = _get_label_path(entity_name, ext)
                        label_nifti = nib.Nifti1Image(npy, affine)
                        nib.save(label_nifti, label_path)

                affine = None
                nifti = nib.load(res_path)
                reordered_to_ras_nifti = nib.as_closest_canonical(nifti)
                affine = reordered_to_ras_nifti.affine

                _save_ann(cls_to_npy, ext, volume_meta, affine)

    sly.logger.info(f"Converted project to NIfTI")

    sly.fs.silent_remove(local_project_dir)
    os.rename(str(new_project_dir), local_project_dir)