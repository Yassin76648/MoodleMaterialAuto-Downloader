import gdown
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import re
import time
import os
import shutil
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from config import USER_NAME, PASSWORD, COURSES_PAGE
import json

download_dir = os.path.join((os.getcwd()), "Downloads")
LOG_FILE = 'download_history.json'

def setup_chrome():
    try:
        options = Options()
        options.add_experimental_option("detach", True)

        try:
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
                print(f"Created folder: {download_dir}")
        except OSError as e:
            print(f"Error: Could not create download folder. {e}")
            return None

        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True # Downloads PDF instead of opening in browser
        }
        options.add_experimental_option("prefs", prefs)

        print("🚀 Starting Chrome... please wait.")
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            print("✅ Chrome started successfully!")
            return driver

        except WebDriverException as e:
            print(f"Browser failed to start. Possible causes:")
            print("- Chrome is not installed.")
            print("- Your internet is down (cannot download driver).")
            print(f"Detailed Error: {e}")
            return None

    except Exception as e:
        print(f"An unexpected error occurred during setup: {e}")
        return None


def login_navigate_to_courses(driver, USER_NAME, PASSWORD):
    try :
        # Try to open the website
        driver.get("https://el.sustech.edu")
        wait = WebDriverWait(driver, 10) # 10 for slower connections

        # Handle Login Fields
        print("📝 Attempting to enter credentials...")
        user_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        pass_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        
        user_field.clear() # Clear any old text first
        user_field.send_keys(USER_NAME)
        pass_field.clear()
        pass_field.send_keys(PASSWORD)

        wait.until(EC.element_to_be_clickable((By.ID, "loginbtn"))).click()

        # Check if login actually worked
        try:
            # wait for a Dashboard-only element
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".userbutton"))) 
            print("✅ Login successful!")
        except TimeoutException:
                print("❌ Login failed: Dashboard element not found.")
                return False

        time.sleep(3)
        # Navigate to courses
        driver.get(COURSES_PAGE)

        return True # Tell the rest of the script everything is okay

    except TimeoutException:
        print("Error: The page took too long to load (Internet issue).")
    except NoSuchElementException:
        print("Error: A button or text box was renamed or moved by the website.")
    except WebDriverException as e:
        print(f"A browser error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error happened: {e}")

    return False # If we hit any error above, we return False


def get_courses(driver):
        """Get list of all courses"""

        print("📁 Fetching courses...")
        driver.get(COURSES_PAGE)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "coursename"))
        )

        courses = []
        course_elements = driver.find_elements(By.CSS_SELECTOR, "a.coursename")

        for element in course_elements:
            url = element.get_attribute("href")

            try:
                multiline_span = element.find_element(By.CSS_SELECTOR, 'span.multiline')
                course_name = multiline_span.get_attribute("title")
                if not course_name:
                    course_name = element.find_element(By.CSS_SELECTOR, '[aria-hidden="true"]').text
            except:
                # Fallback if the structure is different for some links
                course_name = element.text.replace("Course name", "").strip()
            # Clean up any remaining whitespace or newlines
            course_name = " ".join(course_name.split())
            
            courses.append((course_name, url))
        
        print(f"✅ Found {len(courses)} courses\n")
        return courses


def download_plugin_files(driver):
    """
    Finds and downloads all links containing 'pluginfile.php' on the current page.
    """

    history = get_history() # Load the logbook

    try:
        if "Download folder" in driver.page_source:
            download_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Download folder')]")))
            download_btn.click()

            time.sleep(5)
            return
        # store every downloadable link that contains pluginfile.php
        links = driver.find_elements(By.XPATH, "//a[contains(@href,'pluginfile.php')]")
        # Download them
        for link in links:
            try:
                url = link.get_attribute("href")

                raw_name = link.get_attribute("innerText").strip() or "Plugin_file"
                clean_name = re.sub(r'[<>:"/\\|?*]', '_', raw_name) # SANITIZE: Remove characters Windows hates (< > : " / \ | ? *)

                if url in history:
                    print(f"⏭️ Already processed this URL: {history[url]}")
                    continue

                if url:
                    driver.get(url)
                    time.sleep(2)
            except StaleElementReferenceException:
                continue
            update_history(url, clean_name)
    except TimeoutException:
        pass
    except Exception as e:
        print(f"An error occurred during the scanning process: {e}")
        return False


