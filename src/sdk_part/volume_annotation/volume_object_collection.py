# coding: utf-8

from supervisely_lib.video_annotation.video_object_collection import \
    VideoObjectCollection

from sdk_part.volume_annotation.volume_object import VolumeObject


class VolumeObjectCollection(VideoObjectCollection):
    item_type = VolumeObject
