import time
import asyncio
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

async def login(driver, login_url, username, password):
    """
    Thực hiện đăng nhập vào trang dựa trên URL và thông tin đăng nhập.
    """
    driver.get(login_url)
    
    # Đợi và điền thông tin đăng nhập
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Tên đăng nhập"]'))
    )
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Mật khẩu"]'))
    )
    
    username_input.send_keys(username)
    password_input.send_keys(password)
    
    time.sleep(2)
    # Xử lý checkbox và nút đăng nhập
    checkbox = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox']"))
    )
    driver.execute_script("arguments[0].click();", checkbox)
    
    login_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'button.btn.btn-primary.btn-login'))
    )
    driver.execute_script("arguments[0].click();", login_button)

async def handle_otp(driver, bot_handler, chat_id):
    """
    Xử lý nhập mã OTP và xác nhận.
    """
    try:
        otp_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Mã OTP"]'))
        )
        await bot_handler.send_message(chat_id, "Vui lòng nhập mã OTP được gửi đến điện thoại của bạn")
        otp_code = await bot_handler.get_otp(chat_id, timeout=60)
        if not otp_code:
            raise Exception("Không nhận được mã OTP")
        otp_input.send_keys(otp_code)
        
        # Nhấn nút xác nhận OTP
        confirm_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button.btn.btn-primary'))
        )
        driver.execute_script("arguments[0].click();", confirm_button)
        
    except Exception as e:
        print(f"Lỗi trong quá trình xử lý OTP: {str(e)}")
        driver.quit()
        exit(1) 