set(MODULE_NAME SegTemplateEditor)
set(MODULE_TITLE "Segmentation Template Editor")

set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
)

set(MODULE_PYTHON_RESOURCES
)

set(MODULE_UI_RESOURCE_FILES
)

set(MODULE_TARGET_LIBRARIES
)

set(MODULE_INCLUDE_DIRECTORIES
)

slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  TITLE ${MODULE_TITLE}
  SCRIPTS "${MODULE_PYTHON_SCRIPTS}"
  RESOURCES "${MODULE_PYTHON_RESOURCES}"
  UI_RESOURCES "${MODULE_UI_RESOURCE_FILES}"
  WITH_GENERIC_TESTS
)
