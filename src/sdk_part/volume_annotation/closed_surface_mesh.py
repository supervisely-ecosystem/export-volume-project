from supervisely_lib.geometry.geometry import Geometry
import supervisely_lib.annotation.json_geometries_map as geometries_map
from supervisely_lib.geometry.constants import ANY_SHAPE, LABELER_LOGIN, UPDATED_AT, CREATED_AT, ID, CLASS_ID


class ClosedSurfaceMesh(Geometry):
    @staticmethod
    def geometry_name():
        return 'closed_surface_mesh'

    def to_json(self):
        res = {}
        self._add_creation_info(res)
        return res

    @classmethod
    def from_json(cls, data):
        labeler_login = data.get(LABELER_LOGIN, None)
        updated_at = data.get(UPDATED_AT, None)
        created_at = data.get(CREATED_AT, None)
        sly_id = data.get(ID, None)
        class_id = data.get(CLASS_ID, None)
        return cls(sly_id=sly_id, class_id=class_id, labeler_login=labeler_login, updated_at=updated_at, created_at=created_at)

geometries_map._INPUT_GEOMETRIES.append(ClosedSurfaceMesh)
geometries_map._JSON_SHAPE_TO_GEOMETRY_TYPE[ClosedSurfaceMesh.geometry_name()] = ClosedSurfaceMesh