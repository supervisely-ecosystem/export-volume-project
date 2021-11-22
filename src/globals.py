import os
from pathlib import Path
import sys
from dotenv import load_dotenv
from distutils.util import strtobool

import supervisely_lib as sly

root_source_dir = str(Path(sys.argv[0]).parents[1])
print(f"App source directory: {root_source_dir}")
sys.path.append(root_source_dir)

# only for convenient debug
debug_env_path = os.path.join(root_source_dir, "debug.env")
secret_debug_env_path = os.path.join(root_source_dir, "secret_debug.env")
load_dotenv(debug_env_path)
load_dotenv(secret_debug_env_path, override=True)


api: sly.Api = sly.Api.from_env()
my_app: sly.AppService = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
TASK_ID = int(os.environ["TASK_ID"])
BATCH_SIZE = 1

try:
    PROJECT_ID = int(os.environ['modal.state.slyProjectId'])
except KeyError:
    PROJECT_ID = None

try:
    DATASET_ID = int(os.environ['modal.state.slyDatasetId'])
except KeyError:
    DATASET_ID = None

assert DATASET_ID or PROJECT_ID


download_volumes = bool(strtobool(os.getenv('modal.state.download_volumes')))