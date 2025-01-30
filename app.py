from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_all_colleges(stream, city):
    driver = None
    try:
        options = Options()
        options.add_argument("--headless")  # Required for cloud execution
        options.add_argument("--no-sandbox")  # Helps in some environments
        options.add_argument("--disable-dev-shm-usage")  # Prevents memory issues
        options.add_argument("--window-size=1920,1080")  # Ensures elements are visible

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        base_url = f"https://www.collegedunia.com/{stream}/{city}-colleges"
        driver.get(base_url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'college_name')]"))
        )

        college_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'college_name')]")
        city_elements = driver.find_elements(By.XPATH, "//span[contains(@class, 'location')]")
        course_elements = driver.find_elements(By.XPATH, "//span[contains(@class, 'fee-shorm-form')]")

        colleges = []
        for i in range(len(college_elements)):
            college_name = college_elements[i].text.strip()
            city_name = city_elements[i].text.strip() if i < len(city_elements) else "N/A"
            course_name = course_elements[i].text.strip() if i < len(course_elements) else "N/A"
            colleges.append((college_name, city_name, course_name))

        return colleges

    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if driver:
            driver.quit()
