import bpy
from bpy.types import Operator

#
# Removed and replaced by a property in props
#
# class UAS_ShotManager_LockCamToView(Operator):
#     bl_idname = "uas_shot_manager.lockcamtoview"
#     bl_label = "Lock Cameras to View"
#     bl_description = "Enable view navigation within the camera view"
#     bl_options = {"INTERNAL"}

#     @classmethod
#     def poll(cls, context):
#         props = context.scene.UAS_shot_manager_props
#         val = len(props.getTakes()) and len(props.get_shots())
#         return val

#     def execute(self, context):
#         scene = context.scene
#         props = scene.UAS_shot_manager_props

#         # Can also use area.spaces.active to get the space assoc. with the area
#         for area in context.screen.areas:
#             if area.type == "VIEW_3D":
#                 for space in area.spaces:
#                     if space.type == "VIEW_3D":
#                         space.lock_camera = True

#         return {"FINISHED"}


class UAS_ShotManager_EnableDisableAll(Operator):
    bl_idname = "uas_shot_manager.enabledisableall"
    bl_label = "Enable / Disable All Shots"
    bl_description = "Enable all shots,\nClick + Ctrl: Disable all shots,\nClick + Shift: Invert shots state"
    bl_options = {"INTERNAL", "REGISTER", "UNDO"}

    def invoke(self, context, event):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        enableMode = "ENABLEALL"
        if event.shift:
            enableMode = "INVERT"
        elif event.ctrl:
            enableMode = "DISABLEALL"

        selectedShotInd = props.getSelectedShotIndex()
        shotsList = props.getShotsList()
        for shot in shotsList:
            if "ENABLEALL" == enableMode:
                shot.enabled = True
            elif "DISABLEALL" == enableMode:
                shot.enabled = False
            elif "INVERT" == enableMode:
                shot.enabled = not shot.enabled

        props.setSelectedShotByIndex(selectedShotInd)

        return {"FINISHED"}


class UAS_ShotManager_SceneRangeFromShot(Operator):
    bl_idname = "uas_shot_manager.scenerangefromshot"
    bl_label = "Scene Range From Shot"
    bl_description = "Set scene time range with CURRENT shot range"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        currentShot = props.getCurrentShot()
        scene.use_preview_range = True

        scene.frame_preview_start = currentShot.start
        scene.frame_preview_end = currentShot.end

        return {"FINISHED"}


# # operator here must be a duplicate of UAS_ShotManager_SceneRangeFromShot is order to use a different description
# class UAS_ShotManager_SceneRangeFromEnabledShots(Operator):
#     bl_idname = "uas_shot_manager.scenerangefromenabledshots"
#     bl_label = "Scene Range From Enabled Shot"
#     bl_description = "Set scene time range with enabled shots range"
#     bl_options = {"INTERNAL"}

#     def execute(self, context):
#         scene = context.scene
#         props = scene.UAS_shot_manager_props

#         shotList = props.getShotsList(ignoreDisabled=True)

#         if len(shotList):
#             scene.use_preview_range = True

#             scene.frame_preview_start = shotList[0].start
#             scene.frame_preview_end = shotList[len(shotList) - 1].end

#         return {"FINISHED"}


# operator here must be a duplicate of UAS_ShotManager_SceneRangeFromShot is order to use a different description
class UAS_ShotManager_SceneRangeFrom3DEdit(Operator):
    bl_idname = "uas_shot_manager.scenerangefrom3dedit"
    bl_label = "Scene Range From 3D Edit"
    bl_description = "Set scene time range with the the 3D edit range"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        shotList = props.getShotsList(ignoreDisabled=True)

        if 0 < len(shotList):
            scene.use_preview_range = True
            scene.frame_preview_start = shotList[0].start
            scene.frame_preview_end = shotList[len(shotList) - 1].end

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_EnableDisableAll,
    #   UAS_ShotManager_LockCamToView,
    UAS_ShotManager_SceneRangeFromShot,
    #    UAS_ShotManager_SceneRangeFromEnabledShots,
    UAS_ShotManager_SceneRangeFrom3DEdit,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)