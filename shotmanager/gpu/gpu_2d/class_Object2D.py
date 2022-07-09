# GPLv3 License
#
# Copyright (C) 2020 Ubisoft
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
Useful entities for 2D gpu drawings
"""

import gpu

# from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class Object2D:
    """
    The View coordinate system of the region is a screen coordinate system, in pixels.
    Its origin is at the bottom left corner of the region (not of the area!), y axis pointing toward the top.

    The Region coordinate system of the region is a coordinate system depending on the state of the rulers or scroll bars.
    For dopesheets and timelines the X axis units are the frames and the Y axis units are values. For better commodity we
    are rather using lines, a line is 20 values height when the global UI scale factor is 1.0.
    Its origin is at the bottom left corner of the region (not of the area!), y axis pointing toward the top.

    The origin of the object (its position) is at its bottom left, y pointing topward.

    Class properties:

        posXIsInRegionCS:   If True the position on X axis is in the View coordinate system of the region, posX is then in pixels
                            The position X of the object will NOT change even if the region scale on x is changed (eg: time zoom)

                            If False the position on X axis is in the Region coordinate system, in frames.
                            The position X of the object will change if the region scale on x is changed (eg: time zoom)

                            Use posXIsInRegionCS = True to display a quad with a constant position on x on the screen
                            Use posXIsInRegionCS = False to display a clip that has to stay as a specific frame (a key for eg)

        posX:               The position on the X axis of the object. Its unit is in pixels if posXIsInRegionCS is True, in frames otherwise


        posYIsInRegionCS:   If True the position on Y axis is in the View coordinate system of the region, posY is then in pixels
                            The position Y of the object will NOT change even if the region scale on y is changed (eg: not dependent on lines scale)

                            If False the position on X axis is in the Region coordinate system, in number of lines.
                            The position Y of the object will change if the region scale on y is changed (eg: surface that has to mach a line height)

                            Note that the actual height of a line in pixels depends on the global UI scale factor.
                            Use posYIsInRegionCS = True to display a static quad for example
                            Use posYIsInRegionCS = False to display a clip that has to match a line position

        posY:               The position on the Y axis of the object. Its unit is in pixels if posYIsInRegionCS is True, in lines otherwise


        widthIsInRegionCS:  If True the width is in the View coordinate system of the region, width is then in pixels
                            Width of the object will NOT change even if the region scale on x is changed (eg: time zoom)

                            If False the width is in the Region coordinate system, in frames.
                            Width of the object will change if the region scale on x is changed (eg: time zoom)

                            Use widthIsInRegionCS = True to display a quad with a constant width on screen
                            Use widthIsInRegionCS = False to display a clip that has to match a given amount of frames width

        width:              The width of the object. Its unit is in pixels if widthIsInRegionCS is True, in frames otherwise


        heightIsInRegionCS:   If True the height is in the View coordinate system of the region, height is then in pixels
                            Height of the object will NOT change even if the region scale on y is changed (eg: not dependent on lines scale)

                            If False the height is in the Region coordinate system, in number of lines.
                            Height of the object will change if the region scale on y is changed (eg: surface that has to mach a line height)

                            Note that the actual height of a line in pixels depends on the global UI scale factor.
                            Use heightIsInRegionCS = True to display a static quad for example
                            Use heightIsInRegionCS = False to display a clip that has to match a line height

        height:             The height of the object. Its unit is in pixels if heightIsInRegionCS is True, in lines otherwise

        alignment:          aligment of the object to its origin
                            can be TOP_LEFT, TOP_MID, TOP_RIGHT, MID_RIGHT, BOTTOM_RIGHT, BOTTOM_MID, BOTTOM_LEFT (default), MID_LEFT, MID_MID

        alignmentToRegion: aligment of the object to its parent region
                            can be TOP_LEFT, TOP_MID, TOP_RIGHT, MID_RIGHT, BOTTOM_RIGHT, BOTTOM_MID, BOTTOM_LEFT (default), MID_LEFT, MID_MID

    """

    def __init__(
        self,
        posXIsInRegionCS=True,
        posX=30,
        posYIsInRegionCS=True,
        posY=50,
        widthIsInRegionCS=True,
        width=40,
        heightIsInRegionCS=True,
        height=20,
        alignment="BOTTOM_LEFT",
        alignmentToRegion="BOTTOM_LEFT",
        parent=None,
    ):

        self.posXIsInRegionCS = posXIsInRegionCS
        self.posX = posX
        self.posYIsInRegionCS = posYIsInRegionCS
        self.posY = posY

        self.widthIsInRegionCS = widthIsInRegionCS
        self.width = width
        self.heightIsInRegionCS = heightIsInRegionCS
        self.height = height

        self.alignment = alignment
        self.alignmentToRegion = alignmentToRegion

        self._children = list()
        self.parent = parent
        if self.parent:
            self.parent._children.append(self)

        self._pivot_posX = 0
        self._pivot_posY = 0

    def getPositionInRegion(self):
        return (self._pivot_posX, self._pivot_posY)