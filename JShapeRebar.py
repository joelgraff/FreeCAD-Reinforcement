# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2017 - Amritpal Singh <amrit3701@gmail.com>             *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "JShapeRebar"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

from PySide import QtCore, QtGui
from Rebarfunc import *
from PySide.QtCore import QT_TRANSLATE_NOOP
from RebarDistribution import runRebarDistribution, removeRebarDistribution
from PopUpImage import showPopUpImageDialog
import FreeCAD
import FreeCADGui
import ArchCommands
import os
import sys
import math
import Arch
import Part
import Sketcher

def getpointsOfJShapeRebar(FacePRM, r_cover, l_cover, b_cover, t_cover, hook_length, orientation):
    """ getpointsOfJShapeRebar(FacePRM, RightCover, LeftCover, BottomCover, TopCover, Orientation):
    Return points of the UShape rebar in the form of array for sketch.
    It takes four different orientations input i.e. 'Bottom', 'Top', 'Left', 'Right'.
    """
    _x = FacePRM[1][0]
    _y = FacePRM[1][1]
    _width = FacePRM[0][0]
    _height = FacePRM[0][1]

    arc_radius = (_height - b_cover - t_cover) / 2.0

    if orientation == "Bottom":

        #build the center section
        x1 = _x - _width / 2.0 + l_cover + arc_radius
        y1 = _y - _height / 2.0 + b_cover
        x2 = _x + _width / 2.0 - r_cover - arc_radius
        y2 = y1

        #build the left hook end
        x3 = x1
        y3 = _y + (_height / 2.0) - t_cover
        x4 = x3 + hook_length
        y4 = y3

        #build the right hook end
        x5 = x2
        y5 = y3
        x6 = x5 - hook_length
        y6 = y3

        #build the left semi-circle
        lt_ctr_x = x1
        lt_ctr_y = y1 + arc_radius
        lt_start = math.pi / 2.0
        lt_end = lt_start + math.pi

        #build the right semi-circle
        rt_ctr_x = x2
        rt_ctr_y = lt_ctr_y
        rt_start = 1.5 * math.pi
        rt_end = rt_start + math.pi

    elif orientation == "Top":

        print _y
        print _height
        print t_cover

        print _x
        print _width
        print b_cover

        print arc_radius

        #build the center section
        x1 = _x - _width / 2.0 + l_cover + arc_radius
        y1 = _y + (_height / 2.0) - t_cover
        x2 = _x + _width / 2.0 - r_cover - arc_radius
        y2 = y1

        #build the left hook end
        x3 = x1
        y3 = _y - _height / 2.0 + b_cover
        x4 = x3 + hook_length
        y4 = y3

        #build the right hook end
        x5 = x2
        y5 = y3
        x6 = x5 - hook_length
        y6 = y3

        #build the left semi-circle
        lt_ctr_x = x1
        lt_ctr_y = y1 - arc_radius
        lt_start = math.pi / 2.0
        lt_end = lt_start + math.pi

        #build the right semi-circle
        rt_ctr_x = x2
        rt_ctr_y = lt_ctr_y
        rt_start = 1.5 * math.pi
        rt_end = rt_start + math.pi

    elif orientation == "Left":
        pass

    elif orientation == "Right":
        pass

    return [FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0),\
        FreeCAD.Vector(x3, y3, 0), FreeCAD.Vector(x4, y4, 0),\
        FreeCAD.Vector(x5, y5, 0), FreeCAD.Vector(x6, y6, 0),\
        FreeCAD.Vector(lt_ctr_x, lt_ctr_y, 0), FreeCAD.Vector(lt_start, lt_end, arc_radius),\
        FreeCAD.Vector(rt_ctr_x, rt_ctr_y, 0), FreeCAD.Vector(rt_start, rt_end, arc_radius)]

