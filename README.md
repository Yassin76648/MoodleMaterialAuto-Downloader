# 🎓 Moodle Automated Material Downloader

An intelligent Python automation tool that downloads and organizes all course materials from Moodle-based e-learning platforms. Designed specifically for Sudan University of Science and Technology students, but adaptable to any Moodle installation.

## ✨ Features

- 🤖 **Fully Automated** - Logs in and navigates through courses automatically
- 📚 **Smart Download Tracking** - Never downloads the same file twice
- 🗂️ **Intelligent Organization** - Automatically sorts files by course, type, and category
- 🎥 **Video Link Extraction** - Collects YouTube and browser video links for offline viewing
- ☁️ **Google Drive Support** - Downloads files from Google Drive links
- 📄 **Google Docs Conversion** - Converts Google Docs/Slides/Sheets to downloadable formats
- 💾 **Persistent Tracking** - Remembers what you've downloaded across sessions
- 📊 **Statistics** - Shows download progress and history

## 🎯 What It Downloads

- ✅ PDF documents
- ✅ PowerPoint presentations (PPT, PPTX)
- ✅ Word documents (DOC, DOCX)
- ✅ ZIP archives
- ✅ Google Drive files
- ✅ Google Docs/Slides/Sheets (converted to PDF/PPTX/XLSX)
- ✅ Excel spreadsheets
- 📝 YouTube and video links (saved to text file)

## 📋 Prerequisites

- Python 3.7 or higher
- Google Chrome browser installed
- Active Moodle account (e.g., Sudan University account)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Yassin76648/MoodleMaterialAuto-Downloader.git
cd MoodleMaterialAuto-Downloader
```

### 2. Install Required Packages

```bash
pip install -r requirements.txt
```

### 3. Update Configuration File

Add your student id and your password in the configuration file named `config.py` in the project directory:

```python
# config.py

# Your Moodle login credentials
USER_NAME = "your_student_id" 
PASSWORD = "your_password"

LOGIN_URL = "https://el.sustech.edu"
COURSES_PAGE = "https://el.sustech.edu/my/courses.php"
```

## 📦 Project Structure

```
MoodleMaterialAuto-Downloader/
│
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .gitignore                # Git ignore file
├── src/
│   ├── main.py               # Entry point of the script
│   ├── config.py             # Your credentials (DO NOT COMMIT)
│   ├── downloaders.py        # Logic for downloading YouTube links, video links, and Moodle files
│   ├── logs_manager.py       # Contains functions that handle history downloads
├── Downloads/                # Temporary download location
│   ├── lecture1.pdf
│   ├── slides.pptx
| 
├── download_history.json      # Tracking database (auto-generated)
│
└── Desktop/University/        # Final organized location
    └── Semester name/
        └── Data Structures/
            ├── Lectures/
            │   ├── PDFs/
            │   ├── PPTs/
            │   ├── ZIPs/
            │   └── course_name_labs_video_links.txt
            └── Labs/
                ├──PDFs/
                ├── PPTs/
                ├── ZIPs/
                └──course_name_labs_video_links.txt
```

## 🎮 Usage

### Basic Usage

```bash
python main.py
```

The script will:
1. Start the Chrome browser
2. Log in to Moodle
3. Fetch all your courses
4. Show previous download statistics
5. Download new materials only
6. Organize files automatically
7. Display final statistics

### First Run Example

```
================================================================================
                        MOODLE AUTO DOWNLOADER
================================================================================

========================🚀 Starting Chrome... please wait ============================
✅ Chrome started successfully!
📝 Attempting to enter credentials...

======================================================================
✅ Login successful!
======================================================================

📁 Fetching courses...
========================= ✅ Found 6 courses ==============================
أساسيات الأعمال => https://el.sustech.edu/course/view.php?id=33085
تفاعل الإنسان والحاسوب => https://el.sustech.edu/course/view.php?id=33088
مبادئ علوم البيانات => https://el.sustech.edu/course/view.php?id=33091
شبكات الحاسوب => https://el.sustech.edu/course/view.php?id=33090
نظم التشغيل => https://el.sustech.edu/course/view.php?id=33087
نظم إدارة قواعد البيانات => https://el.sustech.edu/course/view.php?id=33089

===================== 🔁 Starting the download loop ==========================
الفصل الخامس
 course : أساسيات الأعمال
➡️ Navigate to first course...
🔍 Scanning main course dashboard for videos...
⏭️ Navigate to first link in the course...
⏭️ Next Page...
⏭️ Next Page...
⏭️ Next Page...
⏭️ Next Page...
⏭️ Next Page...
⏭️ Next Page...
📥 Starting download: 0 1.pptx
✅ Download finished: 0 1.pptx
⏭️ Next Page...
📥 Starting download: Business Essentials 01 1.docx
✅ Download finished: Business Essentials 01 1.docx
⏭️ Next Page...
📥 Starting download: Business Essentials 002.docx
✅ Download finished: Business Essentials 002.docx
⏭️ Next Page...
📥 Starting download: Business Essentials 002.pptx
✅ Download finished: Business Essentials 002.pptx
⏭️ Next Page...
📥 Starting download: Business Essentials 03.pptx
✅ Download finished: Business Essentials 03.pptx
⏭️ Next Page...
📥 Starting download: Business Essentials 03.docx
✅ Download finished: Business Essentials 03.docx
⏭️ Next Page...
################## 🛑 Finished! ##################

