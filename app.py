import streamlit as st
import pandas as pd
import time
import gspread
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from oauth2client.service_account import ServiceAccountCredentials

# Function to get all colleges based on stream and city
def get_all_colleges(stream, city):
    driver_path = './chromedriver.exe'  # Replace with your ChromeDriver path
    service = Service(driver_path)
    options = Options()
    options.headless = True  
    driver = webdriver.Chrome(service=service, options=options)

    base_url = f"https://www.collegedunia.com/{stream}/{city}-colleges"
    driver.get(base_url)

    colleges = []
    
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='jsx-3230181281 college_name underline-on-hover']/h3"))
        )

        college_elements = driver.find_elements(By.XPATH, "//a[@class='jsx-3230181281 college_name underline-on-hover']")
        city_elements = driver.find_elements(By.XPATH, "//span[@class='jsx-3230181281 pr-1 location']")
        email_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'mailto:')]")
        course_elements = driver.find_elements(By.XPATH, "//span[@class='jsx-3230181281 fee-shorm-form']")

        for i in range(len(college_elements)):
            college_name = college_elements[i].find_element(By.XPATH, ".//h3").text.strip()
            city_name = city_elements[i].text.strip() if i < len(city_elements) else "N/A"
            email = email_elements[i].text.strip() if i < len(email_elements) else "N/A"
            course_name = course_elements[i].text.strip() if i < len(course_elements) else "N/A"

            colleges.append((college_name, city_name, email, course_name))

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()

    return colleges


# Function to append DataFrame to Google Sheets
def append_to_gsheet(df, sheet_url):
    try:
        scope = [
            "https://spreadsheets.google.com/feeds", 
            "https://www.googleapis.com/auth/spreadsheets", 
            "https://www.googleapis.com/auth/drive.file"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name("./your_credential.json", scope)
        client = gspread.authorize(creds)

        # Open the Google Sheet by URL
        sheet = client.open_by_url(sheet_url).sheet1  

        # Convert DataFrame to list of lists
        data = df.values.tolist()

        # Append data to the Google Sheet
        sheet.append_rows(data)

        return "✅ Data successfully added to Google Sheets!"

    except Exception as e:
        return f"⚠️ Error: {e}"


# Streamlit App main function
def main():
    st.title("📊 College Scraper with Google Sheets Upload")

    stream = st.text_input("🎓 Enter the stream (e.g., MBBS, Engineering, Law):").strip().lower()
    city = st.text_input("📍 Enter the city (e.g., Delhi, Bangalore, Mumbai):").strip().lower()
    sheet_url = st.text_input("🔗 Enter your Google Sheet URL:", value="https://docs.google.com/spreadsheets/d/1KxA6EYb1D7Xk_R9cQw6xnjtW6-mWyLd6HtYyuG_6MwE/edit?gid=0#gid=0")

    if st.button("Scrape and Save to Google Sheets"):
        if stream and city and sheet_url:
            st.write("🔄 Fetching college data...")
            colleges = get_all_colleges(stream, city)

            if colleges:
                df = pd.DataFrame(colleges, columns=["College Name", "City", "Email", "Course Name"])
                st.dataframe(df)

                result = append_to_gsheet(df, sheet_url)
                st.success(result)
            else:
                st.write(f"⚠️ No colleges found for {stream} in {city}.")
        else:
            st.warning("⚠️ Please enter all required fields.")

if __name__ == "__main__":
    main()
