import sys

from PyQt6.QtGui import QGuiApplication, QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import (QComboBox, QLineEdit, QPushButton, QMainWindow, QApplication, QVBoxLayout, QWidget)

import numpy as np
import matplotlib.pyplot as plt

from calculatePoints import generate_circle_coordinates_within, filter_coordinates_by_angle, reduce_coordinates_by_angle, filter_coordinates_by_min_distance, filter_coordinates_outside_range

from PyQt6.QtCore import Qt



def generate_test_plot():
    # Example usage:
    X = 1000
    Y = 1000
    r = 500
    angle_min = 0    # Minimum angle in degrees
    angle_max = 45   # Maximum angle in degrees

    # Generate all coordinates within the circle
    coordinates_within = generate_circle_coordinates_within(X, Y, r)

    # Filter coordinates by the specified angular range
    coordinates_within_angle = filter_coordinates_by_angle(coordinates_within, X, Y, angle_min, angle_max)

    coordinates_within_angle3 = reduce_coordinates_by_angle(coordinates_within_angle, 1100, 1100, 400, 22.5, 67.5)
    coordinates_within_angle3 = reduce_coordinates_by_angle(coordinates_within_angle3, 1300, 1200, 500, 112.5, 157.5)

    # coordinates_within2 = generate_circle_coordinates_within(1300, 1200, 200)

    # # Filter coordinates by the specified angular range
    # coordinates_within_angle2 = filter_coordinates_by_angle(coordinates_within2, 1300, 1200, 112.5, 157.5)
    # X = 1300
    # Y = 1300
    # r = 200
    # coordinates_within2 = generate_circle_coordinates_within(X, Y, r)
    # coordinates_within_angle2 = filter_coordinates_by_angle(coordinates_within2, X, Y, angle_min+22.5, angle_max+22.5)
    # print(coordinates_within_angle.shape)

    # nrows, ncols = coordinates_within_angle.shape
    # dtype={'names':['f{}'.format(i) for i in range(ncols)],
    #        'formats':ncols * [coordinates_within_angle.dtype]}
    # coordinates_within_angle3 = np.intersect1d(coordinates_within_angle.view(dtype), coordinates_within_angle2.view(dtype))
    # coordinates_within_angle3 = coordinates_within_angle3.view(coordinates_within_angle.dtype).reshape(-1, ncols)
    # print(type(coordinates_within_angle3))

    img = plt.imread("mapdump-flat.png")

    # Plotting
    plt.figure(figsize=(8, 8))
    plt.imshow(img) 
    # plt.scatter(coordinates_within[:, 0], coordinates_within[:, 1], color='lightgray', alpha=0, label='All Points within Circle' )
    plt.scatter(coordinates_within_angle3[:, 0], coordinates_within_angle3[:, 1], color='#FF999C', alpha=0.1, label='Area to be checked')
    # plt.scatter(coordinates_within_angle2[:, 0], coordinates_within_angle2[:, 1], color='b', alpha=0.1, label='Points within Angle Range')
    # plt.scatter(coordinates_within_angle[:, 0], coordinates_within_angle[:, 1], color='g', alpha=0.1, label='Points within Angle Range')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title(f'Points within Circle and Angle Range ({angle_min}° to {angle_max}°)')
    plt.xlabel('X')
    plt.ylabel('Y')
    # plt.legend()
    plt.grid(True)
    plt.savefig("output.png")
    # plt.imshow(img)
    plt.show()

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
    print("direction_index", direction_index)
    directionValues = [0, -45, -90, -135, 180, 135, 90, 45] # ["straight ahead", "ahead to the right", "right", "back to the right", "backwards", "back to the left", "to the left", "ahead to the left" ]
    directionValue = directionValues[direction_index]
    directionValue = ( 450 + ( looking_direction + directionValue )) % 360
    
    print(directionValue)
    DirectionMin = directionValue - 22.5
    DirectionMax = directionValue + 22.5
    if DirectionMin < 0:
        DirectionMin += 360
    if DirectionMax > 360:
        DirectionMax -= 360
    return DirectionMin, DirectionMax

def plot_coordinates(coordinates_within_angle):
    img = plt.imread("mapdump-flat.png")

    # Plotting
    plt.figure(figsize=(8, 8))
    plt.imshow(img) 
    plt.scatter(coordinates_within_angle[:, 0], coordinates_within_angle[:, 1], color='#FF999C', label='Area to be checked')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title(f'Points within Circle and Angle Range')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    # plt.savefig("output.png")
    plt.show()


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.Coordinates = None
        self.PrevCoordinates = None

        self.setWindowTitle("My App")
        self.layout = QVBoxLayout()
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

        self.ResetButton = QPushButton("Reset", clicked = self.reset)

        self.SumbitButton = QPushButton("Submit", clicked = self.calculate)

        self.layout.addWidget(self.DirectionBox)
        self.layout.addWidget(self.DistanceBox)
        self.layout.addWidget(self.FacingDirection)
        self.layout.addWidget(self.PlayerXCoord)
        self.layout.addWidget(self.PlayerYCoord)
        self.layout.addWidget(self.SumbitButton)
        self.layout.addWidget(self.ResetButton)

        self.widget.setLayout(self.layout)
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
        plot_coordinates(self.Coordinates)
    
    def reset(self):
        self.Coordinates = None
        self.PrevCoordinates = None
        self.FacingDirection.setText("")
        self.PlayerXCoord.setText("")
        self.PlayerYCoord.setText("")
        

  
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # generate_test_plot()
    sys.exit(app.exec())





