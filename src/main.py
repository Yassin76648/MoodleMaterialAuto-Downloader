import os
import time
import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from config import USER_NAME, PASSWORD, COURSES_PAGE
from downloaders import download_google_drive_files, download_google_native_docs, download_plugin_files, download_dir, save_video_links

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

        print("\n" + "="*80)
        print("                        MOODLE AUTO DOWNLOADER")
        print("="*80 + "\n")

        print("========================🚀 Starting Chrome... please wait ============================")
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
            print("\n" + "="*70)
            print("✅ Login successful!")
            print("="*70 + "\n")
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
        
        print(f"========================= ✅ Found {len(courses)} courses ==============================")
        return courses


def organize_downloads(course_name, semester_name="Semester !"):
    base_dir = os.path.join(os.path.expanduser("~"), "Desktop", "University", semester_name, course_name)
    temp_dir = os.path.abspath("downloads")

    # Define category logic
    extensions = {
        "PDFs": [".pdf"],
        "PPTs": [".pptx", ".ppt"],
        "Videos": [".mp4", ".mkv", ".mov", ".avi"],
        "Audio": [".mp3", ".wav"],
        "Documents": [".docx", ".doc", ".txt", ".xlsx"],
        "Zips": [".zip", ".rar", ".7z", ".tar", ".gz"], # New Category
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

        # --- SPECIAL LOGIC FOR TXT FILES ---
        if file_ext == ".txt":
            final_destination_dir = os.path.join(base_dir, category)
        else:
            sub_folder = "Other"
            for folder_name, exts in extensions.items():
                if file_ext in exts:
                    sub_folder = folder_name
                    break
            final_destination_dir = os.path.join(base_dir, category, sub_folder)

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
            print("\n===================== 🔁 Starting the download loop ==========================")
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
                            print("################## 🛑 Finished! ##################\n")
                            break

                    organize_downloads(course_name, semester_name)
                    input(f"Press Enter to launch next course : ")
                    # driver.get(url)

        else:
            # If login failed, stop here so we don't get 'No links found' errors
            print("🚫 Script stopped because login was not successful.")
            driver.quit()

if __name__ == "__main__":
    main()