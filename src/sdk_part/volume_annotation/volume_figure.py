from supervisely_lib.video_annotation.video_figure import VideoFigure
from supervisely_lib.video_annotation.video_object_collection import VideoObjectCollection
from supervisely_lib.video_annotation.key_id_map import KeyIdMap


class VolumeFigure(VideoFigure):
    def validate_bounds(self, img_size, _auto_correct=False):
        raise NotImplementedError("Volumes do not support it yet")

    @classmethod
    def from_json(cls, data, objects: VideoObjectCollection, key_id_map: KeyIdMap = None):
        return super().from_json(data, objects, 0, key_id_map)
