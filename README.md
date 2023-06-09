<div align="center" markdown>

<img src="https://user-images.githubusercontent.com/48913536/204284300-a30b77c2-4381-467d-ab95-c993f133241f.png">

# Export Supervisely Volumes

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

Export Supervisely volume project or dataset. You can learn more about the format and its structure by reading [documentation](https://docs.supervise.ly/data-organization/00_ann_format_navi/08_supervisely_format_volume).

Application key points:

- Download annotations in `.json` and `.stl` formats
- Download volumes data in `.nrrd` format
- Convert closed mesh surfaces (`.stl`) to 3d masks (`.nrrd`)
- Save 3d masks for every object (instance segmentation) in `.nrrd` format
- Instance segmentation masks are duplicated with human-readable file names for convenience
- Save all objects masks as a single mask (semantic segmentation) in `.nrrd` format
- Generate `class2idx.json` for semantic segmentation, e.g `{"lung": 1, "brain": 2}`
- All 3d masks (.nrrd) are made for **compatibility with other popular medical viewers**. After downloading, you can open volume and masks in specialized software like [MITK](http://www.mitk.org/) and [3D Slicer](https://www.slicer.org/)

<div>
  <table>
    <tr style="width: 100%">
      <td>
        <b>Volumes Data in Supervisely format</b>
        <img src="https://github.com/supervisely-ecosystem/export-volume-project/releases/download/v1.0.1/interface.gif?raw=true" style="width:150%;"/>
      </td>
      <td>
        <b>Exported .stl with 3d segmentation masks</b>
        <img src="https://github.com/supervisely-ecosystem/export-volume-project/releases/download/v1.0.1/slicer_result.gif?raw=true" style="width:150%;"/>
      </td>
    </tr>
  </table>
</div>

# How To Run

1. Add [Export volumes project in Supervisely format](https://ecosystem.supervise.ly/apps/export-volume-project)

<img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/export-volume-project" src="https://i.imgur.com/DnAVFlZ.png" width="450px" style='padding-bottom: 20px'/>

2. Run the app from the context menu of **Volume Project** or **Volumes Dataset** -> `Download via app` -> `Export Supervisely volume project in Supervisely format`

<img src="https://imgur.com/xGX2kjq.png"/>

3. Define export settings in the modal window and press the **Run** button

<div align="center" markdown>
<img src="https://i.imgur.com/ty0wHZJ.png" width="650"/>
</div>

# How To Use

1. Wait for the app to process your data, once done, a link for download will become available
   <img src="https://imgur.com/9SYRK5n.png"/>

2. The resulting archive will be available for download by link at the `Tasks` page or from `Team Files` by the following path:

- `Team Files`->`Export-Supervisely-volumes-projects`->`<task_id>_<projectId>_<projectName>.tar`
  <img src="https://imgur.com/02KtweO.png"/>

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
