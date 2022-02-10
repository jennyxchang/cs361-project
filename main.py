from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QComboBox, QListWidget
from PyQt5 import uic
import sys
import sqlite3

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        uic.loadUi("mainWindow.ui", self)
        self.setWindowTitle("Airport Information Generator")

        self.airportSelect = self.findChild(QComboBox, "airportSelect")
        self.searchButton = self.findChild(QPushButton, "searchButton")
        self.lastResultButton = self.findChild(QPushButton, "lastResultButton")
        self.airportCodeLabel = self.findChild(QLabel, "airportCodeLabel")
        self.airportNameLabel = self.findChild(QLabel, "airportNameLabel")
        self.locationLabel = self.findChild(QLabel, "locationLabel")
        self.covidLabel = self.findChild(QLabel, "covidLabel")
        self.nearbyButton = self.findChild(QPushButton, "nearbyButton")
        self.nearbyList = self.findChild(QListWidget, "nearbyList")

        self.isFirstSearch = True
        self.lastResultButton.hide()
        self.airportCodeLabel.hide()
        self.airportNameLabel.hide()
        self.locationLabel.hide()
        self.covidLabel.hide()
        self.nearbyButton.hide()
        self.nearbyList.hide()

        self.numHistory = 0
        file = open("history.txt","w")
        file.close()

        conn = sqlite3.connect("airports.db")
        cur = conn.cursor()
        cur.execute("SELECT airportCode FROM Airports;")
        selectData = cur.fetchall()
        conn.close()

        for row in selectData:
            self.airportSelect.addItem(row[0])

        self.searchButton.clicked.connect(self.search)
        self.lastResultButton.clicked.connect(self.lastResult)

        self.show()

    def search(self):
        airportCode = self.airportSelect.currentText()
        conn = sqlite3.connect("airports.db")
        cur = conn.cursor()
        cur.execute("SELECT airportName, airportCity, airportState, airportZipcode, covidTesting FROM Airports WHERE airportCode = ?;", (airportCode,))
        airportName, airportCity, airportState, airportZipcode, covidTesting = cur.fetchall()[0]
        conn.close()

        self.airportCodeLabel.setText(f'Airport Code: {airportCode}')
        self.airportNameLabel.setText(f'Airport Name: {airportName}')
        self.locationLabel.setText(f'Location: {airportCity}, {airportState} {airportZipcode}')
        if covidTesting == 0:
            self.covidLabel.setText("COVID Testing: No")
        else:
            self.covidLabel.setText("COVID Testing: Yes")

        if (self.isFirstSearch == True):
            self.lastResultButton.show()
            self.airportCodeLabel.show()
            self.airportNameLabel.show()
            self.locationLabel.show()
            self.covidLabel.show()
            self.nearbyButton.show()
            self.isFirstSearch = False

        self.numHistory += 1
        with open("history.txt", "a") as f:
            f.write(airportCode)
            f.write("\n")

    def lastResult(self):
        pass

app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()