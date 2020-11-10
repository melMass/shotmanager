import bpy

from bpy.types import Panel, Menu
from bpy.props import IntProperty, EnumProperty, BoolProperty, FloatProperty, StringProperty

from ..properties import vsm_props
from ..operators import tracks

import shotmanager.config as config


######
# Video Shot Manager main panel #
######


class UAS_PT_VideoShotManager(Panel):
    bl_label = "UAS Video Shot Manager"
    bl_idname = "UAS_PT_Video_Shot_Manager"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "UAS Video Shot Man"

    def draw_header(self, context):
        props = context.scene.UAS_shot_manager_props
        layout = self.layout
        layout.emboss = "NONE"

        row = layout.row(align=True)

        # if context.window_manager.UAS_video_shot_manager_displayAbout:
        #     row.alert = True
        # else:
        #     row.alert = False

        icon = config.icons_col["General_Ubisoft_32"]
        row.operator("uas_shot_manager.about", text="", icon_value=icon.icon_id)

    def draw_header_preset(self, context):
        layout = self.layout
        layout.emboss = "NONE"

        row = layout.row(align=True)

        row.operator("utils.launchrender", text="", icon="RENDER_STILL").renderMode = "STILL"
        row.operator("utils.launchrender", text="", icon="RENDER_ANIMATION").renderMode = "ANIMATION"

        #    row.operator("render.opengl", text="", icon='IMAGE_DATA')
        #   row.operator("render.opengl", text="", icon='RENDER_ANIMATION').animation = True
        #    row.operator("screen.screen_full_area", text ="", icon = 'FULLSCREEN_ENTER').use_hide_panels=False

        row.separator(factor=2)
        icon = config.icons_col["General_Explorer_32"]
        row.operator("uas_shot_manager.open_explorer", text="", icon_value=icon.icon_id).path = bpy.path.abspath(
            bpy.data.filepath
        )

        row.separator(factor=2)
        row.menu("UAS_MT_Video_Shot_Manager_prefs_mainmenu", icon="PREFERENCES", text="")

        row.separator(factor=3)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        vsm_props = scene.UAS_vsm_props

        row = layout.row()

        ################
        # tracks

        row = layout.row()
        row.alert = True
        row.label(text=" !!! EXPERIMENTAL !!!" + ("  Debug  " if config.uasDebug else ""))

        row = layout.row()  # just to give some space...
        vseFirstFrame = scene.frame_start
        if vseFirstFrame != 0:
            row.alert = True
        row.label(text="First Frame: " + str(vseFirstFrame))

        row = layout.row()
        row.operator("uas_video_shot_manager.frame_all_clips")

        row = layout.row(align=False)
        subRow = row.row(align=False)
        subRow.prop(scene, "use_preview_range", text="")
        subRow = row.row(align=True)
        if scene.use_preview_range:
            # row.use_property_split = False
            subRow.operator("uas_utils.get_current_frame_for_time_range", text="", icon="TRIA_UP_BAR").opArgs = (
                "{'frame_preview_start': " + str(scene.frame_current) + "}"
            )
            subRow.prop(scene, "frame_preview_start", text="Start")
            subRow.operator("uas_video_shot_manager.frame_time_range", text="", icon="CENTER_ONLY")
            subRow.prop(scene, "frame_preview_end", text="End")
            subRow.operator("uas_utils.get_current_frame_for_time_range", text="", icon="TRIA_UP_BAR").opArgs = (
                "{'frame_preview_end': " + str(scene.frame_current) + "}"
            )
        else:
            subRow.operator("uas_utils.get_current_frame_for_time_range", text="", icon="TRIA_UP_BAR").opArgs = (
                "{'frame_start': " + str(scene.frame_current) + "}"
            )
            subRow.prop(scene, "frame_start", text="Start")
            subRow.operator("uas_video_shot_manager.frame_time_range", text="", icon="CENTER_ONLY")
            subRow.prop(scene, "frame_end", text="End")
            subRow.operator("uas_utils.get_current_frame_for_time_range", text="", icon="TRIA_UP_BAR").opArgs = (
                "{'frame_end': " + str(scene.frame_current) + "}"
            )

        layout.separator()

        row = layout.row()
        row.label(text="Tracks")

        row.prop(vsm_props, "numTracks")
        row.operator("uas_video_shot_manager.update_tracks_list", text="", icon="FILE_REFRESH")
        subRow = row.row(align=True)
        subRow.operator("uas_video_shot_manager.clear_all")
        subRow.menu("UAS_MT_Video_Shot_Manager_clear_menu", icon="TRIA_RIGHT", text="")

        box = layout.box()
        row = box.row()
        templateList = row.template_list(
            "UAS_UL_VideoShotManager_Items", "", vsm_props, "tracks", vsm_props, "selected_track_index", rows=6,
        )

        col = row.column(align=True)
        col.operator("uas_video_shot_manager.add_track", icon="ADD", text="")
        col.operator("uas_video_shot_manager.duplicate_track", icon="DUPLICATE", text="")
        col.operator("uas_video_shot_manager.remove_track", icon="REMOVE", text="")
        col.separator()
        col.operator("uas_video_shot_manager.list_action", icon="TRIA_UP", text="").action = "UP"
        col.operator("uas_video_shot_manager.list_action", icon="TRIA_DOWN", text="").action = "DOWN"
        col.separator()
        col.menu("UAS_MT_Video_Shot_Manager_toolsmenu", icon="TOOL_SETTINGS", text="")

    # layout.separator ( factor = 1 )


