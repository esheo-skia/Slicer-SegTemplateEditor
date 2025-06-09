import os
import json
import random
import vtk, qt, ctk, slicer
import colorsys 
import math
from slicer.ScriptedLoadableModule import *


class SegTemplateEditor(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Segmentation Template Editor"
        self.parent.categories = ["Segmentation"]
        self.parent.contributors = ["Eunseo Heo (esheo-skia)"]
        self.parent.helpText = "Save and apply label groups to Segment Editor.\nThis is useful for repetitive anatomical structure labeling tasks."
        self.parent.acknowledgementText = "Developed by Eunseo Heo using 3D Slicer framework."

class SegTemplateEditorWidget(ScriptedLoadableModuleWidget):
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        self.logic = SegTemplateEditorLogic()

        self.labelInput = qt.QPlainTextEdit()
        self.labelInput.setPlaceholderText("Enter labels (one per line)")
        self.layout.addWidget(self.labelInput)

        self.groupNameInput = qt.QLineEdit()
        self.groupNameInput.setPlaceholderText("Enter group name to save")
        self.layout.addWidget(self.groupNameInput)

        self.saveGroupButton = qt.QPushButton("💾 Save label group")
        self.layout.addWidget(self.saveGroupButton)

        self.autoSelectCheckBox = qt.QCheckBox("Auto-select saved group")
        self.autoSelectCheckBox.setChecked(True)
        self.layout.addWidget(self.autoSelectCheckBox)

        self.autoApplyCheckBox = qt.QCheckBox("Auto-apply group to Segment Editor when selected")
        self.autoApplyCheckBox.setChecked(False)
        self.layout.addWidget(self.autoApplyCheckBox)

        self.groupSelector = qt.QComboBox()
        self.groupSelector.addItem("Select a group")
        self.layout.addWidget(self.groupSelector)

        self.applySelectedGroupButton = qt.QPushButton("🟩 Apply selected group")
        self.layout.addWidget(self.applySelectedGroupButton)

        self.deleteGroupButton = qt.QPushButton("🗑 Delete selected group")
        self.layout.addWidget(self.deleteGroupButton)

        self.saveGroupButton.connect('clicked(bool)', self.onSaveGroup)
        self.groupSelector.currentIndexChanged.connect(self.onGroupSelected)
        self.applySelectedGroupButton.connect('clicked(bool)', self.onApplySelectedGroup)
        self.deleteGroupButton.connect('clicked(bool)', self.onDeleteGroup)

        self.refreshGroupList()

    def refreshGroupList(self):
        self.groupSelector.blockSignals(True)
        self.groupSelector.clear()
        self.groupSelector.addItem("Select a group")
        groups = self.logic.getSavedGroups()
        self.groupSelector.addItems(groups)
        self.groupSelector.setCurrentIndex(0)
        self.groupSelector.blockSignals(False)

    def onSaveGroup(self):
        groupName = self.groupNameInput.text.strip()
        if not groupName:
            slicer.util.errorDisplay("Please enter a group name.")
            return

        text = self.labelInput.toPlainText()
        labelList = [line.strip() for line in text.splitlines() if line.strip()]
        if not labelList:
            slicer.util.errorDisplay("Label list is empty.")
            return

        existingGroups = self.logic.getSavedGroups()
        if groupName in existingGroups:
            result = qt.QMessageBox.question(
                slicer.util.mainWindow(),
                "Overwrite group?",
                f"Group '{groupName}' already exists.\nDo you want to overwrite it?",
                qt.QMessageBox.Yes | qt.QMessageBox.No
            )
            if result != qt.QMessageBox.Yes:
                return

        # ✅ Generate visually distinct group-based color mapping
        labelColorMap = self.logic.generateGroupwiseColors(labelList)

        self.logic.saveLabelGroup(groupName, labelColorMap)
        slicer.util.infoDisplay(f"Group '{groupName}' has been saved.")
        self.refreshGroupList()

        if self.autoSelectCheckBox.isChecked():
            index = self.groupSelector.findText(groupName)
            if index != -1:
                self.groupSelector.setCurrentIndex(index)

    def onGroupSelected(self):
        groupName = self.groupSelector.currentText
        if not groupName or groupName == "Select a group":
            return

        labelColorMap = self.logic.loadLabelGroupWithColors(groupName)
        self.labelInput.setPlainText("\n".join(labelColorMap.keys()))

        if self.autoApplyCheckBox.isChecked():
            self.onApplySelectedGroup()

    def onApplySelectedGroup(self):
        groupName = self.groupSelector.currentText
        if not groupName or groupName == "Select a group":
            slicer.util.errorDisplay("Please select a group to apply.")
            return

        labelColorMap = self.logic.loadLabelGroupWithColors(groupName)
        if not labelColorMap:
            slicer.util.errorDisplay("Cannot load selected group.")
            return

        # ✅ Ensure volume is loaded
        volumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
        if not volumeNode:
            slicer.util.errorDisplay("Please load a volume before applying the label group.")
            return

        # ✅ Get or create SegmentEditorNode
        segmentEditorNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentEditorNode")
        if not segmentEditorNode:
            segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")

        # ✅ Link to Segment Editor widget (for UI sync)
        segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
        segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)

        # ✅ Get or assign segmentation node
        segmentationNode = segmentEditorNode.GetSegmentationNode()
        if not segmentationNode:
            segmentationNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
            if not segmentationNode:
                slicer.util.errorDisplay("Please create or select a segmentation in the Segment Editor.")
                return
            segmentEditorNode.SetAndObserveSegmentationNode(segmentationNode)
            segmentEditorWidget.setSegmentationNode(segmentationNode)

        # ✅ 확인 메시지 띄우기
        currentSegmentationName = segmentationNode.GetName()
        result = qt.QMessageBox.question(
            slicer.util.mainWindow(),
            "Confirm Segmentation",
            f"The current segmentation selected in Segment Editor is:\n\n'{currentSegmentationName}'\n\nDo you want to apply the label group to this segmentation?",
            qt.QMessageBox.Yes | qt.QMessageBox.No
        )
        if result != qt.QMessageBox.Yes:
            return

        # ✅ Connect master volume if needed
        if not segmentEditorNode.GetMasterVolumeNode():
            segmentEditorNode.SetAndObserveMasterVolumeNode(volumeNode)

        # ✅ Ensure display node
        if not segmentationNode.GetDisplayNode():
            displayNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationDisplayNode")
            slicer.mrmlScene.AddNode(displayNode)
            segmentationNode.SetAndObserveDisplayNodeID(displayNode.GetID())

        existingLabels = {
            segmentationNode.GetSegmentation().GetNthSegment(i).GetName()
            for i in range(segmentationNode.GetSegmentation().GetNumberOfSegments())
        }
        duplicateLabels = [label for label in labelColorMap if label in existingLabels]

        if duplicateLabels:
            result = qt.QMessageBox.question(
                slicer.util.mainWindow(),
                "Duplicate labels",
                f"These labels already exist: {', '.join(duplicateLabels)}\nDo you want to apply only the non-duplicate labels?",
                qt.QMessageBox.Yes | qt.QMessageBox.No
            )
            if result != qt.QMessageBox.Yes:
                return

        # ✅ Apply non-duplicate segments
        for label, color in labelColorMap.items():
            if label in duplicateLabels:
                continue
            self.logic.addSegment(segmentationNode, label, color)

        slicer.util.infoDisplay(f"Group '{groupName}' applied to Segment Editor.")


    def onDeleteGroup(self):
        groupName = self.groupSelector.currentText
        if not groupName or groupName == "Select a group":
            return
        confirm = qt.QMessageBox.question(
            slicer.util.mainWindow(),
            "Delete group",
            f"Are you sure you want to delete group '{groupName}'?",
            qt.QMessageBox.Yes | qt.QMessageBox.No
        )
        if confirm == qt.QMessageBox.Yes:
            if self.logic.deleteLabelGroup(groupName):
                slicer.util.infoDisplay(f"Group '{groupName}' deleted.")
                self.refreshGroupList()


