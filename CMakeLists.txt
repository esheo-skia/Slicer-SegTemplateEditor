cmake_minimum_required(VERSION 3.13.4)

project(SegTemplateEditor)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/esheo-skia/Slicer-SegTemplateEditor")
set(EXTENSION_CATEGORY "Segmentation")
set(EXTENSION_CONTRIBUTORS "EunSeo Heo (Independent Developer)")
set(EXTENSION_DESCRIPTION "Extension for creating and managing reusable segmentation templates with predefined segment names and colors")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/esheo-skia/Slicer-SegTemplateEditor/main/Resources/Icons/SegTemplateEditor.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/esheo-skia/Slicer-SegTemplateEditor/main/Resources/Screenshots/step1_save_label_group.png https://raw.githubusercontent.com/esheo-skia/Slicer-SegTemplateEditor/main/Resources/Screenshots/step2_confirm_apply.png https://raw.githubusercontent.com/esheo-skia/Slicer-SegTemplateEditor/main/Resources/Screenshots/step3_segment_editor_result.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(SegTemplateEditor)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