#############
# tracks
#############


class UAS_UL_VideoShotManager_Items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        global icons_col
        vsm_props = context.scene.UAS_vsm_props
        current_track_index = vsm_props.current_track_index

        row = layout.row()
        row.scale_x = 0.4

        subrow = row.row(align=True)
        subrow.scale_x = 0.5

        if vsm_props.display_color_in_tracklist:
            # row = layout.row(align=True)
            subrow.prop(item, "color", text="")
            subrow.scale_x = 0.45
            subrow.separator(factor=2)

        # row = layout.row(align=True)

        # row.scale_x = 1.0
        # subrow = row.row(align=False)
        subrow.prop(item, "enabled", text=" ")
        subrow.separator(factor=0.9)
        subrow.scale_x = 0.9
        subrow.label(text=str(item.vseTrackIndex) + ": " + item.name)

        # row.scale_x = 0.8
        # row.label(text=item.name)

        # grid_flow.label(text="   " + str(item.vseTrackIndex))

        # c.operator("uas_shot_manager.set_current_shot", icon_value=icon.icon_id, text="").index = index
        # layout.separator(factor=0.1)

        row = layout.row(align=True)
        row.scale_x = 1.0
        grid_flow = row.grid_flow(align=True, columns=4, even_columns=False)
        grid_flow.use_property_split = False
        button_x_factor = 0.6

        row = grid_flow.row(align=True)
        row.scale_x = 2.0
        row.prop(item, "trackType", text="")

        if not "CUSTOM" == item.trackType and not "STANDARD" == item.trackType:

            #     if item.shotManagerScene is None:
            #         grid_flow.alert = True
            #     grid_flow.prop(item, "shotManagerScene", text="")
            #     if item.shotManagerScene is None:
            #         grid_flow.alert = False

            #     if item.shotManagerScene is None or item.sceneTakeName == "":
            #         grid_flow.alert = True
            #     grid_flow.prop(item, "sceneTakeName", text="")
            #     if item.shotManagerScene is None:
            #         grid_flow.alert = False

            grid_flow.scale_x = 1.0
            grid_flow.operator(
                "uas_video_shot_manager.update_vse_track", text="", icon="FILE_REFRESH"
            ).trackName = item.name

            grid_flow.operator(
                "uas_video_shot_manager.go_to_specified_scene", text="", icon="SCENE_DATA"
            ).trackName = item.name
            grid_flow.scale_x = 1.8


# ##################
# # track properties
# ##################


