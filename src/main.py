import os
import globals as g
import supervisely_lib as sly

from sdk_part.project.volume_project import download_volume_project
from sdk_part.api.volume.volume_api import VolumeApi
import stl_to_nrrd

@g.my_app.callback("download")
@sly.timeit
def download(api: sly.Api, task_id, context, state, app_logger):
    setattr(api, 'volume', VolumeApi(api))  # custom extension for api instance

    if g.PROJECT_ID:
        project = api.project.get_info_by_id(g.PROJECT_ID)
    else:
        dataset = api.dataset.get_info_by_id(g.DATASET_ID)
        project = api.project.get_info_by_id(dataset.project_id)

    download_dir = os.path.join(g.my_app.data_dir, f'{project.id}_{project.name}')
    sly.fs.remove_dir(download_dir)

    download_volume_project(api,
                            project.id,
                            download_dir,
                            dataset_ids=[g.DATASET_ID] if g.DATASET_ID else None,
                            download_volumes=g.download_volumes,
                            log_progress=True,
                            batch_size=g.BATCH_SIZE)

    stl_to_nrrd.convert_all(download_dir)

    full_archive_name = str(project.id) + '_' + project.name + '.tar'
    result_archive = os.path.join(g.my_app.data_dir, full_archive_name)
    sly.fs.archive_directory(download_dir, result_archive)
    app_logger.info("Result directory is archived")

    upload_progress = []
    remote_archive_path = "/Export-Supervisely-volumes-projects/{}_{}".format(task_id, full_archive_name)
    remote_archive_path = api.file.get_free_name(g.TEAM_ID, remote_archive_path)

    def _print_progress(monitor, upload_progress):
        if len(upload_progress) == 0:
            upload_progress.append(sly.Progress(message="Upload {!r}".format(full_archive_name),
                                                total_cnt=monitor.len,
                                                ext_logger=app_logger,
                                                is_size=True))
        upload_progress[0].set_current_value(monitor.bytes_read)

    file_info = api.file.upload(g.TEAM_ID, result_archive, remote_archive_path,
                                lambda m: _print_progress(m, upload_progress))
    app_logger.info("Uploaded to Team-Files: {!r}".format(file_info.full_storage_url))
    api.task.set_output_archive(task_id, file_info.id, full_archive_name, file_url=file_info.full_storage_url)
    g.my_app.stop()


def main():
    sly.logger.info(
        "Script arguments",
        extra={
            "TEAM_ID": g.TEAM_ID,
            "WORKSPACE_ID": g.WORKSPACE_ID,
            "PROJECT_ID": g.PROJECT_ID,
            "download_volumes": g.download_volumes,
        }
    )

    g.my_app.run(initial_events=[{"command": "download"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main)
