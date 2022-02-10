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
        self.prevResultButton = self.findChild(QPushButton, "prevResultButton")
        self.airportCodeLabel = self.findChild(QLabel, "airportCodeLabel")
        self.airportNameLabel = self.findChild(QLabel, "airportNameLabel")
        self.locationLabel = self.findChild(QLabel, "locationLabel")
        self.covidLabel = self.findChild(QLabel, "covidLabel")
        self.nearbyButton = self.findChild(QPushButton, "nearbyButton")
        self.nearbyList = self.findChild(QListWidget, "nearbyList")

        self.isFirstSearch = True
        self.prevResultButton.hide()
        self.airportCodeLabel.hide()
        self.airportNameLabel.hide()
        self.locationLabel.hide()
        self.covidLabel.hide()
        self.nearbyButton.hide()
        self.nearbyList.hide()

        self.resultHistory = []

        conn = sqlite3.connect("airports.db")
        cur = conn.cursor()
        cur.execute("SELECT airportCode FROM Airports;")
        selectData = cur.fetchall()
        conn.close()

        for row in selectData:
            self.airportSelect.addItem(row[0])

        self.searchButton.clicked.connect(self.search)
        self.prevResultButton.clicked.connect(self.prevResult)

        self.show()

    def loadAirportData(self, airportCode):
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


    def search(self):
        airportCode = self.airportSelect.currentText()
        self.loadAirportData(airportCode)

        if self.isFirstSearch == True:
            self.airportCodeLabel.show()
            self.airportNameLabel.show()
            self.locationLabel.show()
            self.covidLabel.show()
            self.nearbyButton.show()
            self.isFirstSearch = False

        self.resultHistory.append(airportCode)

        if len(self.resultHistory) > 1:
            self.prevResultButton.show()

    def prevResult(self):
        if len(self.resultHistory) == 2:
            self.prevResultButton.hide()
        
        self.resultHistory.pop()
        airportCode = self.resultHistory[-1]
        self.loadAirportData(airportCode)

app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()