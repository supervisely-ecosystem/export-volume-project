# coding: utf-8

from supervisely_lib.video_annotation.key_id_map import KeyIdMap
from supervisely_lib.api.entity_annotation.object_api import ObjectApi
from supervisely_lib.api.module_api import ApiField
from supervisely_lib.sly_logger import logger
from sdk_part.volume_annotation.constants import VOLUME_ID
from sdk_part.volume_annotation.volume_object_collection import VolumeObjectCollection

class VolumeObjectApi(ObjectApi):
    def append_bulk(self, dataset_id, objects: VolumeObjectCollection, key_id_map: KeyIdMap = None):
        info = self._api.volume.get_info_by_id(dataset_id)
        return self._append_bulk(self._api.volume.tag, dataset_id, info.project_id, info.dataset_id, objects,
                                 key_id_map)

    def _get_interpolation(self, volume_id, object_id):
        return self._api.post('figures.volumetric_interpolation', {VOLUME_ID: volume_id,
                                                                   ApiField.OBJECT_ID: object_id})

    def get_interpolation(self, volume_id, objects: VolumeObjectCollection, key_id_map):
        results = []

        for object in objects:
            object_id = key_id_map.get_object_id(object.key())
            try:
                response = self._get_interpolation(volume_id, object_id)
                results.append(response.content)
            except Exception as e:
                logger.warn(f"Error while building interpolation on server for object {object_id} : {e}")
                results.append(None)
        return results