def download_google_drive_files(driver):

    history = get_history()
    # Clear gdown cache to avoid cookie errors
    gdown_cache_file = os.path.expanduser('~/.cache/gdown/cookies.txt')
    if os.path.exists(gdown_cache_file):
        try:
            os.remove(gdown_cache_file)
        except:
            pass

    try:
        # Find all Google Drive links
        links = driver.find_elements(By.XPATH, "//a[contains(@href,'drive.google')]")

        
        for link in links:
            url = link.get_attribute("href")

            # ---- THE CHECK ----
            if url in history:
                print(f"⏭️ Already processed this URL: {history[url]}")
                continue

            # Get the text "Lecture_01.pptx"
            raw_name = link.get_attribute("innerText").strip() or "GDrive_File"
            clean_name = re.sub(r'[<>:"/\\|?*]', '_', raw_name) # SANITIZE: Remove characters Windows hates (< > : " / \ | ? *)

            # If no extension is found, we can't guess, so we save it as is
            save_path = os.path.join(download_dir, clean_name)

            print(f"🔽 Attempting to download: {clean_name}")
            try:
                # fuzzy=True is key here as it converts /view and /edit links to download links
                gdown.download(url, save_path, quiet=False, fuzzy=True)
            except Exception as e:
                print(f"❌ Failed to download {clean_name}: {e}")

            update_history(url, clean_name)

    except Exception as e:
        print(f"🔎 Error scanning for Google Drive links: {e}")



def download_google_native_docs(driver):
    """
    Specifically handles Google Docs, Slides, and Sheets by converting 
    them into downloadable formats (PDF, PPTX, XLSX).
    """
    history = get_history()

    try:
        # 1. Target only 'docs.google.com' links
        links = driver.find_elements(By.XPATH, "//a[contains(@href,'docs.google.com')]")

        if not links:
            return # Exit silently if none found

        print(f"📄 Found {len(links)} Google Native documents. Converting...")

        for link in links:
            url = link.get_attribute("href")

            if url in history:
                print(f"⏭️ Already processed this URL: {history[url]}")
                continue

            raw_name = link.get_attribute("innerText").strip() or "Untitled_Document"

            # Sanitize filename (remove Windows illegal characters)
            clean_name = re.sub(r'[<>:"/\\|?*]', '_', raw_name)

            # Identify the type and build the Export URL
            if "/presentation/" in url:      # Presentation -> PowerPoint
                export_url = url.split('/edit')[0] + "/export/pptx"
                filename = f"{clean_name}.pptx"
            
            elif "/document/" in url:         # Document -> PDF
                export_url = url.split('/edit')[0] + "/export?format=pdf"
                filename = f"{clean_name}.pdf"
            
            elif "/spreadsheets/" in url:     # Spreadsheet -> Excel
                export_url = url.split('/edit')[0] + "/export?format=xlsx"
                filename = f"{clean_name}.xlsx"
            
            else:
                # If it's a docs link we don't recognize, skip it to be safe
                continue

            # 3. Download the converted file
            save_path = os.path.join(download_dir, filename)
            
            try:
                print(f"🔄 Exporting {filename}...")
                # We use fuzzy=True because the export URL structure is simple
                gdown.download(export_url, save_path, quiet=False, fuzzy=True)
            except Exception as e:
                print(f"❌ Failed to export {filename}: {e}")

            update_history(url, clean_name)

    except Exception as e:
        print(f"⚠️ Error in Google Docs function: {e}")


def save_video_links(driver, course_name):
    safe_name = "".join([c for c in course_name if c.isalnum() or c in (' ', '_')]).rstrip()
    file_path = os.path.join(download_dir, f"{safe_name}_video_links.txt")

    # Get the entire HTML source of the page
    page_source = driver.page_source

    # Pattern for YouTube handles standard and short links
    yt_pattern = r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+|https?://youtu\.be/[\w-]+'
    
    # Pattern for Pluginfile MP4s grabs the link until the .mp4 extension
    plugin_pattern = r'https?://[^\s"\'<>]+pluginfile\.php/[^\s"\'<> ]+\.mp4'

    # Find all matches
    yt_matches = re.findall(yt_pattern, page_source)
    plugin_matches = re.findall(plugin_pattern, page_source)
    
    # Combine them and remove duplicates
    all_found_urls = list(set(yt_matches + plugin_matches))

    # Filter against existing links in your file
    existing_urls = set()
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            existing_urls = {line.split("=> ")[-1].strip() for line in f if "=> " in line}

    # Try to get the breadcrumb
    try:
        breadcrumb = driver.find_element(By.CSS_SELECTOR, "ol.breadcrumb").text
        page_label = breadcrumb.split('\n')[-1] 
    except:
        raw_title = driver.title
        page_label = re.sub(r'\d{10,}', '', raw_title).strip() # Removes any number 10 digits or longer

    # If the label is still empty or messy, use a default
    if not page_label or page_label == ":":
        page_label = "Course Video"

    # Save new findings
    new_count = 0
    with open(file_path, "a", encoding="utf-8") as f:
        for url in all_found_urls:
            url_clean = url.strip()
            if url_clean not in existing_urls:
                # Since Regex doesn't give us the 'Title', we use a generic label
                label = "Youtube link" if "youtu" in url_clean else "Browser video link"
                
            url_clean = url.strip()
            if url_clean not in existing_urls:
                # Try to find the title by looking for the anchor tag with this URL
                try:
                    link_element = driver.find_element(By.XPATH, f"//a[contains(@href, '{url_clean}')]")
                    title = link_element.text.strip()
                except:
                    title = page_label # Fallback to the cleaned page title
                
                f.write(f"# {title} {label} => {url_clean}\n")
                print(f"🎯 Regex found: {url_clean}")
                new_count += 1

    if new_count > 0:
        print(f"✅ Added {new_count} new unique links to {safe_name}")



