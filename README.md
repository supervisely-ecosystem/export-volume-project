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
  </table
</div>



# How To Run 

1. Add  [Export volumes project in supervisely format](https://ecosystem.supervise.ly/apps/export-volume-project)

<img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/export-volume-project" src="https://imgur.com/WZFpiDE.png" width="450px" style='padding-bottom: 20px'/>

2. Run app from the context menu of **Volume Project** or **Volumes Dataset** -> `Download via app` -> `Export Supervisely volume project in supervisely format`

<img src="https://imgur.com/xGX2kjq.png"/>

3. Define export settings in modal window and press the **Run** button

<div align="center" markdown>
<img src="https://i.imgur.com/y4MGWUM.png" width="650"/>
</div>

# How To Use 

1. Wait for the app to process your data, once done, a link for download will become available
<img src="https://imgur.com/9SYRK5n.png"/>

2. Result archive will be available for download by link at `Tasks` page or from `Team Files` by the following path:


* `Team Files`->`Export-Supervisely-volumes-projects`->`<task_id>_<projectId>_<projectName>.tar`
<img src="https://imgur.com/02KtweO.png"/>
