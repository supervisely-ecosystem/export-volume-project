import os
import glob
import nrrd
import trimesh
import supervisely_lib as sly

stl_extension = '.stl'
nrrd_extension = '.nrrd'


def convert_all(dir_path):
    all_stl_files = glob.glob(os.path.join(dir_path, '**/*' + stl_extension), recursive=True)
    for stl_path in all_stl_files:
        pre, ext = os.path.splitext(stl_path)
        nrrd_path = pre + nrrd_extension
        convert_stl_to_nrrd(stl_path, nrrd_path)


def convert_stl_to_nrrd(stl_path: str, nrrd_path: str):
    """
        Latest verion of this function from: https://github.com/supervisely-ecosystem/stl-to-nrrd/
    """
    if not sly.fs.file_exists(stl_path):
        raise ValueError('File at given path {} not exist'.format(stl_path))

    if sly.fs.get_file_ext(stl_path) != stl_extension:
        raise ValueError('File extension must be .stl, not {}'.format(sly.fs.get_file_ext(stl_path)))

    mesh = trimesh.load(stl_path)
    voxel = mesh.voxelized(pitch=1.0)
    voxel = voxel.fill()
    np_mask = voxel.matrix.astype(int)
    nrrd.write(nrrd_path, np_mask)