class SegTemplateEditorLogic(ScriptedLoadableModuleLogic):
    def __init__(self):
        super().__init__()
        self.lastColor = None

    def getJsonPath(self):
        return os.path.join(os.path.dirname(__file__), "labels.json")

    def saveLabelGroup(self, groupName, labelColorMap):
        path = self.getJsonPath()
        allGroups = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                allGroups = json.load(f)
        allGroups[groupName] = labelColorMap
        with open(path, "w", encoding="utf-8") as f:
            json.dump(allGroups, f, indent=2)

    def loadLabelGroupWithColors(self, groupName):
        path = self.getJsonPath()
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            allGroups = json.load(f)
        return allGroups.get(groupName, {})

    def getSavedGroups(self):
        path = self.getJsonPath()
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            allGroups = json.load(f)
        return list(allGroups.keys())

    def deleteLabelGroup(self, groupName):
        path = self.getJsonPath()
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as f:
            allGroups = json.load(f)
        if groupName not in allGroups:
            return False
        del allGroups[groupName]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(allGroups, f, indent=2)
        return True  # ✅ with 블록 밖으로 이동

    def addSegment(self, segmentationNode, labelName, color):
        cleanLabel = labelName.strip()
        if not cleanLabel:
            return  # 빈 라벨은 무시

        segmentation = segmentationNode.GetSegmentation()
        if segmentation.GetSegmentIdBySegmentName(cleanLabel):
            return  # 중복도 무시

        if not isinstance(color, list) or len(color) != 3:
            color = [random.random(), random.random(), random.random()]

        segmentId = segmentation.AddEmptySegment(cleanLabel)
        segment = segmentation.GetSegment(segmentId)
        segment.SetName(cleanLabel)
        segment.SetColor(*[float(c) for c in color])
        segment.Modified()

    def generateDistinctColor(self, index, totalCount):
        """
        Generate a visually distinct color using golden ratio hue stepping,
        with added logic to avoid consecutive similar colors in RGB space.
        """
        golden_ratio = 0.61803398875
        max_attempts = 10

        for attempt in range(max_attempts):
            hue = ((index + attempt) * golden_ratio) % 1.0
            saturation = 0.75
            lightness = 0.5
            r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)

            if self.lastColor:
                dist = math.sqrt(sum((a - b) ** 2 for a, b in zip((r, g, b), self.lastColor)))
                if dist < 0.25:
                    continue  # 색이 너무 비슷함 → 다른 hue 시도

            self.lastColor = (r, g, b)
            return [r, g, b]

        # fallback
        return [r, g, b]
    
    def generateGroupwiseColors(self, labelList):
        colorMap = {}
        usedColors = []
        golden_ratio = 0.61803398875
        for i, label in enumerate(labelList):
            hue = (i * golden_ratio) % 1.0
            saturation = 0.75
            lightness = 0.5
            r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)

            if usedColors:
                dist = math.sqrt(sum((a - b) ** 2 for a, b in zip((r, g, b), usedColors[-1])))
                if dist < 0.25:
                    hue = (hue + 0.1) % 1.0
                    r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)

            usedColors.append((r, g, b))
            colorMap[label] = [r, g, b]
        return colorMap