def organize_downloads(course_name, semester_name="Semester !"):
    base_dir = os.path.join(os.path.expanduser("~"), "Desktop", "University", semester_name, course_name)
    temp_dir = os.path.abspath("downloads")

    # Define category logic
    extensions = {
        "PDFs": [".pdf"],
        "PPTs": [".pptx", ".ppt"],
        "Videos": [".mp4", ".mkv", ".mov", ".avi"],
        "Audio": [".mp3", ".wav"],
        "Documents": [".docx", ".doc", ".txt", ".xlsx"]
    }

    print(f"Sorting files for: {course_name}...")

    # Process every file in the temp downloads folder
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        
        # Skip folders, only process files
        if not os.path.isfile(file_path):
            continue

        # Determine if it's a 'Lab' or 'Lecture' based on filename
        category = "Lectures" # Default
        if "lab" in filename.lower() or "practical" in filename.lower() or "coding" in filename.lower() or "code" in filename.lower():
            category = "Labs"
        elif "assignment" in filename.lower() or "homework" in filename.lower():
            category = "Assignments"

        # Determine the file type folder (PDFs, PPTs, etc.)
        file_ext = os.path.splitext(filename)[1].lower()
        sub_folder = "Other" # Default
        for folder_name, exts in extensions.items():
            if file_ext in exts:
                sub_folder = folder_name
                break

        # Create the full destination path
        final_destination_dir = os.path.join(base_dir, category, sub_folder)
        os.makedirs(final_destination_dir, exist_ok=True)

        # Move the file
        try:
            shutil.move(file_path, os.path.join(final_destination_dir, filename))
            print(f"✅ Moved: {filename} -> {category}/{sub_folder}")
        except Exception as e:
            print(f"❌ Error moving {filename}: {e}")


def main():
    driver = setup_chrome()

    if driver:
        # Capture the result of the login function
        login_success = login_navigate_to_courses(driver, USER_NAME, PASSWORD)  
        time.sleep(3)      
        # ONLY if login worked, start the scavenge loop
        if login_success:
            # get courses in list
            courses = get_courses(driver)
            for name, url in courses:
                print(f"{name} => {url}")
            print("🔁 Starting the download loop...")
            if courses:
                semester_element = driver.find_element(By.CSS_SELECTOR, "span.categoryname")
                semester_name = semester_element.text
                print(semester_name)
                # test with first course
                for name, url in courses:

                    course_name = name

                    print(f" course : {course_name}")
                    print("➡️ Navigate to first course...")


                    driver.get(url)
                    print("🔍 Scanning main course dashboard for videos...")
                    save_video_links(driver, course_name)

                    print("➡️ Navigate to first link in the course...")


                    try :
                        WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.aalink"))
                        ).click()
                    except:
                        WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn btn-icon me-3 icons-collapse-expand"))).click()

                        WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.aalink"))).click()

                    while True:
                        # Your scavenger functions here
                        if "pluginfile.php" in driver.page_source or "Download folder" in driver.page_source:
                            download_plugin_files(driver)
                            
                        if "drive.google" in driver.page_source:
                            download_google_drive_files(driver)
                            
                        if "docs.google" in driver.page_source:
                            download_google_native_docs(driver)

                        # if "youtube.com" in driver.page_source or "youtu.be" in driver.page_source or ".mp4" in driver.page_source or "<source" in driver.page_source:
                        save_video_links(driver, course_name)
                        # Check for next page
                        try:
                            print("➡️ Next Page...")
                            next_btn = driver.find_element(By.ID, "next-activity-link")
                            next_btn.click()
                        except NoSuchElementException:
                            print("🛑 Finished!")
                            break

                    organize_downloads(course_name, semester_name)
                    input("Next Course...")
                    # driver.get(url)

        else:
            # If login failed, stop here so we don't get 'No links found' errors
            print("🚫 Script stopped because login was not successful.")
            driver.quit()



def get_history():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {}

def update_history(url, file_name):
    history = get_history()
    history[url] = file_name
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump(history, f, indent=4)


if __name__ == "__main__":
    main()