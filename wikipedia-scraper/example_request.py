"""
Instruction for how to use the microservice wikipedia scraper:

Everything you need is in the folder "wikipedia-scraper".
This file "example_request.py" contains example code of how to make request, wait for response, and get response.
Feel free to incorporate the example code into your own code, or edit any part of the example code as needed.
Please note: you don't have to run this file for the microservice to work.

1) Install required libraries by typing into command line "pip install -r requirements.txt".
2) Run "main.py" in the background (it will keep running unless you use Ctrl-C to terminate microservice)
3) Actions needed from within your program:
   a) Make a request by writing an URL to "input.txt" (example code below)
   b) Wait for a response by continuously checking if "status.txt" is created by microservice (example code below)
   c) Read "status.txt":
      - If "status.txt" contains "success", read "output.txt" to get summary text.
      - If "status.txt" contains "fail", the URL provided does not have a wikipedia page. No "output.txt" will be created.
4) After each request, "input.txt" will be deleted. So, you can start another request by making another "input.txt".
   As long as the microservice is running, it will keep looking for "input.txt".

Last note: The microservice reads and writes file from within its folder "wikipedia-scraper".
This means that if your program is outside the folder, make sure to pay attention to the path of where you are writing
"input.txt" and reading "status.txt" and "output.txt" (example below).
"""

# Needs to import os library to look for files.
import os

# Your program sends a request to microservice by writing an URL to "input.txt".
# If your program is outside folder "wikipedia-scraper", use with open("./wikipedia-scraper/input.txt", "w") as file.
example_url = "https://en.wikipedia.org/wiki/Computer_science"
with open("input.txt", "w") as file:
    file.write(example_url)

# Your program then waits for microservice to send response by continuously looking to see if "status.txt" is created.
# If your program is outside folder "wikipedia-scraper", use if os.path.exists("./wikipedia-scraper/status.txt"),
# with open("./wikipedia-scraper/output.txt", "r") as file, etc.
status = ""
while True:
    # "status.txt" is found.
    if os.path.exists("status.txt"):
        with open("status.txt", "r") as file:
            status = file.read()
        # Required - must remove "status.txt" for the next request to work.
        os.remove("status.txt")

        # Successful request.
        if status == "success":
            # Your program reads summary from "output.txt".
            with open("output.txt", "r") as file:
                # Your program can process summary accordingly.
                print(file.read())
            # Required - must remove "output.txt" for the next request to work.
            os.remove("output.txt")
        # Failed request.
        elif status == "fail":
            # Your program can process error accordingly.
            print("Wikipedia page does not exist!")
        break
    # "status.txt" is not found. Continue looking.
    else:
        continue
