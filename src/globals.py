import os
import supervisely_lib as sly


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

download_volumes = os.getenv('modal.state.download_volumes').lower() in ('true', '1', 't')