class UAS_PT_VideoShotManager_TrackProperties(Panel):
    bl_label = " "  # "Current Track Properties" # keep the space !!
    bl_idname = "UAS_PT_Video_Shot_Manager_TrackProperties"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "UAS Video Shot Man"
    bl_parent_id = "UAS_PT_Video_Shot_Manager"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        vsm_props = context.scene.UAS_vsm_props
        track = vsm_props.getTrack(vsm_props.selected_track_index)
        val = track

        return val

    def draw_header(self, context):
        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

        row.label(text="Selected Track Properties")

    def draw(self, context):
        scene = context.scene
        vsm_props = scene.UAS_vsm_props

        track = vsm_props.getTrack(vsm_props.selected_track_index)

        layout = self.layout

        if track is not None:
            box = layout.box()

            # name and color
            row = box.row()
            row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            grid_flow.prop(track, "name", text="Name")
            #   grid_flow.scale_x = 0.7
            grid_flow.prop(track, "color", text="")
            #   grid_flow.scale_x = 1.0
            grid_flow.prop(vsm_props, "display_color_in_tracklist", text="")
            row.separator(factor=0.5)  # prevents stange look when panel is narrow

            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            grid_flow.prop(track, "trackType")

            row = box.row()
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            if "CUSTOM" == track.trackType:
                layout.separator()
                row = layout.row()
                row.operator("uas_video_shot_manager.clear_vse_track")

                pass
            elif "STANDARD" == track.trackType:
                layout.separator()
                row = layout.row()
                row.operator("uas_video_shot_manager.clear_vse_track")

                pass
            else:
                if track.shotManagerScene is None:
                    grid_flow.alert = True
                grid_flow.prop(track, "shotManagerScene")
                if track.shotManagerScene is None:
                    grid_flow.alert = False

                if track.shotManagerScene is None:
                    grid_flow.alert = True
                grid_flow.prop(track, "sceneTakeName")
                if track.shotManagerScene is None:
                    grid_flow.alert = False

                layout.separator()
                row = layout.row()
                row.operator("uas_video_shot_manager.clear_vse_track")
                row.operator("uas_video_shot_manager.update_vse_track", icon="FILE_REFRESH").trackName = track.name
                row.operator("uas_video_shot_manager.go_to_specified_scene", icon="SCENE_DATA").trackName = track.name
                layout.separator()


#################
# tools for tracks
#################


class UAS_MT_VideoShotManager_ToolsMenu(Menu):
    bl_idname = "UAS_MT_Video_Shot_Manager_toolsmenu"
    bl_label = "Tracks Tools"
    bl_description = "Tracks Tools"

    def draw(self, context):

        # Copy menu entries[ ---
        layout = self.layout
        row = layout.row(align=True)

        # row.label(text="Tools for Tracks:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator(
            "uas_video_shot_manager.remove_multiple_tracks", text="   Remove Disabled Tracks"
        ).action = "DISABLED"

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_video_shot_manager.remove_multiple_tracks", text="   Remove All Tracks").action = "ALL"

        # import edits
        layout.separator()
        row = layout.row(align=True)
        row.label(text="Import Edits:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uasotio.openfilebrowser", text="   Import Edit From EDL").importMode = "IMPORT_EDIT"

        # export edits
        layout.separator()
        row = layout.row(align=True)
        row.label(text="Export Edits:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator(
            "uas_video_shot_manager.export_markers_edit_as_videos", text="   Export Markers Edit as Videos..."
        )  # , text="Import Edit From EDL")

        layout.separator()
        # wkip debug - to remove:
        if config.uasDebug:
            row = layout.row(align=True)
            row.operator("uas_video_shot_manager.importeditfromotio", text="   Import Edit From EDL - Debug...")

        if config.uasDebug:
            row = layout.row(align=True)
            row.operator(
                "uas_video_shot_manager.importeditfromotio", text="   Import Edit From EDL - Debug + file"
            ).otioFile = (
                # r"Z:\_UAS_Dev\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_ACT01_AQ_200730__FromPremiere.xml"
                r"Z:\EvalSofts\Blender\DevPython_Data\UAS_ShotManager_Data\ImportEDLPremiere\ImportEDLPremiere.xml"
                # r"C:\_UAS_ROOT\RRSpecial\04_ActsPredec\Act01\Exports\RRSpecial_ACT01_AQ_XML_200730\RRSpecial_ACT01_AQ_200730__FromPremiere_to40.xml"  # _to40
            )

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uasotio.openfilebrowser", text="   Parse Edit From EDL").importMode = "PARSE_EDIT"

        # wkip debug - to remove:
        if config.uasDebug:
            row = layout.row(align=True)
            row.operator(
                "uas_video_shot_manager.parseeditfromotio", text="   Import Edit From EDL - Debug"
            ).otioFile = ""

        layout.separator()

        row = layout.row(align=True)
        row.label(text="RRS Specific:")
        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_video_shot_manager.rrs_export_shots_from_edit", text="   RRS Export Shots From Edit")


_classes = (
    UAS_PT_VideoShotManager,
    UAS_PT_VideoShotManager_TrackProperties,
    UAS_UL_VideoShotManager_Items,
    UAS_MT_VideoShotManager_ToolsMenu,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