class _JShapeRebarTaskPanel:
    def __init__(self, Rebar = None):
        self.CustomSpacing = None
        if not Rebar:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            self.SelectedObj = selected_obj.Object
            self.FaceName = selected_obj.SubElementNames[0]
        else:
            self.FaceName = Rebar.Base.Support[0][1][0]
            self.SelectedObj = Rebar.Base.Support[0][0]

        self.form = FreeCADGui.PySideUic.loadUi(os.path.splitext(__file__)[0] + ".ui")
        self.form.setWindowTitle(QtGui.QApplication.translate("RebarAddon", "J-Shape Rebar", None))
        self.form.orientation.addItems(["Bottom", "Top", "Right", "Left"])
        self.form.amount_radio.clicked.connect(self.amount_radio_clicked)
        self.form.spacing_radio.clicked.connect(self.spacing_radio_clicked)
        self.form.customSpacing.clicked.connect(lambda: runRebarDistribution(self))
        self.form.removeCustomSpacing.clicked.connect(lambda: removeRebarDistribution(self))
        self.form.PickSelectedFace.clicked.connect(lambda: getSelectedFace(self))
        self.form.orientation.currentIndexChanged.connect(self.getOrientation)
        self.form.image.setPixmap(QtGui.QPixmap(os.path.split(os.path.abspath(__file__))[0] + "/icons/UShapeRebarBottom.svg"))
        self.form.toolButton.setIcon(self.form.toolButton.style().standardIcon(QtGui.QStyle.SP_DialogHelpButton))
        self.form.toolButton.clicked.connect(lambda: showPopUpImageDialog(os.path.split(os.path.abspath(__file__))[0] + "/icons/UShapeRebarDetailed.svg"))
        self.Rebar = Rebar

    def getOrientation(self):
        orientation = self.form.orientation.currentText()
        if orientation == "Bottom":
            self.form.image.setPixmap(QtGui.QPixmap(os.path.split(os.path.abspath(__file__))[0] + "/icons/UShapeRebarBottom.svg"))
        elif orientation == "Top":
            self.form.image.setPixmap(QtGui.QPixmap(os.path.split(os.path.abspath(__file__))[0] + "/icons/UShapeRebarTop.svg"))
        elif orientation == "Right":
            self.form.image.setPixmap(QtGui.QPixmap(os.path.split(os.path.abspath(__file__))[0] + "/icons/UShapeRebarRight.svg"))
        else:
            self.form.image.setPixmap(QtGui.QPixmap(os.path.split(os.path.abspath(__file__))[0] + "/icons/UShapeRebarLeft.svg"))

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Apply) | int(QtGui.QDialogButtonBox.Cancel)

    def clicked(self, button):
        if button == int(QtGui.QDialogButtonBox.Apply):
            self.accept(button)

    def accept(self, signal = None):
        f_cover = self.form.frontCover.text()
        f_cover = FreeCAD.Units.Quantity(f_cover).Value
        b_cover = self.form.bottomCover.text()
        b_cover = FreeCAD.Units.Quantity(b_cover).Value
        r_cover = self.form.r_sideCover.text()
        r_cover = FreeCAD.Units.Quantity(r_cover).Value
        l_cover = self.form.l_sideCover.text()
        l_cover = FreeCAD.Units.Quantity(l_cover).Value
        t_cover = self.form.topCover.text()
        t_cover = FreeCAD.Units.Quantity(t_cover).Value
        diameter = self.form.diameter.text()
        diameter = FreeCAD.Units.Quantity(diameter).Value
        rounding = 0 #self.form.rounding.value()
        orientation = self.form.orientation.currentText()
        amount_check = self.form.amount_radio.isChecked()
        spacing_check = self.form.spacing_radio.isChecked()

        if not self.Rebar:
            if amount_check:
                amount = self.form.amount.value()
                rebar = makeJShapeRebar(f_cover, b_cover, r_cover, l_cover, diameter, t_cover, rounding, True, amount, orientation, self.SelectedObj, self.FaceName)
            elif spacing_check:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                rebar = makeJShapeRebar(f_cover, b_cover, r_cover, l_cover, diameter, t_cover, rounding, False, spacing, orientation, self.SelectedObj, self.FaceName)
        else:
            if amount_check:
                amount = self.form.amount.value()
                rebar = editJShapeRebar(self.Rebar, f_cover, b_cover, r_cover, l_cover, diameter, t_cover, rounding, True, amount, orientation, self.SelectedObj, self.FaceName)
            elif spacing_check:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                rebar = editJShapeRebar(self.Rebar, f_cover, b_cover, r_cover, l_cover, diameter, t_cover, rounding, False, spacing, orientation, self.SelectedObj, self.FaceName)
        
        if self.CustomSpacing:
            rebar.CustomSpacing = self.CustomSpacing
            FreeCAD.ActiveDocument.recompute()
       
        self.Rebar = rebar
        
        if signal == int(QtGui.QDialogButtonBox.Apply):
            pass
        else:
            FreeCADGui.Control.closeDialog(self)

    def amount_radio_clicked(self):
        self.form.spacing.setEnabled(False)
        self.form.amount.setEnabled(True)

    def spacing_radio_clicked(self):
        self.form.amount.setEnabled(False)
        self.form.spacing.setEnabled(True)


