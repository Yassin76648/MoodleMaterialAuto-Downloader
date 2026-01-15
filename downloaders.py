import gdown
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import re
import time
import os
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from logs_manager import get_history, update_history

download_dir = os.path.join((os.getcwd()), "Downloads")


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

                if ".mp4" in url.lower():
                    continue

                if url in history:
                    print(f"⏭️ Already processed this URL: {history[url]}")
                    continue

                if url:
                    driver.get(url)
                    update_history(url, clean_name)
                    time.sleep(2)
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

