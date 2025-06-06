<div align="center" markdown>

<img src="https://github.com/supervisely-ecosystem/export-volume-project/releases/download/v2.2.16/var_6.jpg">

# Export Volumes with 3D Annotations

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#whats-new">What's new</a> •
  <a href="#how-to-run">How To Run</a> •
  <a href="#how-to-use">How To Use</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervisely.com/apps/export-volume-project)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervisely.com/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/export-volume-project)
[![views](https://app.supervisely.com/img/badges/views/supervisely-ecosystem/export-volume-project.png)](https://supervisely.com)
[![runs](https://app.supervisely.com/img/badges/runs/supervisely-ecosystem/export-volume-project.png)](https://supervisely.com)

</div>

## Overview

🔥 All 3D data is exported as `.nrrd` for **compatibility with other popular medical viewers**, so that once downloaded, the volume and masks can be opened in specialized software like [MITK](http://www.mitk.org/) and [3D Slicer](https://www.slicer.org/) without any further action!

You can export as a whole Supervisely project or only as a dataset. To learn more about the format and its structure read [documentation](https://docs.supervisely.com/data-organization/00_ann_format_navi/08_supervisely_format_volume).

Application key points:
- Export annotations in `.json` and `.nrrd` formats
- Export volumes data in `.nrrd` format
- Export Instance segmentation as Mask3D for every non-Mask3D object in `.nrrd` format
- Instance segmentation masks are duplicated with human-readable file names for convenience
- Export Semantic segmentation as a single Mask3D for all objects in `.nrrd` format
- Semantic segmentation generates `class2idx.json` mapping, e.g. `{"lung": 1, "brain": 2}`
- Export project in NIfTI format for both semantic and instance segmentation tasks
- Export project's spatial geometries as `.stl` or `.obj` meshes

💡 If you will download only annotations, i.e. all available checkboxes will be turned off, the project structure will contain the `volume` directory with empty (zero-sized) volumes `.nrrd` files. This is not a bug, but a special solution for displaying the format in which you will need to substitute volumes when uploading them to the platform.

<div>
  <table>
    <tr style="width:100%">
      <td>
        <b>Volumes Data in Supervisely format</b>
        <img src="https://github.com/supervisely-ecosystem/export-volume-project/assets/57998637/ed1951e5-65a5-45ea-81ce-9a642f2468e6?raw-true"/>
      </td>
      <td>
        <b>Exported .nrrd with 3D segmentation mask</b>
        <img src="https://github.com/supervisely-ecosystem/export-volume-project/assets/57998637/26c862f9-a6a9-4378-937b-8d562fccc7f9?raw=true"/>
      </td>
    </tr>
  </table>
</div>


## What's new 

Version `v2.4.2`
  - Added option to export Mask3D (spatial) geometries as `STL` or `OBJ` meshes.

Version `v2.4.1`
  - Added option to export to NIfTI format for both instance and semantic segmentation types. If input data was originally imported in NIfTI format **from cloud storage**, original volume files will be exported instead of converting existing files. For more details on output structure, check [NIfTI converter documentation](https://docs.supervisely.com/import-and-export/import/supported-annotation-formats/volumes/nifti).

Version `v2.3.1`
 - 🏷️ Support for a new format for storing Mask3D objects geometry as `.nrrd` files in the `mask` directory. To learn more read [this article](https://docs.supervisely.com/data-organization/00_ann_format_navi/08_supervisely_format_volume).
 - ℹ️ Automatic conversion of `.stl` closed mesh surface interpolations to Mask3D when exporting. STL files will be saved in the project interpolation folder, but cannot be re-imported in future as closed mesh surfaces due to format obsolescence.

# How To Run

1. Add [Export volumes project in Supervisely format](https://ecosystem.supervisely.com/apps/export-volume-project)

   <img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/export-volume-project" src="https://i.imgur.com/DnAVFlZ.png" width="450px" style='padding-bottom: 20px'/>

2. Run the app from the context menu of **Volume Project** or **Volumes Dataset** → `Download via app` → `Export Supervisely volume project in Supervisely format`

   <img width="1250" alt="context menu" src="https://github.com/supervisely-ecosystem/export-volume-project/assets/57998637/563084d9-e8d5-485f-a90e-dcc5eb921175">

3. Define export settings in the modal window and press the **Run** button

   <img width="405" alt="export settings" src="https://github.com/supervisely-ecosystem/export-volume-project/assets/57998637/55f1730e-8e7d-4693-accf-98be5e749c12">


# How To Use

1. Wait for the app to process your data, and then the download link will become available
   <img width="1250" alt="2023-06-13_18-38-53" src="https://github.com/supervisely-ecosystem/export-volume-project/assets/57998637/6432147e-5b4d-4633-943e-66166a0d4ad4">


2. The resulting archive will be available for download by the link at the `Tasks` page or from `Team Files` by the following path:

- `Team Files` → `tmp` → `supervisely` → `export` → `export-supervisely-volumes-projects` → `<task_id>_<projectId>_<projectName>.tar`


  <img width="1250" alt="2023-06-13_18-28-51" src="https://github.com/supervisely-ecosystem/export-volume-project/assets/57998637/418d0687-ec3a-4435-b093-e58eed3116b2">

**Output project structure:**

```
📦project.tar
 └──📂project_dir
     ├──📂dataset_1
     │   ├──📂ann
     │   │   ├──📜CTChest.nrrd.json
     │   │   └──📜...
     │   ├──📂interpolation (optional)
     │   │   └──📂CTChest.nrrd
     │   │       ├──📜9aab4ddf1ddb4af1836006f0f1a3a694.stl
     │   │       └──📜...     
     │   ├──📂mask
     │   │   ├──📂CTChest.nrrd
     │   │   │   ├──📂human-readable-objects
     │   │   │   │   └──📜lung_object_001.nrrd
     │   │   │   ├──📜86a6bd27d358440fb97783f5fc7fec57.nrrd
     │   │   │   ├──📜9aab4ddf1ddb4af1836006f0f1a3a694.nrrd
     │   │   │   └──📜semantic_segmentation.nrrd
     │   │   └──📂...
     │   └──📂volume
     │       ├──📜CTChest.nrrd
     │       └──📜...
     ├──📜class2idx.json
     ├──📜key_id_map.json
     └──📜meta.json
```

## How to import annotations into 3D Slicer
All 3D annotations exported with this application are 3D models in NRRD format and have the same dimensions as its volume.

<img width="1250" alt="3dmasks_explanation" src="https://github.com/supervisely-ecosystem/dicom-spatial-figures/assets/57998637/e420a798-d376-40fc-b118-44c62615aef2"/>

We can also export objects with any shape as voxelized annotations using option `Additionally, save each object in Mask3D format` (instance segmentation) in the modal window of this application or `Additionally, save all objects as one in Mask3D format` (semantic segmentation)

Annotations before the exporting with `mask` and `polygon` shapes:

<img width="1250" alt="other_shapes" src="https://github.com/supervisely-ecosystem/export-volume-project/releases/download/v2.2.16/mask_polygon.png"/>


The same annotations after exporting with the option mentioned before:

<img width="1250" alt="3dmask_shapes" src="https://github.com/supervisely-ecosystem/export-volume-project/releases/download/v2.2.16/mask3d.png"/>

Representation in 3D Slicer:

<img width="400" alt="3dmask_shapes_slicer" src="https://github.com/supervisely-ecosystem/export-volume-project/releases/download/v2.2.16/slicer_repr.png"/>

### Import steps:
1. Take volume at path `📂project_dir → 📂dataset_1 → 📂volume → 📜CTChest.nrrd`
2. Take annotations at path `📂project_dir → 📂dataset_1 → 📂mask → 📂CTChest.nrrd → 📜86a6bd27d358440fb97783f5fc7fec57.nrrd` (for example)
3.  Load this files into 3D Slicer
4.  Then select Volume Rendering and enable visibility for each desired volume. You can also customize presets in the Display menu to adjust its visibility.

<video width="100%" src="https://github.com/supervisely-ecosystem/export-volume-project/assets/57998637/106ce8d6-db50-4426-a008-6e391237713a" controls="controls"></video>
