from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QComboBox, QListWidget, QMessageBox, QTextBrowser
from PyQt5 import uic
import sys
import sqlite3
import os
import csv


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
        self.weatherButton = self.findChild(QPushButton, "weatherButton")
        self.weatherText = self.findChild(QTextBrowser, "weatherText")

        self.isFirstSearch = True
        self.prevResultButton.hide()
        self.airportCodeLabel.hide()
        self.airportNameLabel.hide()
        self.locationLabel.hide()
        self.covidLabel.hide()
        self.nearbyButton.hide()
        self.nearbyList.hide()
        self.weatherButton.hide()
        self.weatherText.hide()

        self.resultHistory = []
        self.requestZipcode = ""

        conn = sqlite3.connect("airports.db")
        cur = conn.cursor()
        cur.execute("SELECT airportCode FROM Airports;")
        selectData = cur.fetchall()
        conn.close()

        for row in selectData:
            self.airportSelect.addItem(row[0])

        self.searchButton.clicked.connect(self.search)
        self.prevResultButton.clicked.connect(self.alertBox)
        self.nearbyButton.clicked.connect(self.nearbySearch)
        self.weatherButton.clicked.connect(self.weatherSearch)

        self.show()

    def loadAirportData(self, airportCode):
        conn = sqlite3.connect("airports.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT airportName, airportCity, airportState, airportZipcode, covidTesting FROM Airports WHERE airportCode = ?;", (airportCode,))
        airportName, airportCity, airportState, airportZipcode, covidTesting = cur.fetchall()[
            0]
        conn.close()

        self.airportCodeLabel.setText(f'Airport Code: {airportCode}')
        self.airportNameLabel.setText(f'Airport Name: {airportName}')
        self.locationLabel.setText(
            f'Location: {airportCity}, {airportState} {airportZipcode}')
        if covidTesting == 0:
            self.covidLabel.setText("COVID Testing: No")
        else:
            self.covidLabel.setText("COVID Testing: Yes")

        self.requestZipcode = airportZipcode

    def search(self):
        airportCode = self.airportSelect.currentText()
        self.loadAirportData(airportCode)

        if self.isFirstSearch == True:
            self.airportCodeLabel.show()
            self.airportNameLabel.show()
            self.locationLabel.show()
            self.covidLabel.show()
            self.nearbyButton.show()
            self.weatherButton.show()
            self.isFirstSearch = False

        self.resultHistory.append(airportCode)

        if len(self.resultHistory) > 1:
            self.prevResultButton.show()

        self.nearbyList.clear()
        self.nearbyList.hide()
        self.weatherText.clear()
        self.weatherText.hide()

    def alertBox(self):
        alertMessage = QMessageBox()
        alertMessage.setWindowTitle("Show previous search result?")
        alertMessage.setText(
            "The current result will be cleared. Are you sure?")
        alertMessage.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        alertButton = alertMessage.exec_()

        if alertButton == QMessageBox.Yes:
            self.prevResult()

    def prevResult(self):
        if len(self.resultHistory) == 2:
            self.prevResultButton.hide()

        self.resultHistory.pop()
        airportCode = self.resultHistory[-1]
        self.loadAirportData(airportCode)

        self.nearbyList.clear()
        self.nearbyList.hide()
        self.weatherText.clear()
        self.weatherText.hide()

    def requestPlaceFinder(self):
        # Sends a request to teammate's microservice - place finder.
        with open("./place-finder/input.txt", "w") as file:
            file.write(
                f'["{self.requestZipcode}", "US", 10, "5", ["restaurants"]]')

        status = ""
        # Waits for teammate's microservice to send response.
        while True:
            if os.path.exists("./place-finder/status.txt"):
                with open("./place-finder/status.txt", "r") as file:
                    status = file.read()
                os.remove("./place-finder/status.txt")
                break
            else:
                continue

        restaurants = []
        # Reads response.
        with open("./place-finder/output.csv", "r") as file:
            csvFile = csv.DictReader(file)
            for row in csvFile:
                restaurants.append(dict(row)["name"])
        os.remove("./place-finder/output.csv")
        return restaurants

    def nearbySearch(self):
        self.nearbyList.clear()
        restaurants = self.requestPlaceFinder()
        # exampleList = ["Beecher's Handmade Cheese", "Bambuza Vietnam Kitchen and Bar",
        #               "Bigfoot Food & Spirits", "Seattle Seahawks 12 Club"]
        for item in restaurants:
            self.nearbyList.addItem(item)
        self.nearbyList.show()

    def requestWeatherService(self):
        # Sends a request to teammate's microservice - weather service.
        with open("./weather-service/request.txt", "w") as file:
            file.write(self.requestZipcode)

        weather = ""
        # Waits for teammate's microservice to send response.
        while weather == "":
            # Reads response.
            with open("./weather-service/response.txt", "r") as file:
                weather = file.read()

        with open("./weather-service/response.txt", "w") as file:
            file.write("")
        
        return weather

    def weatherSearch(self):
        self.weatherText.clear()
        weatherRes = self.requestWeatherService()
        parts = weatherRes.partition("Later:")
        weather = f'{parts[0]}\n\n{parts[1]}{parts[2]}' 
        self.weatherText.setText(weather)
        self.weatherText.show()


app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()
