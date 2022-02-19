# Can ignore "missing imports" error for wikipediaapi if you have already pip install -r requirements.txt.
import wikipediaapi
import os


def request_summary():
    # Continously looks for "input.txt" to read user's request URL.
    url = ""
    while True:
        if os.path.exists("input.txt"):
            with open("input.txt", "r") as file:
                url = file.read()
            # Required - must remove "input.txt" for the next request to work.
            os.remove("input.txt")
            break
        else:
            continue

    page_exists = True

    # Partitions request URL into ("https://en.wikipedia.org", "/wiki/", "{page title}")
    # to check validity of URL and see if a wikipedia page exists for the page title.
    url_parts = url.partition("/wiki/")
    if url_parts[0] != "https://en.wikipedia.org" or url_parts[1] != "/wiki/":
        page_exists = False

    wikipedia = wikipediaapi.Wikipedia("en")
    wikipage = wikipedia.page(url_parts[2])

    if not wikipage.exists():
        page_exists = False

    # If the wikipedia page exists, writes summary to "output.txt" and request status to "status.txt".
    if page_exists:
        with open("output.txt", "w") as file:
            file.write(wikipage.summary)
        with open("status.txt", "w") as file:
            file.write("success")
    else:
        with open("status.txt", "w") as file:
            file.write("fail")


if __name__ == '__main__':
    # Keeps running the microservice until user enters Ctrl-C to terminate the microservice.
    while True:
        request_summary()
