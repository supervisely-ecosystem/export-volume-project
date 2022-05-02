# coding: utf-8
import re

from requests_toolbelt import MultipartDecoder, MultipartEncoder
from supervisely_lib._utils import batched
from supervisely_lib.api.module_api import ApiField
from supervisely_lib.api.video.video_figure_api import VideoFigureApi
from supervisely_lib.io.fs import ensure_base_path
from supervisely_lib.video_annotation.key_id_map import KeyIdMap

import sdk_part.volume_annotation.constants as const


class VolumeFigureApi(VideoFigureApi):
    def create(
        self, volume_id, object_id, slice_index, normal, geometry_json, geometry_type
    ):
        return super().create(
            volume_id,
            object_id,
            {ApiField.META: {const.SLICE_INDEX: slice_index, const.NORMAL: normal}},
            geometry_json,
            geometry_type,
        )

    def append_bulk(self, volume_id, figures, normal, key_id_map: KeyIdMap):
        keys = []
        figures_json = []
        for figure in figures:
            keys.append(figure.key())
            fig_json = figure.to_json(key_id_map, save_meta=True)

            slice_index = fig_json[ApiField.META][ApiField.FRAME]
            fig_json[ApiField.META] = {
                const.SLICE_INDEX: slice_index,
                const.NORMAL: normal,
            }
            figures_json.append(fig_json)

        self._append_bulk(volume_id, figures_json, keys, key_id_map)

    # def download_geometries_batch(self, figure_ids, save_paths):
    #     return self._api.post('figures.bulk.download.geometry', {ApiField.IDS: figure_ids})

    def _download_geometries_batch(self, ids):
        for batch_ids in batched(ids):
            response = self._api.post(
                "figures.bulk.download.geometry", {ApiField.IDS: batch_ids}
            )
            decoder = MultipartDecoder.from_response(response)
            for part in decoder.parts:
                content_utf8 = part.headers[b"Content-Disposition"].decode("utf-8")
                # Find name="1245" preceded by a whitespace, semicolon or beginning of line.
                # The regex has 2 capture group: one for the prefix and one for the actual name value.
                figure_id = int(
                    re.findall(r'(^|[\s;])name="(\d*)"', content_utf8)[0][1]
                )
                yield figure_id, part

    def download_geometries_paths(self, ids, paths):
        if len(ids) == 0:
            return
        if len(ids) != len(paths):
            raise RuntimeError(
                'Can not match "ids" and "paths" lists, len(ids) != len(paths)'
            )

        id_to_path = {id: path for id, path in zip(ids, paths)}
        for img_id, resp_part in self._download_geometries_batch(ids):
            ensure_base_path(id_to_path[img_id])
            with open(id_to_path[img_id], "wb") as w:
                w.write(resp_part.content)
