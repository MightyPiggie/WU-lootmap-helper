import sys

from PyQt6.QtGui import QGuiApplication, QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import (QComboBox, QLineEdit, QPushButton, QMainWindow, QApplication, QVBoxLayout, QWidget, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6 import QtGui

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from calculatePoints import generate_circle_coordinates_within, filter_coordinates_by_angle, reduce_coordinates_by_angle, filter_coordinates_by_min_distance, filter_coordinates_outside_range

def calculate_coordinates(X, Y, r, angle_min, angle_max ):
    coordinates_within = generate_circle_coordinates_within(X, Y, r)

    # Filter coordinates by the specified angular range
    coordinates_within_angle = filter_coordinates_by_angle(coordinates_within, X, Y, angle_min, angle_max)
    return coordinates_within_angle

def get_distance_value(distance):
    if distance < 0:
        return 0
    DistanceValues = [3, 5, 9, 19, 49, 199, 499, 999, 1999, 4096]
    return DistanceValues[distance]

def get_direction_values(direction_index, looking_direction):
    # print("direction_index", direction_index)
    directionValues = [0, -45, -90, -135, 180, 135, 90, 45] # ["straight ahead", "ahead to the right", "right", "back to the right", "backwards", "back to the left", "to the left", "ahead to the left" ]
    directionValue = directionValues[direction_index]
    directionValue = ( 450 + ( looking_direction + directionValue )) % 360
    
    # print(directionValue)
    DirectionMin = directionValue - 22.5
    DirectionMax = directionValue + 22.5
    if DirectionMin < 0:
        DirectionMin += 360
    if DirectionMax > 360:
        DirectionMax -= 360
    return DirectionMin, DirectionMax

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.Coordinates = None
        self.PrevCoordinates = None
        self.img = plt.imread("mapdump-flat.png")

        self.setWindowTitle("My App")
        self.layoutWidgets = QVBoxLayout()
        self.layoutPlot = QVBoxLayout()
        self.mainLayout = QGridLayout()
        self.mainLayout.addLayout(self.layoutWidgets, 0, 0)
        self.mainLayout.addLayout(self.layoutPlot, 0, 1)
        self.mainLayout.setColumnStretch(1, 2)
        self.mainLayout.setColumnMinimumWidth(0, int(QtGui.QGuiApplication.primaryScreen().availableSize().width()/8))
        self.layoutWidgets.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.widget = QWidget()

        self.DirectionBox = QComboBox()  # ["straight ahead", "ahead to the left", "to the left", "back to the left", "backwards", "back to the right", "right", "ahead to the right"]
        self.DirectionBox.addItems(["straight ahead", "ahead to the right", "right", "back to the right", "backwards", "back to the left", "to the left", "ahead to the left" ]) # ["straight ahead", "ahead to the right", "right", "back to the right", "backwards", "back to the left", "to the left", "ahead to the left"] 

        self.DistanceBox = QComboBox()
        self.DistanceBox.addItems(["a stone's throw away", "very close", "pretty close by", "fairly close by", "some distance away", "quite some distance away", "rather a long distance away", "pretty far away", "far away", "very far away"])

        self.FacingDirection = QLineEdit()
        self.FacingDirectionValidator = QDoubleValidator()
        self.FacingDirectionValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.FacingDirectionValidator.setRange(0, 360, 1)
        self.FacingDirection.setValidator(self.FacingDirectionValidator)
        self.FacingDirection.setPlaceholderText("Facing Direction")

        self.PlayerCoordValidator = QIntValidator()
        self.PlayerCoordValidator.setBottom(0)
        self.PlayerCoordValidator.setTop(4096)
        self.PlayerXCoord = QLineEdit()
        self.PlayerYCoord = QLineEdit()
        self.PlayerXCoord.setValidator(self.PlayerCoordValidator)
        self.PlayerYCoord.setValidator(self.PlayerCoordValidator)
        self.PlayerXCoord.setPlaceholderText("X Coordinate")
        self.PlayerYCoord.setPlaceholderText("Y Coordinate")

        self.dynamic_canvas = FigureCanvas(Figure(figsize=(10, 10)))
        self._dynamic_ax = self.dynamic_canvas.figure.subplots()
        self.plot_coordinates(np.array([[0, 0]]) )
        
        self.layoutPlot.addWidget(self.dynamic_canvas)
        self.layoutPlot.addWidget(NavigationToolbar(self.dynamic_canvas, self))

        self.ResetButton = QPushButton("Reset", clicked = self.reset)
        self.SumbitButton = QPushButton("Submit", clicked = self.calculate)
        self.UndoButton = QPushButton("Undo", clicked = self.undo)

        self.layoutWidgets.addWidget(self.DirectionBox)
        self.layoutWidgets.addWidget(self.DistanceBox)
        self.layoutWidgets.addWidget(self.FacingDirection)
        self.layoutWidgets.addWidget(self.PlayerXCoord)
        self.layoutWidgets.addWidget(self.PlayerYCoord)
        self.layoutWidgets.addWidget(self.SumbitButton)
        self.layoutWidgets.addWidget(self.ResetButton)
        self.layoutWidgets.addWidget(self.UndoButton)

        self.widget.setLayout(self.mainLayout)
        self.setCentralWidget(self.widget)

    def calculate(self):
        try:
            if(float(self.FacingDirection.text()) >= 360.0):
                self.FacingDirection.setText("0")
            FacingDirectionValue = float(self.FacingDirection.text())
        except:
            print("Facing Direction is not valid")
            return 
        DirectionBoxIndex = self.DirectionBox.currentIndex()
        DistanceBoxIndex = self.DistanceBox.currentIndex()
        try:
            PlayerXCoord = int(self.PlayerXCoord.text())
            PlayerYCoord = int(self.PlayerYCoord.text())
        except:
            print("Player Coordinates are not valid")
            return
        DistanceValueMax = get_distance_value(DistanceBoxIndex)
        DistanceValueMin = get_distance_value(DistanceBoxIndex-1)
        DirectionMin, DirectionMax = get_direction_values(DirectionBoxIndex, FacingDirectionValue)
        
        if self.Coordinates is not None:
            self.PrevCoordinates = self.Coordinates
            self.Coordinates = reduce_coordinates_by_angle(self.PrevCoordinates, PlayerXCoord, PlayerYCoord, DistanceValueMax, DirectionMin, DirectionMax)
            print(len(self.Coordinates))
        else:
            coordinates_within_angle = calculate_coordinates(PlayerXCoord, PlayerYCoord, DistanceValueMax, DirectionMin, DirectionMax)
            self.Coordinates = filter_coordinates_by_min_distance(coordinates_within_angle, PlayerXCoord, PlayerYCoord, DistanceValueMin)
        self.Coordinates = filter_coordinates_outside_range(self.Coordinates)

        self.plot_coordinates(self.Coordinates)
    
    def reset(self):
        self.PrevCoordinates = self.Coordinates
        self.Coordinates = None
        self.FacingDirection.setText("")
        self.PlayerXCoord.setText("")
        self.PlayerYCoord.setText("")
        self.plot_coordinates(np.array([[0, 0]]) )
    
    def plot_coordinates(self, coordinates_within_angle):
        self._dynamic_ax.clear()
        self._dynamic_ax.imshow(self.img)
        self._dynamic_ax.set_xlabel('X')
        self._dynamic_ax.set_ylabel('Y')
        self.dynamic_canvas.figure.set_layout_engine(layout="constrained")
        self._dynamic_ax.imshow(self.img) 
        self.scatterplot = self._dynamic_ax.scatter(coordinates_within_angle[:, 0], coordinates_within_angle[:, 1], color='#FF999C', label='Area to be checked')
        self._dynamic_ax.set_aspect('equal', adjustable='box')
        self.scatterplot.figure.canvas.draw()
    
    def undo(self):
        if self.PrevCoordinates is not None:
            self.Coordinates = self.PrevCoordinates
            self.plot_coordinates(self.Coordinates)
        else:
            self.reset()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(QtGui.QGuiApplication.primaryScreen().availableSize())
    window.show()
    sys.exit(app.exec())
