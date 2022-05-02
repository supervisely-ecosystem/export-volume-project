def create_class2idx_map(project_meta):
    return {
        obj_class.name: idx + 1
        for idx, obj_class in enumerate(project_meta.obj_classes)
    }