Sorting files for: أساسيات الأعمال...
✅ Moved: 0 1.pptx -> Lectures\PPTs
✅ Moved: Business Essentials 002.docx -> Lectures\Documents
✅ Moved: Business Essentials 002.pptx -> Lectures\PPTs
✅ Moved: Business Essentials 01 1.docx -> Lectures\Documents
✅ Moved: Business Essentials 03.docx -> Lectures\Documents
✅ Moved: Business Essentials 03.pptx -> Lectures\PPTs
✅ Moved: تفاعل الإنسان والحاسوب_labs_video_links.txt -> Labs
✅ Moved: تفاعل الإنسان والحاسوب_lecture_video_links.txt -> Lectures
Press Enter to launch next course :
```

## ⚙️ Configuration Options

### File Organization

The script categorizes files automatically:

| Keyword in Filename | Category |
|---------------------|----------|
| "lab", "practical", "coding" | Labs |
| "assignment", "homework" | Assignments |
| Everything else | Lectures |

Files are then sorted by type:
- PDFs → `PDFs/`
- PowerPoints → `PPTs/`
- Documents → `Documents/`
- Text → txt
- Other → `Other/`

## 🔧 Advanced Features

If a professor updates files, you can reset tracking:

### Reset All Tracking

Delete the download_history.json file or Remove entries (urls) to force re-download.

### If a professor updates files, you can reset tracking:

Run the code it will skip already downloaded files

## 🐛 Troubleshooting

### "Chrome failed to start"

**Cause:** Chrome not installed or chromedriver incompatible

**Solution:**
```bash
# Update webdriver-manager
pip install --upgrade webdriver-manager

# Or manually specify Chrome path
options.binary_location = "/path/to/chrome"
```

### "Login failed"

**Cause:** Incorrect credentials or Moodle structure changed

**Solution:**
1. Verify credentials in `config.py`
2. Check if Moodle login page changed
3. Update selectors in `login_navigate_to_courses()`

### "Same file downloaded twice"

**Cause:** Filename variation or tracking not saved

**Solution:**
- Check `download_history.json` is being updated
- Ensure script completes without interruption

## 🔒 Security & Privacy

### Credential Safety

- ✅ Keep `config.py` in `.gitignore`
- ✅ Never commit credentials to GitHub

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contributions

- [ ] Support for other Moodle versions
- [ ] GUI interface
- [ ] Multi-threading for faster downloads
- [ ] Download resume capability
- [ ] Email notifications when new content is available
- [ ] Support for other file hosting services
- [ ] Automatic course detection and enrollment

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Users are responsible for:

- Complying with their university's terms of service
- Respecting copyright and intellectual property rights
- Using downloaded materials for personal study only
- Not sharing or distributing course materials

The authors are not responsible for any misuse of this tool.

## 🙏 Acknowledgments

- Built with [Selenium](https://www.selenium.dev/) for browser automation
- Uses [gdown](https://github.com/wkentaro/gdown) for Google Drive downloads
- Inspired by the need to manage e-learning materials efficiently

## 📧 Contact

**Project Maintainer:** Yassin Shaaban or Mohammed Fath Al-Rahman
**Email:** yassin.shaaban2004@gmail.com  
**University:** Sudan University of Science and Technology

## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ Basic download functionality
- ✅ Smart tracking system
- ✅ Google Drive support
- ✅ Automatic organization

### Version 2.0 (Planned)
- [ ] GUI interface (Tkinter/PyQt)
- [ ] Multi-threaded downloads
- [ ] Download scheduling
- [ ] Cloud backup integration
- [ ] Mobile app companion

### Version 3.0 (Future)
- [ ] AI-powered content categorization
- [ ] Automatic note-taking from videos
- [ ] Integration with note-taking apps
- [ ] Collaborative features

## 💡 Tips & Best Practices

1. **Run regularly** - Schedule the script to run weekly
2. **Check statistics** - Review what's being downloaded
3. **Backup tracker** - Save `download_tracker.json` periodically
4. **Monitor downloads** - Check the `Downloads/` folder for issues
5. **Update selectors** - If Moodle changes, update CSS selectors

## 🎓 For Students

This tool was created by a student, for students. It's designed to:
- Save time downloading course materials
- Keep your files organized automatically
- Help you focus on studying, not file management

**Study smart, not hard!** 📖

---

**Star ⭐ this repository if it helped you!**

**Have questions? Open an issue!**

**Want to contribute? Pull requests are welcome!**
