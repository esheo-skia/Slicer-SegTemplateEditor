# Label Name Generator

**Label Name Generator** is a 3D Slicer extension to save and apply reusable label groups for Segment Editor.  
Each label is assigned a visually distinct color using golden-ratio hue stepping, allowing for fast and consistent anatomical labeling.

---

## Features

- Define label sets and save them as reusable groups
- Auto-assign visually distinct colors using golden-ratio hue stepping
- Apply saved label groups to any existing segmentation in Segment Editor
- Prevent duplicate label creation and handle confirmation safely
- Groups are persisted in `labels.json` and shared across projects

---

## How to Use

### 1. Enter Labels and Save a Group
- Enter label names line-by-line (e.g., `left renal artery`, `right renal artery`, etc.)
- Input a group name (e.g., `Abdomen vessels`)
- Click `Save label group`

![Step 1 - Save label group](Resources/Screenshots/step1_save_label_group.png)

Labels will be saved with auto-assigned colors. Duplicate or empty lines are ignored. If a group already exists, overwrite confirmation will appear.

---

### 2. Apply Group to Segment Editor
- Select a saved group from the dropdown
- Click `Apply selected group`

A confirmation popup will appear showing the current segmentation name.  
This helps avoid accidental application to the wrong segmentation.

![Step 2 - Confirm segmentation](Resources/Screenshots/step2_confirm_apply.png)

If duplicate labels already exist in the segmentation, you’ll be asked whether to skip them.

---

### 3. View Results in Segment Editor
- Newly applied segments will appear with distinct colors
- Colors are assigned using golden-ratio hue stepping to reduce similarity

![Step 3 - Segment Editor view](Resources/Screenshots/step3_segment_editor_result.png)

Segments are automatically linked to the master volume and displayed with their assigned colors.

---

## Author

**Eunseo Heo (esheo-skia)**  
GitHub: [esheo-skia](https://github.com/esheo-skia)  
Email: esheo.skia@gmail.com

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.


