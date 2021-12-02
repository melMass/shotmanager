# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
UI in BGL for the Interactive Shots Stack overlay tool
"""

import time
from collections import defaultdict

import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from shotmanager.config import config
from shotmanager.utils.utils import clamp, gamma_color, color_is_dark

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


def draw_shots_stack(context):
    ## with dico
    # print(f" suis dans draw_shots_stack: config.gShotsStackInfos: {config.gShotsStackInfos}")

    # _logger.debug_colored("Here 80 - config.gShotsStackInfos Clips len: " + str(len(config.gShotsStackInfos["clips"])))

    if config.gShotsStackInfos is not None:
        # _logger.debug_ext("Redraw in draw_shots_stack", col="PURPLE")
        #    _logger.debug_colored("Here 82")
        for clip in config.gShotsStackInfos["clips"]:
            #        _logger.debug_colored("Here 83")
            clip.draw(context)
            # try:
            #     clip.draw(context)
            # except Exception as e:
            #     # wkip wkip
            #     pass
        #    _logger.debug_colored("Here 84")
        if config.gShotsStackInfos["frame_under_mouse"] != -1:
            #       _logger.debug_colored("Here 85")
            blf.color(0, 0.99, 0.99, 0.99, 1)
            blf.size(0, 11, 72)
            blf.position(
                0, config.gShotsStackInfos["prev_mouse_x"] + 4, config.gShotsStackInfos["prev_mouse_y"] + 10, 0
            )
            #      _logger.debug_colored("Here 86")
            blf.draw(0, str(config.gShotsStackInfos["frame_under_mouse"]))
    #      _logger.debug_colored("Here 87")


def clamp_to_region(x, y, region):
    l_x, l_y = region.view2d.region_to_view(0, 0)
    h_x, h_y = region.view2d.region_to_view(region.width - 1, region.height - 1)
    return clamp(x, l_x, h_x), clamp(y, l_y, h_y)


class Image2D:
    def __init__(self, position, width, height):
        import os

        # IMAGE_NAME = "Untitled"
        IMAGE_NAME = os.path.join(os.path.dirname(__file__), "../../icons/ShotMan_EnabledCurrentCam.png")

        # image = bpy.types.Image()
        # # image.file_format = 'PNG'
        # image.filepath = IMAGE_NAME

        # self._image = bpy.data.images[image]
        self._image = bpy.data.images.load(IMAGE_NAME)
        self._shader = gpu.shader.from_builtin("2D_IMAGE")

        x1, y1 = position.x, position.y
        x2, y2 = position.x + width, position.y
        x3, y3 = position.x, position.y + height
        x4, y4 = position.x + width, position.y + height

        self._position = position
        self._vertices = ((x1, y1), (x2, y2), (x4, y4), (x3, y3))
        # print(f"vertices: {self._vertices}")
        # self._vertices = ((100, 100), (200, 100), (200, 200), (100, 200))
        #    self._verticesSquare = ((0, 0), (0, 1), (1, 1), (0, 1))

        # origin is bottom left of the screen
        # self._vertices = ((bottom_left.x, bottom_left.y), (bottom_right.x, bottom_right.y), (top_right.x, top_right.y), (top_left.x, top_left.y))

        if self._image.gl_load():
            raise Exception()

    def draw(self, region=None):
        bgl.glActiveTexture(bgl.GL_TEXTURE0)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, self._image.bindcode)

        transformed_vertices = self._vertices
        if region:
            transformed_vertices = [
                region.view2d.view_to_region(*clamp_to_region(x, y, region), clip=True) for x, y in transformed_vertices
            ]

        verticesSquare = (
            (transformed_vertices[0][0], transformed_vertices[0][1],),
            (
                transformed_vertices[0][0] + transformed_vertices[3][1] - transformed_vertices[0][1],
                transformed_vertices[0][1],
            ),
            (
                transformed_vertices[0][0] + transformed_vertices[3][1] - transformed_vertices[0][1],
                transformed_vertices[3][1],
            ),
            (transformed_vertices[0][0], transformed_vertices[3][1],),
        )

        batch = batch_for_shader(
            self._shader, "TRI_FAN", {"pos": verticesSquare, "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),},
        )
        self._shader.bind()
        self._shader.uniform_int("image", 0)
        batch.draw(self._shader)


class Mesh2D:
    def __init__(self, vertices=None, indices=None, texcoords=None):
        self._vertices = list() if vertices is None else vertices
        self._indices = list() if indices is None else indices
        self._texcoords = list() if texcoords is None else texcoords
        self._linewidth = 1

    @property
    def vertices(self):
        return list(self._vertices)

    @property
    def indices(self):
        return list(self._indices)

    @property
    def texcoords(self):
        return list(self._texcoords)

    @property
    def linewidth(self):
        return self._linewidth

    @linewidth.setter
    def linewidth(self, value):
        self._linewidth = max(1, value)

    def draw(self, shader, region=None, draw_types="TRIS", cap_lines=False):
        transformed_vertices = self._vertices
        if region:
            transformed_vertices = [
                region.view2d.view_to_region(*clamp_to_region(x, y, region), clip=True) for x, y in transformed_vertices
            ]

        if "TRIS" == draw_types:
            batch = batch_for_shader(shader, draw_types, {"pos": transformed_vertices}, indices=self._indices)
            batch.draw(shader)
        elif "LINES":
            # draw lines and points fo the caps
            batch = batch_for_shader(shader, draw_types, {"pos": transformed_vertices}, indices=self._indices)
            bgl.glLineWidth(self._linewidth)
            batch.draw(shader)
            if cap_lines:
                batch = batch_for_shader(shader, draw_types, {"pos": transformed_vertices})
                bgl.glPointSize(self._linewidth)
                batch.draw(shader)
        elif "POINTS":
            # wkip here draw points for rounded line caps
            batch = batch_for_shader(shader, "POINTS", {"pos": transformed_vertices})
            bgl.glPointSize(self._linewidth)
            batch.draw(shader)


def build_rectangle_mesh(position, width, height, as_lines=False):
    """

    :param position:
    :param width:
    :param height:
    :param region: if region is specified this will transform the vertices into the region's view. This allow for pan and zoom support
    :return:
    """
    x1, y1 = position.x, position.y
    x2, y2 = position.x + width, position.y
    x3, y3 = position.x, position.y + height
    x4, y4 = position.x + width, position.y + height

    vertices = ((x1, y1), (x2, y2), (x3, y3), (x4, y4))
    if as_lines:
        indices = ((0, 1), (0, 2), (2, 3), (1, 3))
    else:
        indices = ((0, 1, 2), (2, 1, 3))

    return Mesh2D(vertices, indices)


LANE_HEIGHT = 18


def get_lane_origin_y(lane):
    return -LANE_HEIGHT * lane - 39  # an offset to put it under timeline ruler.


class BL_UI_ShotClip:
    def __init__(self, lane, shot_index):
        """
        shot_index is the index of the shot in the whole take list
        """
        self.height = LANE_HEIGHT
        self.width = 0
        self.lane = lane
        self._highlight = False
        self.clip_mesh = None
        self.contour_mesh = None
        self.contourCurrent_mesh = None
        self.camIcon = None
        self.start_interaction_mesh = None
        self.end_interaction_mesh = None
        self.origin = None

        self.color_currentShot_border = (0.92, 0.55, 0.18, 0.99)
        self.color_currentShot_border_mix = (0.94, 0.3, 0.1, 0.99)

        self._shot_index = shot_index
        self._name_color_light = (0.9, 0.9, 0.9, 1)
        self._name_color_dark = (0.12, 0.12, 0.12, 1)
        self._name_color_disabled = (0.6, 0.6, 0.6, 1)

        self._shot_color = (0.8, 0.3, 0.3, 1.0)
        self._shot_color_disabled = (0.23, 0.23, 0.23, 1)

        # self.color_selectedShot_border = (0.9, 0.9, 0.2, 0.99)
        #    self.color_selectedShot_border = (0.2, 0.2, 0.2, 0.99)  # dark gray
        self.color_selectedShot_border = (0.95, 0.95, 0.95, 0.9)  # white

        # self.update()

    def update(self):
        props = bpy.context.scene.UAS_shot_manager_props
        shots = props.get_shots()
        shot = shots[self._shot_index]

        self.width = shot.end - shot.start + 1
        self.origin = Vector([shot.start, get_lane_origin_y(self.lane)])
        self.clip_mesh = build_rectangle_mesh(self.origin, self.width, self.height)
        self.start_interaction_mesh = build_rectangle_mesh(self.origin, 1, self.height)
        self.end_interaction_mesh = build_rectangle_mesh(self.origin + Vector([self.width - 1, 0]), 1, self.height)
        self.contour_mesh = build_rectangle_mesh(self.origin, self.width, self.height, True)
        self.contourCurrent_mesh = build_rectangle_mesh(self.origin, self.width, self.height, True)
        # self.contourCurrent_mesh = build_rectangle_mesh(
        #     Vector([self.origin.x - 1, self.origin.y - 1]), self.width + 2, self.height + 2, True
        # )
        self.camIcon = Image2D(self.origin, self.width, self.height)

    @property
    def shot_index(self):
        return self._shot_index

    @shot_index.setter
    def shot_index(self, value):
        self._shot_index = value

    @property
    def shot_color(self):
        return self._shot_color

    @shot_color.setter
    def shot_color(self, value):
        self._shot_color = (value[0], value[1], value[2], 0.5)

    @property
    def highlight(self):
        return self._highlight

    @highlight.setter
    def highlight(self, value: bool):
        self._highlight = value

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props
        shots = props.get_shots()
        shot = shots[self._shot_index]

        bgl.glEnable(bgl.GL_BLEND)
        UNIFORM_SHADER_2D.bind()

        self.shot_color = shot.color
        color = gamma_color(self.shot_color)

        if not shot.enabled:
            color = (0.15, 0.15, 0.15, 0.5)

        if self.highlight:
            color = (0.9, 0.9, 0.9, 0.5)
        UNIFORM_SHADER_2D.uniform_float("color", color)
        self.clip_mesh.draw(UNIFORM_SHADER_2D, context.region)

        self.start_interaction_mesh.draw(UNIFORM_SHADER_2D, context.region)
        self.end_interaction_mesh.draw(UNIFORM_SHADER_2D, context.region)

        # current_shot = props.getCurrentShot()
        # selected_shot = props.getSelectedShot()
        current_shot_ind = props.getCurrentShotIndex()
        selected_shot_ind = props.getSelectedShotIndex()

        # current shot
        # if current_shot != -1 and self.name == current_shot.name:
        if self.shot_index == current_shot_ind:
            UNIFORM_SHADER_2D.uniform_float("color", self.color_currentShot_border)
            self.contourCurrent_mesh.linewidth = 4 if current_shot_ind == selected_shot_ind else 2
            self.contourCurrent_mesh.draw(UNIFORM_SHADER_2D, context.region, "LINES")

        # selected shot
        # if current_shot != -1 and self.name == selected_shot.name:
        if self.shot_index == selected_shot_ind:
            UNIFORM_SHADER_2D.uniform_float("color", self.color_selectedShot_border)
            self.contour_mesh.linewidth = 1 if current_shot_ind == selected_shot_ind else 2
            self.contour_mesh.draw(UNIFORM_SHADER_2D, context.region, "LINES")

        # draw a camera icon on the current shot
        # TODO finish and clean
        #   self.camIcon.draw(context.region)

        bgl.glDisable(bgl.GL_BLEND)

        if shot.enabled:
            if color_is_dark(color, 0.4):
                blf.color(0, *self._name_color_light)
            else:
                blf.color(0, *self._name_color_dark)
        else:
            blf.color(0, *self._name_color_disabled)

        blf.size(0, 11, 72)
        blf.position(0, *context.region.view2d.view_to_region(self.origin.x + 1.3, self.origin.y + 5), 0)
        blf.draw(0, shot.name)

    def get_handle(self, x, y):
        """
        Return the handle of the clip the mouse is on: -1 for start, 0 for move, 1 for end. None otherwise
        :param x:
        :param y:
        :return:
        """
        props = bpy.context.scene.UAS_shot_manager_props
        shots = props.get_shots()
        shot = shots[self._shot_index]

        if shot.start <= x < shot.end + 1 and self.origin.y <= y < self.origin.y + self.height:
            # Test order is important for the case of start and end are the same. We want to prioritize moving the end.
            if shot.end <= x < shot.end + 1:
                return 1
            elif shot.start <= x < shot.start + 1:
                return -1
            else:
                return 0

        return None

    ### #TODO: wkip undo doesn't work here !!!
    def handle_mouse_interaction(self, region, mouse_disp):
        """
        region: if region == -1:    left clip handle (start)
                if region == 1:     right lip handle (end)
        """
        # from shotmanager.properties.shot import UAS_ShotManager_Shot

        #  bpy.ops.ed.undo_push(message=f"Set Shot Start...")

        props = bpy.context.scene.UAS_shot_manager_props
        shots = props.get_shots()
        shot = shots[self._shot_index]
        # !! we have to be sure we work on the selected shot !!!
        if region == 1:
            shot.end += mouse_disp
        elif region == -1:
            shot.start += mouse_disp
            # bpy.ops.uas_shot_manager.set_shot_start(newStart=self.start + mouse_disp)
        else:
            # Very important, don't use properties for changing both start and ends. Depending of the amount of displacement duration can change.
            if mouse_disp > 0:
                shot.end += mouse_disp
                shot.start += mouse_disp
            else:
                shot.start += mouse_disp
                shot.end += mouse_disp