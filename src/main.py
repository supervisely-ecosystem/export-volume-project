import os

import supervisely as sly
from supervisely.io.json import dump_json_file, load_json_file
from supervisely.project.volume_project import download_volume_project
from supervisely.video_annotation.key_id_map import KeyIdMap

import functions as f
import stl_to_nrrd
import globals as g


class MyExport(sly.app.Export):
    def process(self, context: sly.app.Export.Context):
        
        api = sly.Api.from_env()

        project = api.project.get_info_by_id(id=context.project_id)
        project_name = project.name

        download_dir = os.path.join(g.STORAGE_DIR, f"{project.id}_{project_name}")
        sly.fs.remove_dir(download_dir)

        download_volume_project(
            api=api,
            project_id=project.id,
            dest_dir=download_dir,
            dataset_ids=[context.dataset_id] if context.dataset_id is not None else None,
            download_volumes=g.download_volumes,
            log_progress=True,
        )

        project_meta_local = load_json_file(os.path.join(download_dir, "meta.json"))
        project_meta = sly.ProjectMeta.from_json(project_meta_local)

        key_id_map = KeyIdMap.load_json(os.path.join(download_dir, "key_id_map.json"))
        class2idx = f.create_class2idx_map(project_meta)
        class2idx_path = os.path.join(download_dir, "class2idx.json")
        dump_json_file(class2idx, class2idx_path)

        if g.download_volumes and any(
            [
                g.convert_surface_to_mask,
                g.save_instance_segmentation,
                g.save_semantic_segmentation,
            ]
        ):
            stl_to_nrrd.convert_all(download_dir, project_meta, key_id_map)

        full_archive_name = f"{project.id}_{project.name}.tar"
        result_archive = os.path.join(g.STORAGE_DIR, full_archive_name)
        sly.fs.archive_directory(download_dir, result_archive)
        sly.logger.info("Result directory is archived")

        return result_archive


app = MyExport()
app.run()
