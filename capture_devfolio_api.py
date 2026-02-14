from playwright.sync_api import sync_playwright
import json

def capture():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        def handle_response(response):
            url = response.url

            # print ALL XHR/Fetch calls
            if "graphql" in url or "hackathon" in url:
                print("\n=== API CALL ===")
                print("URL:", url)
                try:
                    print("Response snippet:")
                    print(response.text()[:500])
                except:
                    pass

        page.on("response", handle_response)

        page.goto("https://devfolio.co/hackathons/open")

        page.wait_for_timeout(10000)  # wait 10 seconds

        browser.close()

capture()
