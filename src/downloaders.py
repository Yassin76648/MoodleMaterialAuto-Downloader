import os
import re
import time
import os
import gdown
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from logs_manager import get_history, update_history

download_dir = os.path.join((os.getcwd()), "Downloads")

def wait_for_download_complete(directory, timeout=300):
    """
    Waits for all Chrome temporary download files (.crdownload) to disappear.
    """
    seconds = 0
    while seconds < timeout:
        # Check if any file in the directory ends with .crdownload
        files = os.listdir(directory)
        if not any(f.endswith('.crdownload') for f in files):
            return True # Download complete
        
        time.sleep(1)
        seconds += 1
    return False # Timed out


def download_plugin_files(driver):
    """
    Finds and downloads all links containing 'pluginfile.php' on the current page.
    """
    
    history = get_history() # Load the logbook

    try:
        if "Download folder" in driver.page_source:
            folder_url = driver.current_url.split('&')[0] # Clean the URL
            if folder_url in history:
                print(f"⏭️ Already processed this URL: {history[url]}")
            else:
                try :
                    download_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Download folder')]")))
                    folder_name = driver.find_element(By.TAG_NAME, "h2").text.strip() or "Course_Folder"

                    print(f"⏳ Downloading folder ... waiting for completion.")
                    download_btn.click()
                    if wait_for_download_complete(download_dir):
                        print("✅ Folder download complete.")
                        update_history(folder_url, folder_name)
                    return
                except:
                    pass

        # store every downloadable link that contains pluginfile.php
        links = driver.find_elements(By.XPATH, "//a[contains(@href,'pluginfile.php')]")
        # Download them
        for link in links:
            try:
                url = link.get_attribute("href")

                raw_name = link.get_attribute("innerText").strip() or "Plugin_file"
                clean_name = re.sub(r'[<>:"/\\|?*]', '_', raw_name) # SANITIZE: Remove characters Windows hates (< > : " / \ | ? *)

                if ".mp4" in url.lower():
                    continue

                if url in history:
                    print(f"⏭️ Already processed this URL: {history[url]}")
                    continue

                if url:
                    print(f"📥 Starting download: {clean_name}")
                    driver.get(url)

                if wait_for_download_complete(download_dir):
                    print(f"✅ Download finished: {clean_name}")
                    update_history(url, clean_name)
                else:
                    print(f"⚠️ Warning: Download for {clean_name} timed out.")
            except StaleElementReferenceException:
                continue
            
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

            save_path = os.path.join(download_dir, clean_name)

            print(f"🔽 Attempting to download: {clean_name}")
            try:
                # fuzzy=True is key here as it converts /view and /edit links to download links
                result = gdown.download(url, save_path, quiet=False, fuzzy=True)
                if result:
                    update_history(url, clean_name)
            except Exception as e:
                print(f"❌ Failed to download {clean_name}: {e}")


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

            # Download the converted file
            save_path = os.path.join(download_dir, filename)

            try:
                print(f"🔄 Exporting {filename}...")
                # We use fuzzy=True because the export URL structure is simple
                result = gdown.download(export_url, save_path, quiet=False, fuzzy=True)
                if result:
                    update_history(url, clean_name)
            except Exception as e:
                print(f"❌ Failed to export {filename}: {e}")


    except Exception as e:
        print(f"⚠️ Error in Google Docs function: {e}")


def save_video_links(driver, course_name):
    safe_name = "".join([c for c in course_name if c.isalnum() or c in (' ', '_')]).rstrip()
    
    # Define the two file paths
    lab_path = os.path.join(download_dir, f"{safe_name}_labs_video_links.txt")
    lec_path = os.path.join(download_dir, f"{safe_name}_lecture_video_links.txt")

    page_source = driver.page_source
    yt_pattern = r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+|https?://youtu\.be/[\w-]+'
    plugin_pattern = r'https?://[^\s"\'<>]+pluginfile\.php/[^\s"\'<> ]+\.mp4'

    all_found_urls = list(set(re.findall(yt_pattern, page_source) + re.findall(plugin_pattern, page_source)))

    # Load existing URLs from BOTH files to prevent duplicates
    existing_urls = set()
    for path in [lab_path, lec_path]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                existing_urls.update({line.split("=> ")[-1].strip() for line in f if "=> " in line})

    # Get Breadcrumb/Label logic
    try:
        breadcrumb = driver.find_element(By.CSS_SELECTOR, "ol.breadcrumb").text
        page_label = breadcrumb.split('\n')[-1] 
    except:
        page_label = re.sub(r'\d{10,}', '', driver.title).strip()

    if not page_label or page_label == ":":
        page_label = "Course Video"

    new_count = 0
    for url in all_found_urls:
        url_clean = url.strip()
        if url_clean not in existing_urls:
            # Determine the Title
            try:
                link_element = driver.find_element(By.XPATH, f"//a[contains(@href, '{url_clean}')]")
                title = link_element.text.strip()
            except:
                title = page_label 

            label_type = "Youtube link" if "youtu" in url_clean else "Browser video link"
            
            # Categorization Logic
            # check both the video title and the page label for "Lab" keywords
            lab_keywords = ['lab', 'معمل', 'لاب', 'practical', 'تجربة']
            is_lab = any(kw in title.lower() or kw in page_label.lower() for kw in lab_keywords)
            
            target_file = lab_path if is_lab else lec_path
            
            # Write to the specific file
            with open(target_file, "a", encoding="utf-8") as f:
                f.write(f"# {title} {label_type} => {url_clean}\n")
            
            print(f"🎯 {'Lab' if is_lab else 'Lecture'} found: {url_clean}")
            existing_urls.add(url_clean) # Add to set so we don't save it twice in the same run
            new_count += 1

    if new_count > 0:
        print(f"✅ Sorted {new_count} new links for {safe_name}")
