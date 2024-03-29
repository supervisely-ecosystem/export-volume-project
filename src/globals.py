import os
import sys
from distutils.util import strtobool
from pathlib import Path

import supervisely as sly
from dotenv import load_dotenv
from supervisely.app.v1.app_service import AppService

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


download_volumes = bool(strtobool(os.getenv("modal.state.downloadVolumes")))
download_annotations = True  # bool(strtobool(os.getenv('modal.state.downloadAnnotations')))
save_instance_segmentation = bool(strtobool(os.getenv("modal.state.saveInstanceSegmentationMasks")))
save_semantic_segmentation = bool(strtobool(os.getenv("modal.state.saveSemanticSegmentationMasks")))

class2idx = {}

if not download_volumes:
    save_instance_segmentation = False
    save_semantic_segmentation = False
