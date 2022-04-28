from supervisely_lib.video_annotation.video_object import VideoObject
from supervisely_lib.annotation.obj_class import ObjClass
from supervisely_lib.video_annotation.video_tag_collection import VideoTagCollection
from supervisely_lib._utils import take_with_default
import uuid


class VolumeObject(VideoObject):
    def __init__(self, obj_class: ObjClass, tags: VideoTagCollection = None, key=None, class_id=None,
                 labeler_login=None, updated_at=None, created_at=None):
        '''
        :param obj_class: ObjClass class object
        :param tags: VideoTagCollection
        :param key: uuid class object
        '''
        super().__init__(obj_class, tags, key, class_id, labeler_login, updated_at, created_at)
        self.labeler_login = labeler_login
        self.updated_at = updated_at
        self.created_at = created_at
        self.class_id = class_id

        self._obj_class = obj_class
        self._key = take_with_default(key, uuid.uuid4())
        self._tags = take_with_default(tags, VideoTagCollection())
