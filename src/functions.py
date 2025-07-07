from collections import defaultdict
import os

from sly_globals import PlanePrefix
import nrrd
import supervisely as sly
from supervisely.io.fs import mkdir
from supervisely.io.json import load_json_file
from supervisely.volume_annotation.volume_annotation import VolumeAnnotation
from supervisely.convert.volume.nii import nii_volume_helper as helper


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


plane_xyz_map = {
    PlanePrefix.SAGITTAL: "1-0-0",
    PlanePrefix.CORONAL: "0-1-0",
    PlanePrefix.AXIAL: "0-0-1",
}
get_xyz = lambda x: plane_xyz_map.get(x, "0-0-1")


def convert_project_to_nifti(local_project_dir: str, segmentation_type: str) -> str:
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
    import sly_globals as g
    import numpy as np
    from pathlib import Path

    project_id = g.get_project_id()

    project_fs = sly.VolumeProject(local_project_dir, mode=sly.OpenMode.READ)
    new_suffix = "_nifti"
    new_name = f"{project_fs.name}{new_suffix}"
    new_project_dir = Path(local_project_dir).parent / new_name
    new_project_dir.mkdir(parents=True, exist_ok=True)

    meta = project_fs.meta

    def _find_pixel_values(descr: str) -> int:
        """
        Find the pixel value in the description string.
        """
        lines = descr.split("\n")
        for line in lines:
            if line.strip().startswith(helper.MASK_PIXEL_VALUE):
                try:
                    value_part = line.strip().split(helper.MASK_PIXEL_VALUE)[1]
                    return int(value_part.strip())
                except (IndexError, ValueError):
                    continue
        return None

    mask_pixel_values = {
        obj_class.name: _find_pixel_values(obj_class.description) for obj_class in meta.obj_classes
    }

    color_map = {}
    used_indices = set()

    # First assign original pixel_values (if they exist)
    for obj_class in meta.obj_classes:
        original_pixel_value = mask_pixel_values.get(obj_class.name)
        if original_pixel_value is not None:
            color_map[obj_class.name] = [original_pixel_value, obj_class.color]
            used_indices.add(original_pixel_value)

    # Then assign free indices to classes without original pixel_values
    next_available_idx = 1
    for obj_class in meta.obj_classes:
        if obj_class.name not in color_map:
            # Find the next available index
            while next_available_idx in used_indices:
                next_available_idx += 1

            color_map[obj_class.name] = [next_available_idx, obj_class.color]
            used_indices.add(next_available_idx)
            next_available_idx += 1

    color_map_to_txt = []
    for name, (idx, color) in color_map.items():
        color_map_to_txt.append(f"{idx} {name} {' '.join(map(str, color))}")
    color_map_txt_path = new_project_dir / "color_map.txt"

    ds_infos = g.api.dataset.get_list(project_id, recursive=True)

    for ds in project_fs.datasets:
        ds: sly.VolumeDataset

        ds_name = ds.name
        if "/" in ds_name:
            ds_name = ds.name.split("/")[-1]
        curr_ds_info = next(info for info in ds_infos if info.name == ds_name)

        ds_path = new_project_dir / ds.name
        ds_path.mkdir(parents=True, exist_ok=True)

        ds_structure_type = 2
        prefixes = [PlanePrefix.AXIAL, PlanePrefix.CORONAL, PlanePrefix.SAGITTAL]
        for item_name in ds.get_items_names():
            if not any(prefix in item_name for prefix in prefixes):
                ds_structure_type = 1
                break

        if ds_structure_type == 2:
            if not sly.fs.file_exists(color_map_txt_path):
                with open(color_map_txt_path, "w") as f:
                    f.write("\n".join(color_map_to_txt))
                sly.logger.info(f"Color map saved to {color_map_txt_path}")

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
                direction = np.array(volume_meta["directions"]).reshape(3, 3)
                spacing = np.array(volume_meta["spacing"])
                space_directions = (direction.T * spacing[:, None]).tolist()
                volume_header = {
                    "space": "right-anterior-superior",
                    "space directions": space_directions,
                    "space origin": volume_meta.get("origin", None),
                }
                semantic = np.zeros(volume_np.shape, dtype=np.uint8)
                instances = {}
                cls_to_npy = {
                    obj.obj_class.name: np.zeros(volume_np.shape, dtype=np.uint8)
                    for obj in ann.objects
                }
                custom_data = defaultdict(lambda: defaultdict(float))

                if ds_structure_type == 2:
                    used_labels = set()
                    for fig in ann.figures + ann.spatial_figures:
                        if fig.custom_data:
                            plane = None
                            for key in prefixes:
                                if key in short_name:
                                    plane = key
                                    break
                            plane = get_xyz(plane)
                            if plane is not None and plane in fig.custom_data:
                                label_index = color_map[fig.volume_object.obj_class.name][0]
                                for _frame_idx, _data in fig.custom_data[plane].items():
                                    if "score" in _data:
                                        custom_data[_frame_idx][f"Label-{label_index}"] = _data[
                                            "score"
                                        ]
                                        used_labels.add(fig.volume_object.obj_class.name)

                mask_dir = ds.get_mask_dir(name)

                if mask_dir is not None and sly.fs.dir_exists(mask_dir):
                    mask_paths = sly.fs.list_files(mask_dir, valid_extensions=[".nrrd"])
                    nrrd_data_dict = {}
                    for mask_path in mask_paths:
                        key = os.path.basename(mask_path).replace(".nrrd", "")
                        data, _ = nrrd.read(mask_path)
                        nrrd_data_dict[key] = data
                for sf in ann.spatial_figures:
                    class_name = sf.volume_object.obj_class.name

                    try:
                        mask_data = nrrd_data_dict[sf.key().hex]
                        mask3d = sly.Mask3D(mask_data, volume_header=volume_header)
                    except Exception as e:
                        sly.logger.warning(
                            f"Skipping spatial figure {sf.key().hex} for class '{class_name}': {str(e)}"
                        )
                        continue

                    if ds_structure_type == 2:
                        pixel_value = color_map[class_name][0]
                        if segmentation_type == "semantic":
                            semantic[mask3d.data] = pixel_value
                        else:  # instance segmentation
                            if pixel_value not in instances.keys():
                                instances[pixel_value] = np.zeros(volume_np.shape, dtype=np.uint8)
                            idx = instances[pixel_value].max() + 1
                            instances[pixel_value][mask3d.data] = idx
                    else:  # ds_structure_type == 1
                        val = 1
                        if segmentation_type != "semantic":
                            val = cls_to_npy[class_name].max() + 1
                        cls_to_npy[class_name][mask3d.data] = val

                def _get_label_path(entity_name, ext):
                    if ds_structure_type == 1:
                        labels_dir = ds_path / short_name
                        labels_dir.mkdir(parents=True, exist_ok=True)
                        label_path = labels_dir / f"{entity_name}{ext}"
                    else:
                        idx = 1
                        label_path = ds_path / (short_name.replace("anatomic", "inference") + ext)
                        while label_path.exists():
                            idx += 1
                            label_path = ds_path / (
                                short_name.replace("anatomic", "inference") + f"_{idx}" + ext
                            )

                    return label_path

                def _save_ann(ent_to_npy, ext, affine=None):
                    for entity_name, npy in ent_to_npy.items():
                        label_path = _get_label_path(entity_name, ext)
                        label_nifti = nib.Nifti1Image(npy, affine)
                        nib.save(label_nifti, label_path)

                volume_affine = nib.as_closest_canonical(nib.load(res_path)).affine

                if ds_structure_type == 1:
                    mapping = cls_to_npy
                else:
                    mapping = instances if segmentation_type != "semantic" else {ds.name: semantic}

                _save_ann(mapping, ext, volume_affine)

                if ds_structure_type == 2 and segmentation_type == "semantic" and len(custom_data) > 0:
                    csv_path = ds_path / f"{short_name}.csv"
                    with open(csv_path, "w") as f:
                        col_names = [f"Label-{color_map[name][0]}" for name in used_labels]
                        f.write(",".join(["Layer"] + col_names) + "\n")
                        for layer, scores in custom_data.items():
                            scores_str = [str(scores.get(name, 0.0)) for name in col_names]
                            f.write(",".join([str(layer)] + scores_str) + "\n")

    sly.logger.info(f"Converted project to NIfTI")

    sly.fs.remove_dir(local_project_dir)
    os.rename(str(new_project_dir), local_project_dir)


