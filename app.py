from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import asyncio
import time
import os
import glob
import shutil
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from auth import login, handle_otp
from telegram_bot import TelegramBotHandler

# Cấu hình
CHROME_DRIVER_PATH = r"G:\My Drive\App- baocao\Dieukhienweb\chromedriver-win64\chromedriver.exe"
TELEGRAM_TOKEN = "7810323512:AAEL6hDjjZgz64gADrJfcKwrqO42himl3oI"
CHAT_ID = "1125088525"
LOGIN_URL = "https://onebss.vnpt.vn/#/auth/login"

# Đường dẫn thư mục
# Giả sử trình duyệt tải file về thư mục tải xuống mặc định
DOWNLOAD_FOLDER_TEMP = r"C:\Users\thinhdx-hni\Downloads"
# Sau đó chuyển file báo cáo vào thư mục này (DOWNLOAD_FOLDER_PTTB)
DOWNLOAD_FOLDER_PTTB = r"C:\Users\thinhdx-hni\Downloads\pttb"
DOWNLOAD_FOLDER_DHSC = r"C:\Users\thinhdx-hni\Downloads\dhsc"
# URL báo cáo cần mở
REPORT_URL = (
    "https://onebss.vnpt.vn/#/report/bi?"
    "path=TINH%2FHANOI%2FHNI_PTTB_001%2FRP_HNI_PTTB_001&"
    "name=2.%20%5BHNI.PTTB.001%5D-B%C3%A1o%20c%C3%A1o%20phi%E1%BA%BFu%20t%E1%BB%93n%20d%E1%BB%8Bch%20v%E1%BB%A5%20chi%20ti%E1%BA%BFt%20%28online%3A%20Ng%C3%B4%20V%C4%83n%20L%C6%B0u%20%29"
)

# URL báo cáo DHSC cần mở
REPORT_URL_DHSC = (
    "https://onebss.vnpt.vn/#/report/bi?"
    "path=TINH%2FHANOI%2FHNI_BHSC_005%2FRP_HNI_BHSC_005&"
    "name=2.%20%5BHNI.BHSC.005%5D-B%C3%A1o%20c%C3%A1o%20t%E1%BB%93n%20s%E1%BB%ADa%20ch%E1%BB%AFa%20%28online%3A%20Ng%C3%B4%20V%C4%83n%20L%C6%B0u%20%29"
)

# Thông tin đăng nhập
USERNAME = "thinhdx.hni"
PASSWORD = "T#g6542u"

# Khởi tạo driver và bot
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Chạy ở chế độ ẩn
options.add_argument("--disable-gpu")  # Tắt GPU nếu cần
# Thiết lập kích thước màn hình ảo (nếu cần)
options.add_argument("window-size=1920,1080")

service = Service(executable_path=CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)
driver.set_window_size(1920, 1080)  # Thiết lập kích thước cửa sổ ảo

bot_handler = TelegramBotHandler(TELEGRAM_TOKEN)
bot_handler.start_bot()



async def download_report_pttb(driver, report_url, download_dest_folder, wait_time=5):
    """
    Mở URL báo cáo, tải file Excel mới xuống và chuyển file vào thư mục DOWNLOAD_FOLDER_PTTB.
    """
    # Mở trang URL báo cáo
    driver.get(report_url)
    print("Đã mở trang URL báo cáo:", report_url)
    await asyncio.sleep(wait_time)  # Đợi trang báo cáo load
    
    # Click dropdown "Xem báo cáo"
    dropdown_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "dropdown-1__BV_toggle_"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_button)
    await asyncio.sleep(1)
    driver.execute_script("arguments[0].click();", dropdown_button)
    print("Đã click chọn dropdown 'Xem báo cáo'")
    
    # Chọn tùy chọn "Xuất XLSX -"
    export_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Xuất XLSX -')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", export_option)
    await asyncio.sleep(1)
    driver.execute_script("arguments[0].click();", export_option)
    print("Đã click chọn tùy chọn 'Xuất XLSX -'")
    
    # Ghi nhận thời điểm bắt đầu tải file mới
    start_time = time.time()
    
    # Chờ file mới được tải xuống trong thư mục tải file mặc định
    timeout = 120  # thời gian chờ tối đa (giây)
    new_file = None
    while time.time() - start_time < timeout:
        xlsx_files = glob.glob(os.path.join(DOWNLOAD_FOLDER_TEMP, "*.xlsx"))
        for file in xlsx_files:
            # Chỉ nhận file có thời gian chỉnh sửa sau khi nhấn xuất báo cáo
            if os.path.getmtime(file) > start_time:
                new_file = file
                break
        if new_file:
            break
        time.sleep(1)
    
    if new_file:
        print("Đã tải xuống file mới:", os.path.basename(new_file))
        # Chuyển file đã tải xuống sang thư mục DOWNLOAD_FOLDER_PTTB
        destination_path = os.path.join(download_dest_folder, os.path.basename(new_file))
        try:
            shutil.move(new_file, destination_path)
            print("Đã chuyển file đến:", destination_path)
        except Exception as e:
            print("Lỗi khi chuyển file:", str(e))
    else:
        print("Không tìm thấy file Excel được tải xuống sau {} giây.".format(timeout))

