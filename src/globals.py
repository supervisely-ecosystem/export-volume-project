import os
from distutils.util import strtobool

import supervisely as sly
from dotenv import load_dotenv


if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))


download_volumes = bool(strtobool(os.getenv("modal.state.downloadVolumes")))
download_annotations = (True)
convert_surface_to_mask = bool(strtobool(os.getenv("modal.state.convertSurfaceToMask")))
save_instance_segmentation = bool(
    strtobool(os.getenv("modal.state.saveInstanceSegmentationMasks"))
)
save_semantic_segmentation = bool(
    strtobool(os.getenv("modal.state.saveSemanticSegmentationMasks"))
)

STORAGE_DIR = sly.app.get_data_dir()

class2idx = {}

if not download_volumes:
    convert_surface_to_mask = False
    save_instance_segmentation = False
    save_semantic_segmentation = False