def makeJShapeRebar(f_cover, b_cover, r_cover, l_cover, diameter, t_cover, rounding, amount_spacing_check, amount_spacing_value, orientation = "Bottom", structure = None, facename = None):
    """ makeJShapeRebar(FrontCover, BottomCover, RightCover, LeftCover, Diameter, Topcover, Rounding, AmountSpacingCheck, AmountSpacingValue,
    Orientation, Structure, Facename): Adds the U-Shape reinforcement bar to the selected structural object.
    It takes four different types of orientations as input i.e 'Bottom', 'Top', 'Right', 'Left'.
    """
    if not structure and not facename:
        selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
        structure = selected_obj.Object
        facename = selected_obj.SubElementNames[0]
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    #StructurePRM = getTrueParametersOfStructure(structure)

    FacePRM = getParametersOfFace(structure, facename)

    if not FacePRM:
        FreeCAD.Console.PrintError("Cannot identified shape or from which base object sturctural element is derived\n")
        return

    # Get points of J-Shape rebar
    points = getpointsOfJShapeRebar(FacePRM, r_cover, l_cover, b_cover, t_cover, 300.0, orientation)

    print points

    sketch = FreeCAD.activeDocument().addObject('Sketcher::SketchObject', 'Sketch')
    sketch.MapMode = "FlatFace"
    sketch.Support = [(structure, facename)]
    FreeCAD.ActiveDocument.recompute()

    idx_ctr = sketch.addGeometry(Part.LineSegment(points[0], points[1]), False)
    idx_lt = sketch.addGeometry(Part.LineSegment(points[2], points[3]), False)
    idx_rt = sketch.addGeometry(Part.LineSegment(points[4], points[5]), False)

    lt_arc = Part.Circle(points[6], FreeCAD.Vector(0.0, 0.0, 1.0), points[7][2])
    idx_lt_arc = sketch.addGeometry(Part.ArcOfCircle(lt_arc, points[7][0], points[7][1]))

    rt_arc = Part.Circle(points[8], FreeCAD.Vector(0.0, 0.0, 1.0), points[9][2])
    idx_rt_arc = sketch.addGeometry(Part.ArcOfCircle(rt_arc, points[9][0], points[9][1]))

    #sketch.addConstraint(Sketcher.Constraint("Coincident", idx_ctr, 1, idx_lt_arc, 2))
    #sketch.addConstraint(Sketcher.Constraint("Coincident", idx_lt, 1, idx_lt_arc, 1))

    #sketch.addConstraint(Sketcher.Constraint("Coincident", idx_ctr, 2, idx_rt_arc, 1))
    #sketch.addConstraint(Sketcher.Constraint("Coincident", idx_rt, 1, idx_rt_arc, 2))

    FreeCAD.ActiveDocument.recompute()

    if amount_spacing_check:
        rebar = Arch.makeRebar(structure, sketch, diameter, amount_spacing_value, f_cover)
        FreeCAD.ActiveDocument.recompute()

    else:
        size = (ArchCommands.projectToVector(structure.Shape.copy(), face.normalAt(0, 0))).Length
        rebar = Arch.makeRebar(structure, sketch, diameter, int((size - diameter) / amount_spacing_value), f_cover)

    rebar.Rounding = rounding

    # Adds properties to the rebar object
    rebar.ViewObject.addProperty("App::PropertyString", "RebarShape", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Shape of rebar")).RebarShape = "JShapeRebar"
    rebar.ViewObject.setEditorMode("RebarShape", 2)
    rebar.addProperty("App::PropertyDistance", "FrontCover", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Front cover of rebar")).FrontCover = f_cover
    rebar.setEditorMode("FrontCover", 2)
    rebar.addProperty("App::PropertyDistance", "RightCover", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Right Side cover of rebar")).RightCover = r_cover
    rebar.setEditorMode("RightCover", 2)
    rebar.addProperty("App::PropertyDistance", "LeftCover", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Left Side cover of rebar")).LeftCover = l_cover
    rebar.setEditorMode("LeftCover", 2)
    rebar.addProperty("App::PropertyDistance", "BottomCover", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Bottom cover of rebar")).BottomCover = b_cover
    rebar.setEditorMode("BottomCover", 2)
    rebar.addProperty("App::PropertyBool", "AmountCheck", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Amount radio button is checked")).AmountCheck
    rebar.setEditorMode("AmountCheck", 2)
    rebar.addProperty("App::PropertyDistance", "TopCover", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Top cover of rebar")).TopCover = t_cover
    rebar.setEditorMode("TopCover", 2)
    rebar.addProperty("App::PropertyDistance", "TrueSpacing", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Spacing between of rebars")).TrueSpacing = amount_spacing_value
    rebar.setEditorMode("TrueSpacing", 2)
    rebar.addProperty("App::PropertyString", "Orientation", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Shape of rebar")).Orientation = orientation
    rebar.setEditorMode("Orientation", 2)
    if amount_spacing_check:
        rebar.AmountCheck = True
    else:
        rebar.AmountCheck = False
        rebar.TrueSpacing = amount_spacing_value
    rebar.Label = "JShapeRebar"
    FreeCAD.ActiveDocument.recompute()
    return rebar

def editJShapeRebar(Rebar, f_cover, b_cover, r_cover, l_cover, diameter, t_cover, rounding, amount_spacing_check, amount_spacing_value, orientation, structure = None, facename = None):
    sketch = Rebar.Base
    if structure and facename:
        sketch.Support = [(structure, facename)]
    # Check if sketch support is empty.
    if not sketch.Support:
        showWarning("You have checked remove external geometry of base sketchs when needed.\nTo unchecked Edit->Preferences->Arch.")
        return
    # Assigned values
    facename = sketch.Support[0][1][0]
    structure = sketch.Support[0][0]
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    #StructurePRM = getTrueParametersOfStructure(structure)
    # Get parameters of the face where sketch of rebar is drawn
    FacePRM = getParametersOfFace(structure, facename)
    # Get points of U-Shape rebar
    points = getpointsOfJShapeRebar(FacePRM, r_cover, l_cover, b_cover, t_cover, 300.0, orientation)
    sketch.movePoint(0, 1, points[0], 0)
    FreeCAD.ActiveDocument.recompute()
    sketch.movePoint(0, 2, points[1], 0)
    FreeCAD.ActiveDocument.recompute()
    sketch.movePoint(1, 1, points[1], 0)
    FreeCAD.ActiveDocument.recompute()
    sketch.movePoint(1, 2, points[2], 0)
    FreeCAD.ActiveDocument.recompute()
    sketch.movePoint(2, 1, points[2], 0)
    FreeCAD.ActiveDocument.recompute()
    sketch.movePoint(2, 2, points[3], 0)
    FreeCAD.ActiveDocument.recompute()
    Rebar.OffsetStart = f_cover
    Rebar.OffsetEnd = f_cover
    if amount_spacing_check:
        Rebar.Amount = amount_spacing_value
        FreeCAD.ActiveDocument.recompute()
        Rebar.AmountCheck = True
    else:
        size = (ArchCommands.projectToVector(structure.Shape.copy(), face.normalAt(0, 0))).Length
        Rebar.Amount = int((size - diameter) / amount_spacing_value)
        FreeCAD.ActiveDocument.recompute()
        Rebar.AmountCheck = False
    Rebar.Diameter = diameter
    Rebar.FrontCover = f_cover
    Rebar.RightCover = r_cover
    Rebar.LeftCover = l_cover
    Rebar.BottomCover = b_cover
    Rebar.TopCover = t_cover
    Rebar.Rounding = rounding
    Rebar.TrueSpacing = amount_spacing_value
    Rebar.Orientation = orientation
    FreeCAD.ActiveDocument.recompute()
    return Rebar

def editDialog(vobj):
    FreeCADGui.Control.closeDialog()
    obj = _JShapeRebarTaskPanel(vobj.Object)
    obj.form.frontCover.setText(str(vobj.Object.FrontCover))
    obj.form.r_sideCover.setText(str(vobj.Object.RightCover))
    obj.form.l_sideCover.setText(str(vobj.Object.LeftCover))
    obj.form.bottomCover.setText(str(vobj.Object.BottomCover))
    obj.form.diameter.setText(str(vobj.Object.Diameter))
    obj.form.topCover.setText(str(vobj.Object.TopCover))
    obj.form.rounding.setValue(vobj.Object.Rounding)
    obj.form.orientation.setCurrentIndex(obj.form.orientation.findText(str(vobj.Object.Orientation)))
    if vobj.Object.AmountCheck:
        obj.form.amount.setValue(vobj.Object.Amount)
    else:
        obj.form.amount_radio.setChecked(False)
        obj.form.spacing_radio.setChecked(True)
        obj.form.amount.setDisabled(True)
        obj.form.spacing.setEnabled(True)
        obj.form.spacing.setText(str(vobj.Object.TrueSpacing))
    #obj.form.PickSelectedFace.setVisible(False)
    FreeCADGui.Control.showDialog(obj)

def CommandJShapeRebar():
    selected_obj = check_selected_face()
    if selected_obj:
        FreeCADGui.Control.showDialog(_JShapeRebarTaskPanel())