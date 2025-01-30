import streamlit as st
import pandas as pd
import time
import json
import gspread
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from oauth2client.service_account import ServiceAccountCredentials


# Function to get all colleges based on stream and city
def get_all_colleges(stream, city):
    driver = None
    try:
        options = Options()
        options.add_argument("--headless")  # Required for cloud execution
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        base_url = f"https://www.collegedunia.com/{stream}/{city}-colleges"
        print(f"Fetching URL: {base_url}")  # Debugging output
        driver.get(base_url)

        # Wait until the college list appears
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'college_name')]"))
        )

        college_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'college_name')]")
        city_elements = driver.find_elements(By.XPATH, "//span[contains(@class, 'location')]")
        course_elements = driver.find_elements(By.XPATH, "//span[contains(@class, 'fee-shorm-form')]")

        print(f"Found {len(college_elements)} colleges")  # Debugging output

        colleges = []
        for i in range(len(college_elements)):
            college_name = college_elements[i].text.strip()
            city_name = city_elements[i].text.strip() if i < len(city_elements) else "N/A"
            course_name = course_elements[i].text.strip() if i < len(course_elements) else "N/A"
            colleges.append((college_name, city_name, course_name))

        return colleges

    except Exception as e:
        print(f"ERROR: {e}")
        return None
    finally:
        if driver:
            driver.quit()


# Function to append DataFrame to Google Sheets
def append_to_gsheet(df, sheet_url):
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file"
        ]
        creds_dict = json.loads(st.secrets["gcp_service_account"])  # Load from Streamlit secrets
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
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
    sheet_url = st.text_input("🔗 Enter your Google Sheet URL:")

    if st.button("Scrape and Save to Google Sheets"):
        if stream and city and sheet_url:
            st.write("🔄 Fetching college data...")
            colleges = get_all_colleges(stream, city)

            if colleges:
                df = pd.DataFrame(colleges, columns=["College Name", "City", "Course Name"])
                st.dataframe(df)

                result = append_to_gsheet(df, sheet_url)
                st.success(result)
            else:
                st.write(f"⚠️ No colleges found for {stream} in {city}.")
        else:
            st.warning("⚠️ Please enter all required fields.")


if __name__ == "__main__":
    main()
