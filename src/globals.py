import os
import sys
from distutils.util import strtobool
from pathlib import Path

import supervisely as sly
from dotenv import load_dotenv
from supervisely.app.v1.app_service import AppService
from supervisely.collection.str_enum import StrEnum

root_source_dir = str(Path(sys.argv[0]).parents[1])
print(f"App source directory: {root_source_dir}")
sys.path.append(root_source_dir)

# only for convenient debug
if sly.is_development():
    load_dotenv("debug.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))


api: sly.Api = sly.Api.from_env()
my_app: AppService = AppService()

TEAM_ID = int(os.environ["context.teamId"])
WORKSPACE_ID = int(os.environ["context.workspaceId"])
TASK_ID = int(os.environ["TASK_ID"])

try:
    PROJECT_ID = int(os.environ["modal.state.slyProjectId"])
except KeyError:
    PROJECT_ID = None

try:
    DATASET_ID = int(os.environ["modal.state.slyDatasetId"])
except KeyError:
    DATASET_ID = None

assert DATASET_ID or PROJECT_ID

format = os.getenv("modal.state.format", "sly")
segmentation_type = None if format == "sly" else os.getenv("modal.state.segmentationType", "semantic")
download_volumes = bool(strtobool(os.getenv("modal.state.downloadVolumes")))
download_annotations = True  # bool(strtobool(os.getenv('modal.state.downloadAnnotations')))
save_instance_segmentation = bool(strtobool(os.getenv("modal.state.saveInstanceSegmentationMasks")))
save_semantic_segmentation = bool(strtobool(os.getenv("modal.state.saveSemanticSegmentationMasks")))

save_mesh = bool(strtobool(os.getenv("modal.state.saveMesh")))
mesh_export_type = os.getenv("modal.state.meshExportType", "stl")
class2idx = {}

if not download_volumes:
    save_instance_segmentation = False
    save_semantic_segmentation = False

class PlanePrefix(str, StrEnum):
    """Prefix for plane names."""

    CORONAL = "cor"
    SAGITTAL = "sag"
    AXIAL = "axl"

def get_project_id() -> int:
    # for cases when only dataset id is provided but project id is needed intended to not break the code
    if PROJECT_ID:
        return PROJECT_ID
    return api.dataset.get_info_by_id(DATASET_ID).project_id
