import os

import supervisely as sly

from draw_masks import convert_all
from supervisely.api.volume.volume_api import VolumeApi
from supervisely.io.json import dump_json_file, load_json_file
from supervisely.project.volume_project import download_volume_project
from supervisely.video_annotation.key_id_map import KeyIdMap

import functions as f
import globals as g
import workflow as w


@g.my_app.callback("download")
@sly.timeit
def download(api: sly.Api, task_id, context, state, app_logger):
    setattr(api, "volume", VolumeApi(api))  # custom extension for api instance

    if g.DATASET_ID:
        dataset = api.dataset.get_info_by_id(g.DATASET_ID)
        project = api.project.get_info_by_id(dataset.project_id)
        w.workflow_input(api, dataset.id, "dataset")
    elif g.PROJECT_ID:
        project = api.project.get_info_by_id(g.PROJECT_ID)
        w.workflow_input(api, project.id, "project")
    else:
        raise ValueError("PROJECT_ID or DATASET_ID should be provided")

    download_dir = os.path.join(
        g.my_app.data_dir, f"{project.id}_{project.name}/{project.id}_{project.name}"
    )
    sly.fs.remove_dir(download_dir)

    download_volume_project(
        api=api,
        project_id=project.id,
        dest_dir=download_dir,
        dataset_ids=[g.DATASET_ID] if g.DATASET_ID else None,
        download_volumes=g.download_volumes,
        log_progress=True,
    )

    if g.format == "sly":
        project_meta_local = load_json_file(os.path.join(download_dir, "meta.json"))
        project_meta = sly.ProjectMeta.from_json(project_meta_local)

        key_id_map = KeyIdMap.load_json(os.path.join(download_dir, "key_id_map.json"))
        g.class2idx = f.create_class2idx_map(project_meta)
        class2idx_path = os.path.join(download_dir, "class2idx.json")
        dump_json_file(g.class2idx, class2idx_path)
        
        if g.download_volumes and any(
            [
                g.save_instance_segmentation,
                g.save_semantic_segmentation,
            ]
        ):
            convert_all(download_dir, project_meta, key_id_map)
    elif g.format == "nifti":
        download_dir = f.convert_volume_project(download_dir, g.format, g.segmentation_type)
    else:
        raise ValueError(f"Unsupported format: {g.format}")

    full_archive_name = str(project.id) + "_" + project.name + ".tar"
    result_archive = os.path.join(g.my_app.data_dir, full_archive_name)
    archive_dir = os.path.dirname(download_dir)
    sly.fs.archive_directory(archive_dir, result_archive)
    app_logger.info("Result directory is archived")

    upload_progress = []
    remote_archive_path = os.path.join(
        sly.team_files.RECOMMENDED_EXPORT_PATH,
        "export-supervisely-volumes-projects/{}_{}".format(task_id, full_archive_name),
    )
    remote_archive_path = api.file.get_free_name(g.TEAM_ID, remote_archive_path)

    def _print_progress(monitor, upload_progress):
        if len(upload_progress) == 0:
            upload_progress.append(
                sly.Progress(
                    message="Upload {!r}".format(full_archive_name),
                    total_cnt=monitor.len,
                    ext_logger=app_logger,
                    is_size=True,
                )
            )
        upload_progress[0].set_current_value(monitor.bytes_read)

    file_info = api.file.upload(
        g.TEAM_ID,
        result_archive,
        remote_archive_path,
        lambda m: _print_progress(m, upload_progress),
    )
    app_logger.info("Uploaded to Team-Files: {!r}".format(file_info.storage_path))
    api.task.set_output_archive(
        task_id, file_info.id, full_archive_name, file_url=file_info.storage_path
    )
    w.workflow_output(api, file_info)
    g.my_app.stop()


def main():
    sly.logger.info(
        "Script arguments",
        extra={
            "TEAM_ID": g.TEAM_ID,
            "WORKSPACE_ID": g.WORKSPACE_ID,
            "PROJECT_ID": g.PROJECT_ID,
            "download_volumes": g.download_volumes,
        },
    )

    g.my_app.run(initial_events=[{"command": "download"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main)
