<div align="center" markdown>
<img src="https://imgur.com/7IHY0Gs.png">

# Export Supervisely Volumes

<p align="center">
  <a href="#Overview">Overview</a>
  <a href="#How-To-Run">How To Run</a>
  <a href="#How-To-Use">How To Use</a>
</p>



[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/export-volume-project)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/export-volume-project)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/export-volume-project&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/export-volume-project&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/export-volume-project&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview

Export Supervisely volume project or dataset. You can learn more about format and its structure by reading [documentation](https://docs.supervise.ly/data-organization/00_ann_format_navi/08_supervisely_format_volume).


Application key points:
- Download annotations in `.json` and `.stl` formats
- Download volumes data in `.nrrd` format
- Convert closed mesh surfaces (`.stl`) to 3d masks (`.nrrd`)
- Save 3d masks for every object (instance segmentation) in `.nrrd` format
- Instance segmentation masks are duplicated with human readable file names for convenience
- Save all objects masks as single mask (semantic segmentation) in `.nrrd` format
- Generate `class2idx.json` for semantic segmentation, e.g `{"lung": 1, "brain": 2}`
- All 3d masks (.nrrd) are made for **compatibility with other popular medical viewers**. After download you can open volume and masks in specialised software like [MITK](http://www.mitk.org/) and [3D Slicer](https://www.slicer.org/)

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

1. Add  [Export volumes project in supervisely format](https://ecosystem.supervise.ly/apps/export-volume-project)

<img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/export-volume-project" src="https://i.imgur.com/DnAVFlZ.png" width="450px" style='padding-bottom: 20px'/>

2. Run app from the context menu of **Volume Project** or **Volumes Dataset** -> `Download via app` -> `Export Supervisely volume project in supervisely format`

<img src="https://imgur.com/xGX2kjq.png"/>

3. Define export settings in modal window and press the **Run** button

<div align="center" markdown>
<img src="https://i.imgur.com/ty0wHZJ.png" width="650"/>
</div>

# How To Use 

1. Wait for the app to process your data, once done, a link for download will become available
<img src="https://imgur.com/9SYRK5n.png"/>

2. Result archive will be available for download by link at `Tasks` page or from `Team Files` by the following path:


* `Team Files`->`Export-Supervisely-volumes-projects`->`<task_id>_<projectId>_<projectName>.tar`
<img src="https://imgur.com/02KtweO.png"/>

**Output project structure:**
```text
project.tar
├── dataset_1
│   ├── ann
│   │   ├── CTACardio.nrrd.json
│   │   ├── CTChest.nrrd.json
│   │   └── MRHead.nrrd.json
│   ├── interpolation
│   │   └── MRHead.nrrd
│   │       ├── 451e670973a247ac8f49b035dc407f63.stl
│   │       ├── 461c37cdf8ff48a2943dcb989aa752d6.stl
│   │       └── 9aab4ddf1ddb4af1836006f0f1a3a694.stl
│   ├── mask
│   │   ├── CTACardio.nrrd
│   │   │   ├── human-readable-objects
│   │   │   │   └── lung_object_001.nrrd
│   │   │   ├── 603b7dce7c8e412788882545d6814237.nrrd
│   │   │   ├── 629b85fbb57c428aba1ee536a793c1ad.nrrd
│   │   │   └── semantic_segmentation.nrrd
│   │   ├── CTChest.nrrd
│   │   │   ├── human-readable-objects
│   │   │   │   └── lung_object_001.nrrd
│   │   │   ├── 86a6bd27d358440fb97783f5fc7fec57.nrrd
│   │   │   └── semantic_segmentation.nrrd
│   │   └── MRHead.nrrd
│   │       ├── human-readable-objects
│   │       │   ├── brain_object_001.nrrd
│   │       │   ├── brain_object_002.nrrd
│   │       │   ├── brain_object_003.nrrd
│   │       │   ├── brain_object_004.nrrd
│   │       │   ├── brain_object_005.nrrd
│   │       │   └── brain_object_006.nrrd
│   │       ├── 451e670973a247ac8f49b035dc407f63.nrrd
│   │       ├── 461c37cdf8ff48a2943dcb989aa752d6.nrrd
│   │       ├── 4a0747937de44e73b252310ee693c267.nrrd
│   │       ├── 9aab4ddf1ddb4af1836006f0f1a3a694.nrrd
│   │       ├── aa4a036a5376475b946bbea0d8857ff9.nrrd
│   │       ├── ca44240c7f27423b942c42848847e69d.nrrd
│   │       └── semantic_segmentation.nrrd
│   └── volume
│       ├── CTACardio.nrrd
│       ├── CTChest.nrrd
│       └── MRHead.nrrd
├── class2idx.json
├── key_id_map.json
└── meta.json
```
