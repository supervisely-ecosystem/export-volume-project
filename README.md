<div align="center" markdown>

<img src="https://github.com/supervisely-ecosystem/export-volume-project/releases/download/v2.2.16/var_6.jpg">

# Export Volumes with 3D Annotations

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#whats-new">What's new</a> •
  <a href="#how-to-run">How To Run</a> •
  <a href="#how-to-use">How To Use</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/export-volume-project)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/export-volume-project)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/export-volume-project.png)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/export-volume-project.png)](https://supervise.ly)

</div>

## Overview

🔥 All 3D data is exported as `.nrrd` for **compatibility with other popular medical viewers**, so that once downloaded, the volume and masks can be opened in specialized software like [MITK](http://www.mitk.org/) and [3D Slicer](https://www.slicer.org/) without any further action!

You can export as a whole Supervisely project or only as a dataset. To learn more about the format and its structure read [documentation](https://docs.supervise.ly/data-organization/00_ann_format_navi/08_supervisely_format_volume).

Application key points:
- Export annotations in `.json` and `.nrrd` formats
- Export volumes data in `.nrrd` format
- Export Instance segmentation as Mask3D for every non-Mask3D object in `.nrrd` format
- Instance segmentation masks are duplicated with human-readable file names for convenience
- Export Semantic segmentation as a single Mask3D for all objects in `.nrrd` format
- Semantic segmentation generates `class2idx.json` mapping, e.g. `{"lung": 1, "brain": 2}`

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

Version `v2.3.0`
 - 🏷️ new format for storing `Mask3D` geometry as `.nrrd` files in the `mask` directory. To learn more read [this article](https://docs.supervisely.com/data-organization/00_ann_format_navi/08_supervisely_format_volume).
 - ℹ️ Convert closed mesh surfaces `.stl` to Mask3D as `.nrrd` automatically. STL files will be saved in the project interpolation folder, but cannot be re-imported as closed mesh surfaces due to format obsolescence.

# How To Run

1. Add [Export volumes project in Supervisely format](https://ecosystem.supervise.ly/apps/export-volume-project)

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
     │   ├──📂interpolation
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