'''


async def download_report_dhsc(driver, report_url, download_dest_folder, wait_time=5):
    """
    Mở URL báo cáo DHSC, thực hiện tìm kiếm với từ khóa "08", sau đó tải file Excel mới xuống
    và chuyển file vào thư mục DOWNLOAD_FOLDER_DHSC.
    """
    # Mở trang URL báo cáo
    driver.get(report_url)
    print("Đã mở trang URL báo cáo:", report_url)
    await asyncio.sleep(wait_time)  # Đợi trang báo cáo load

    # Tìm đến trường tìm kiếm trong dropdown và nhập "08", sau đó enter
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span.select2-search.select2-search--dropdown > input.select2-search__field"))
    )
    search_input.send_keys("08")
    search_input.send_keys(Keys.ENTER)
    await asyncio.sleep(1)
    
    # Tiến hành click dropdown "Xem báo cáo"
    dropdown_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "dropdown-1__BV_toggle_"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_button)
    await asyncio.sleep(1)
    driver.execute_script("arguments[0].click();", dropdown_button)
    print("Đã click chọn dropdown 'Xem báo cáo'")
    
    # Chọn tùy chọn "Xuất XLSX -"
    export_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Xuất XLSX -')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", export_option)
    await asyncio.sleep(1)
    driver.execute_script("arguments[0].click();", export_option)
    print("Đã click chọn tùy chọn 'Xuất XLSX -'")
    
    # Ghi nhận thời điểm bắt đầu tải file mới
    start_time = time.time()
    
    # Chờ file mới được tải xuống trong thư mục tải file mặc định
    timeout = 120  # Thời gian chờ tối đa (giây)
    new_file = None
    while time.time() - start_time < timeout:
        xlsx_files = glob.glob(os.path.join(DOWNLOAD_FOLDER_TEMP, "*.xlsx"))
        for file in xlsx_files:
            # Chỉ nhận file có thời gian chỉnh sửa sau thời điểm nhấn xuất báo cáo
            if os.path.getmtime(file) > start_time:
                new_file = file
                break
        if new_file:
            break
        time.sleep(1)
    
    if new_file:
        print("Đã tải xuống file mới:", os.path.basename(new_file))
        # Chuyển file đã tải xuống sang thư mục DOWNLOAD_FOLDER_DHSC
        destination_path = os.path.join(download_dest_folder, os.path.basename(new_file))
        try:
            shutil.move(new_file, destination_path)
            print("Đã chuyển file đến:", destination_path)
        except Exception as e:
            print("Lỗi khi chuyển file:", str(e))
    else:
        print("Không tìm thấy file Excel được tải xuống sau {} giây.".format(timeout))

'''
async def main():
    try:
        # Gọi hàm đăng nhập
        await login(driver, LOGIN_URL, USERNAME, PASSWORD)
        # Xử lý nhập mã OTP
        await handle_otp(driver, bot_handler, CHAT_ID)
        # Sau khi đăng nhập và OTP thành công, giữ trạng thái đăng nhập và tải báo cáo mỗi 5 phút
        while True:
            print("Bắt đầu tải báo cáo PTTB...")
            await download_report_pttb(driver, REPORT_URL, DOWNLOAD_FOLDER_PTTB)
            print("Đã tải báo cáo PTTB. Chờ 5 phút để tải báo cáo lần tiếp theo...")
            await asyncio.sleep(300)  # Chờ 300 giây (5 phút)
    except KeyboardInterrupt:
        print("\nĐã dừng chương trình theo yêu cầu")
    finally:
        driver.quit()

if __name__ == "__main__":
    asyncio.run(main())