def write_meshes(local_project_dir: str, mesh_export_type: str) -> str:
    """
    Write meshes to the local project directory.

    Args:
        local_project_dir (str): Path to the local project directory.
        mesh_export_type (str): Type of mesh export (e.g., "stl").
    """
    from supervisely.volume_annotation.constants import SPATIAL_FIGURES, KEY
    from pathlib import Path
    from sly_globals import api

    project_fs = sly.VolumeProject(local_project_dir, mode=sly.OpenMode.READ)
    local_project_dir = Path(local_project_dir)
    out_dir = local_project_dir.with_name("meshes")

    for ds in project_fs.datasets:
        ds: sly.VolumeDataset
        ds_path = local_project_dir / ds.name
        for name in ds.get_items_names():
            ann_path = ds.get_ann_path(name)
            ann_json = sly.json.load_json_file(ann_path)
            ann = sly.VolumeAnnotation.from_json(ann_json, project_fs.meta)
            if len(ann.spatial_figures) == 0:
                continue
            fig_index = {f[KEY]: f["geometry"]["id"] for f in ann_json[SPATIAL_FIGURES]}

            export_folder = out_dir / ds.name / Path(name).stem
            export_folder.mkdir(parents=True, exist_ok=True)
            for fig in ann.spatial_figures:
                figure_key = fig.key().hex
                figure_id = fig_index.get(figure_key, None)
                if figure_id is None:
                    sly.logger.warning(f"Figure ID not found in JSON for figure {fig.key().hex}")
                    continue

                sf_geometry_name = figure_key + ".nrrd"
                full_sf_geometry_path = os.path.join(
                    ds_path, ds.get_mask_dir(name), sf_geometry_name
                )
                if os.path.exists(full_sf_geometry_path):
                    sly.logger.debug(f"Loading geometry from file. Path: {full_sf_geometry_path}")
                    try:
                        mask3d = sly.Mask3D.create_from_file(full_sf_geometry_path)
                        assert mask3d is not None, "Failed to create Mask3D"
                        fig._set_3d_geometry(mask3d)
                    except Exception as e:
                        sly.logger.warning(
                            f"Failed to load geometry from {full_sf_geometry_path}: {str(e)}"
                        )
                        continue
                else:
                    api.volume.figure.load_sf_geometry(fig, project_fs.key_id_map)

                sly.logger.debug(f"Mask3D shape: {fig.geometry.data.shape}")
                volume_header = None
                if fig.geometry.space_directions is None or fig.geometry.space_origin is None:
                    try:
                        volume_path = ds.get_item_path(name)
                        volume_header = nrrd.read_header(volume_path)
                    except Exception as e:
                        sly.logger.warning(
                            f"Failed to set NRRD header for geometry (figure id: {figure_id}): {str(e)}"
                        )
                        continue

                path = (export_folder / f"{figure_id}.{mesh_export_type}").as_posix()
                try:
                    sly.volume.volume.export_3d_as_mesh(
                        fig.geometry, path, volume_meta=volume_header
                    )
                except Exception as e:
                    sly.logger.warning(
                        f"Failed to write mesh for figure (id: {fig.geometry.sly_id}): {str(e)}"
                    )
                    continue

    sly.logger.info(f"Finished downloading meshes")
    return str(out_dir)
