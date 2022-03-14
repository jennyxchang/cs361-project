from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QComboBox, QListWidget, QMessageBox, QTextBrowser
from PyQt5 import uic
import sys
import sqlite3
import os
import csv


class UI(QMainWindow):
    # Initializes UI.
    def __init__(self):
        super(UI, self).__init__()

        uic.loadUi("mainWindow.ui", self)
        self.setWindowTitle("Airport Information Generator")

        # Sets a name for each UI element.
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

        # Sets a flag for first search.
        self.isFirstSearch = True

        # Hides elements for first search.
        self.prevResultButton.hide()
        self.airportCodeLabel.hide()
        self.airportNameLabel.hide()
        self.locationLabel.hide()
        self.covidLabel.hide()
        self.nearbyButton.hide()
        self.nearbyList.hide()
        self.weatherButton.hide()
        self.weatherText.hide()

        # Uses a list to track history of search results.
        self.resultHistory = []

        # Stores the zipcode from search result.
        self.requestZipcode = ""

        # Connects to the database to populate dropdown with airport codes.
        conn = sqlite3.connect("airports.db")
        cur = conn.cursor()
        cur.execute("SELECT airportCode FROM Airports;")
        selectData = cur.fetchall()
        conn.close()

        for row in selectData:
            self.airportSelect.addItem(row[0])

        # Performs respective action when a button is clicked.
        self.searchButton.clicked.connect(self.search)
        self.prevResultButton.clicked.connect(self.alertBox)
        self.nearbyButton.clicked.connect(self.nearbySearch)
        self.weatherButton.clicked.connect(self.weatherSearch)

        self.show()

    # Loads airport data for a given airport code.
    def loadAirportData(self, airportCode):
        # Connects to the database to query using an airport code.
        conn = sqlite3.connect("airports.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT airportName, airportCity, airportState, airportZipcode, covidTesting FROM Airports WHERE airportCode = ?;", (airportCode,))
        airportName, airportCity, airportState, airportZipcode, covidTesting = cur.fetchall()[
            0]
        conn.close()

        # Loads airport data to UI elements.
        self.airportCodeLabel.setText(f'Airport Code: {airportCode}')
        self.airportNameLabel.setText(f'Airport Name: {airportName}')
        self.locationLabel.setText(
            f'Location: {airportCity}, {airportState} {airportZipcode}')
        if covidTesting == 0:
            self.covidLabel.setText("COVID Testing: No")
        else:
            self.covidLabel.setText("COVID Testing: Yes")

        # Stores the zipcode from search result.
        self.requestZipcode = airportZipcode

    # Generates a search result on UI.
    def search(self):
        # Searches using the selected airport code.
        airportCode = self.airportSelect.currentText()
        self.loadAirportData(airportCode)

        # Shows UI elements if it's the first search. Otherwise, the UI elements are already shown from the previous search.
        if self.isFirstSearch == True:
            self.airportCodeLabel.show()
            self.airportNameLabel.show()
            self.locationLabel.show()
            self.covidLabel.show()
            self.nearbyButton.show()
            self.weatherButton.show()
            self.isFirstSearch = False

        # Adds airport code to search result history.
        self.resultHistory.append(airportCode)

        # Shows a previous result button if there are more than 1 search result.
        if len(self.resultHistory) > 1:
            self.prevResultButton.show()

        # Resets UI elements that display nearby restaurants and weather, until they are requested later.
        self.nearbyList.clear()
        self.nearbyList.hide()
        self.weatherText.clear()
        self.weatherText.hide()

    # Displays a warning before previous search result is displayed. Allows user to choose to proceed or cancel current action.
    def alertBox(self):
        alertMessage = QMessageBox()
        alertMessage.setWindowTitle("Show previous search result?")
        alertMessage.setText(
            "The current result will be cleared. Are you sure?")
        alertMessage.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        alertButton = alertMessage.exec_()

        # Loads previous search result only when user chooses 'Yes'. Otherwise, nothing happens.
        if alertButton == QMessageBox.Yes:
            self.prevResult()

    # Generates the previous search result.
    def prevResult(self):
        # When resultHistory == 2, there are only the current search result and the 1 search result before it.
        # Hides the previous result button because there will be no more previous search result after this function is completed.
        if len(self.resultHistory) == 2:
            self.prevResultButton.hide()

        # Removes the current search result from history.
        self.resultHistory.pop()
        
        # Loads the previous search result from history.
        airportCode = self.resultHistory[-1]
        self.loadAirportData(airportCode)

        # Resets UI elements that display nearby restaurants and weather, until they are requested later.
        self.nearbyList.clear()
        self.nearbyList.hide()
        self.weatherText.clear()
        self.weatherText.hide()

    # Requests nearby restaurants from teammate's microservice - place finder.
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

    # Generates nearby restaurants on UI.
    def nearbySearch(self):
        self.nearbyList.clear()
        restaurants = self.requestPlaceFinder()
        for item in restaurants:
            self.nearbyList.addItem(item)
        self.nearbyList.show()

    # Requests weather from teammate's microservice - weather service.
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

    # Generates weather on UI.
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
