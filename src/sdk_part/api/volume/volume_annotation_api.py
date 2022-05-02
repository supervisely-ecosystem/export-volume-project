# coding: utf-8


from supervisely_lib.api.entity_annotation.entity_annotation_api import \
    EntityAnnotationAPI
from supervisely_lib.api.module_api import ApiField
from supervisely_lib.video_annotation.key_id_map import KeyIdMap

from sdk_part.volume_annotation.volume_annotation import (VolumeAnnotation,
                                                          const)


class VolumeAnnotationApi(EntityAnnotationAPI):
    _method_download_bulk = "volumes.annotations.bulk.info"
    _entity_ids_str = const.VOLUME_IDS

    def download_bulk(self, dataset_id, volume_ids):
        response = self._api.post(
            self._method_download_bulk,
            {ApiField.DATASET_ID: dataset_id, self._entity_ids_str: volume_ids},
        )
        return response.json()

    def download(self, entity_id):
        dataset_id = self._api.volume.get_info_by_id(entity_id).dataset_id
        return self.download_bulk(dataset_id, [entity_id]).pop()

    def append(self, volume_id, ann: VolumeAnnotation, key_id_map: KeyIdMap = None):
        if key_id_map is None:
            key_id_map = KeyIdMap()

        info = self._api.volume.get_info_by_id(volume_id)

        self._api.volume.tag.append_to_entity(
            volume_id, info.project_id, ann.tags, key_id_map
        )
        self._api.volume.object.append_bulk(volume_id, ann.objects, key_id_map)

        self._api.volume.figure.append_bulk(
            volume_id, ann.axial.figures, ann.axial.normal, key_id_map
        )
        self._api.volume.figure.append_bulk(
            volume_id, ann.coronal.figures, ann.coronal.normal, key_id_map
        )
        self._api.volume.figure.append_bulk(
            volume_id, ann.sagittal.figures, ann.sagittal.normal, key_id_map
        )
