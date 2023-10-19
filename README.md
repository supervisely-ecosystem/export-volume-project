<div align="center" markdown>

<img src="https://github.com/supervisely-ecosystem/export-volume-project/releases/download/v2.2.16/var_6.jpg">

# Export Volumes with 3D Annotations

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
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
- Export annotations in `.json` and `.stl` formats
- Export volumes data in `.nrrd` format
- Convert closed mesh surfaces `.stl` to 3D masks as `.nrrd`
- Export Instance segmentation as 3D masks for every object in `.nrrd` format
- Instance segmentation masks are duplicated with human-readable file names for convenience
- Export Semantic segmentation as a single mask for all objects in `.nrrd` format
- Semantic segmentation generates `class2idx.json` mapping, e.g. `{"lung": 1, "brain": 2}` 


<div>
  <table>
    <tr style="width:100%">
      <td>
        <b>Volumes Data in Supervisely format</b>
        <img src="https://github.com/supervisely-ecosystem/export-volume-project/assets/57998637/ed1951e5-65a5-45ea-81ce-9a642f2468e6?raw-true"/>
      </td>
      <td>
        <b>Exported .stl with 3D segmentation mask</b>
        <img src="https://github.com/supervisely-ecosystem/export-volume-project/assets/57998637/26c862f9-a6a9-4378-937b-8d562fccc7f9?raw=true"/>
      </td>
    </tr>
  </table>
</div>

# How To Run

1. Add [Export volumes project in Supervisely format](https://ecosystem.supervise.ly/apps/export-volume-project)

   <img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/export-volume-project" src="https://i.imgur.com/DnAVFlZ.png" width="450px" style='padding-bottom: 20px'/>

2. Run the app from the context menu of **Volume Project** or **Volumes Dataset** -> `Download via app` -> `Export Supervisely volume project in Supervisely format`

   <img width="1250" alt="2023-06-13_18-44-30" src="https://github.com/supervisely-ecosystem/export-volume-project/assets/57998637/563084d9-e8d5-485f-a90e-dcc5eb921175">

3. Define export settings in the modal window and press the **Run** button

   <img width="405" alt="2023-06-13_18-46-45" src="https://github.com/supervisely-ecosystem/export-volume-project/assets/57998637/cdc63faf-24ba-44da-8daa-4a69ec7700d1">


# How To Use

1. Wait for the app to process your data, once done, a link for the download will become available
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
     │   │   ├──📜CTACardio.nrrd.json
     │   │   ├──📜CTChest.nrrd.json
     │   │   └──📜MRHead.nrrd.json
     │   ├──📂interpolation
     │   │   └──📂MRHead.nrrd
     │   │       └──📜9aab4ddf1ddb4af1836006f0f1a3a694.stl
     │   ├──📂mask
     │   │   ├──📂CTACardio.nrrd
     │   │   │   ├──📂human-readable-objects
     │   │   │   │   └──📜lung_object_001.nrrd
     │   │   │   ├──📜629b85fbb57c428aba1ee536a793c1ad.nrrd
     │   │   │   └──📜semantic_segmentation.nrrd
     │   │   ├──📂CTChest.nrrd
     │   │   │   ├──📂human-readable-objects
     │   │   │   │   └──📜lung_object_001.nrrd
     │   │   │   ├──📜86a6bd27d358440fb97783f5fc7fec57.nrrd
     │   │   │   └──📜semantic_segmentation.nrrd
     │   │   └──📂MRHead.nrrd
     │   │       ├──📂human-readable-objects
     │   │       │   └──📜brain_object_001.nrrd
     │   │       ├──📜ca44240c7f27423b942c42848847e69d.nrrd
     │   │       └──📜semantic_segmentation.nrrd
     │   └──📂volume
     │       ├──📜CTACardio.nrrd
     │       ├──📜CTChest.nrrd
     │       └──📜MRHead.nrrd
     ├──📜class2idx.json
     ├──📜key_id_map.json
     └──📜meta.json
```
