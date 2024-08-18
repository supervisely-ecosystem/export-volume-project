# This module contains the functions that are used to configure the input and output of the workflow for the current app.

import supervisely as sly
from typing import Union, Literal


def workflow_input(api: sly.Api, id: Union[int, str], type: Literal["project", "dataset"]):
    if type == "project":
        api.app.workflow.add_input_project(int(id))
        sly.logger.debug(f"Workflow: Input project - {id}")
    elif type == "dataset":
        api.app.workflow.add_input_dataset(int(id))
        sly.logger.debug(f"Workflow: Input dataset - {id}")


def workflow_output(api: sly.Api, file: Union[int, sly.api.file_api.FileInfo]):
    try:
        if isinstance(file, int):
            file = api.file.get_info_by_id(file)
        relation_settings = sly.WorkflowSettings(
            title=file.name,
            icon="archive",
            icon_color="#33c94c",
            icon_bg_color="#d9f7e4",
            url=f"/files/{file.id}/true/?teamId={file.team_id}",
            url_title="Download",
        )
        meta = sly.WorkflowMeta(relation_settings=relation_settings)
        api.app.workflow.add_output_file(file, meta=meta)
        sly.logger.debug(f"Workflow: Output file - {file}")
    except Exception as e:
        sly.logger.debug(f"Failed to add output to the workflow: {repr(e)}")
