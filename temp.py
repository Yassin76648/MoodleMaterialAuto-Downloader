import webbrowser
import gdown
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import subprocess
import requests
import os
import time
import os
import shutil
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, WebDriverException

# from urllib.parse import urlparse, unquote
from config import USER_NAME, PASSWORD

bad_link = ["https://el.sustech.edu/mod/page/view.php?id=98625"]
# Define the ADDRESS
download_dir = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
# Configuration object for Google Chrome
options = Options()
# Don't close the chrome window when code is finished
options.add_experimental_option("detach", True)
# Define the RULES
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
}
# Pack the rules into the SUITCASE
options.add_experimental_option("prefs", prefs)

session = requests.Session()
# START the browser with the suitcase
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
# Launch website
driver.get("https://el.sustech.edu")
wait = WebDriverWait(driver, 5)
# Type login credentials
wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USER_NAME)
wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD)
wait.until(EC.element_to_be_clickable((By.ID, "loginbtn"))).click()
driver.get("https://el.sustech.edu/my/courses.php")
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.aalink"))).click()
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.aalink"))).click()

while True:
    try:
        # try:
        #     download_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Download folder')]")))
        #     download_btn.click()
        # except TimeoutException:
        #     pass
        # try:
        #     yt_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'youtu.be')]")))
        #     video_url = yt_link.get_attribute("href")
        #     subprocess.run(["yt-dlp","--cookies", "cookies.txt",video_url])        
        # except TimeoutException:
        #     pass

        # this try download pptx, mp4, and pdf files
        # List of downladable files formats from google drive
        # file_format = ['PowerPoint', 'PDF', 'Plain text', 'MPEG-4', 'MP3']
        # found = False
        # for format in file_format:
        #     try:
        #         short_wait = WebDriverWait(driver, 2)
        #         drive_element = driver.find_element(By.CSS_SELECTOR, "#region-main > div:nth-child(4) > div > a")
                
        #         # Get the link from the element
        #         link = drive_element.get_attribute("href")

        #         # LOGIC: Only enter if "pluginfile.php" is NOT in the link
        #         if "pluginfile.php" not in link:
        #             drive_element.click()
                    
        #             # Navigate the menus (Arabic: ملف -> تنزيل)
        #             wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='ملف']"))).click()
        #             wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='تنزيل']"))).click()
                    
        #             # Find the specific format button
        #             element = short_wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{format}')]")))
        #             element.click()
                    
        #             print(f"Successfully started download for: {format}")
        #             found = True
        #             break # Exit the 'for format' loop because we found a match
        #     except Exception as e:
        #         continue # Try the next format in the list
        # # 3. Only wait and go back if we actually clicked something
        # if found:
        #     time.sleep(7) # Give it a bit more time just in case it's a large MP4/MP3
        #     driver.back()
        # else:
        #     print("Could not find any of the requested download formats.")
        # # end edit
        try:
            # store every downloadable link that contains pluginfile.php
            links = driver.find_elements(By.XPATH, "//a[contains(@href,'pluginfile.php')]")
            # Download them
            for link in links:
                try:
                    url = link.get_attribute("href")
                    if url:
                        driver.get(url)
                        time.sleep(1)
                except StaleElementReferenceException:
                    continue
        except TimeoutException:
            pass
        try:
            # clear cookies file if it exists.
            gdown_cache_file = os.path.expanduser('~/.cache/gdown/cookies.txt')
            if os.path.exists(gdown_cache_file):
                try:
                    os.remove(gdown_cache_file)
                    print("Cleared corrupted gdown cache.")
                except Exception as e:
                    print(f"Could not clear cache: {e}")
            links = driver.find_elements(By.XPATH, "//a[contains(@href,'drive.google')]")
            for link in links:
                url = link.get_attribute("href")     
                name = link.get_attribute("innerText").strip()
                file_save_path = os.path.join(download_dir, f"{name}.pdf")
                gdown.download(url, file_save_path, quiet=False, fuzzy=True)
        except Exception as e:
            # Instead of opening the browser, we just print the error and move on
            print(f"Skipping {url} because: {e}")
        # Press next page
        next_btn = wait.until(EC.element_to_be_clickable((By.ID, "next-activity-link")))
        next_btn.click()
    except TimeoutException:
        break
