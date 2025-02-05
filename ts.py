from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions

chrome_options = ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")  # Recommended for headless
chrome_options.add_argument("--disable-dev-shm-usage")  # Add this line!

service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get("https://www.google.com")
    print("Tiêu đề trang Google:", driver.title)
except Exception as e:
    print("Lỗi khi tải trang:", e)
finally:
    driver.quit()