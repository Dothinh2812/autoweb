from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions

chrome_options = ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")  # Thường cần thiết trong headless

service = ChromeService(executable_path=ChromeDriverManager().install()) # WebDriverManager sẽ tự tìm chromedriver tương thích
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get("https://www.google.com")
    print("Tiêu đề trang Google:", driver.title)  # Kiểm tra xem trang có tải thành công không
except Exception as e:
    print("Lỗi khi tải trang:", e)
finally:
    driver.quit()