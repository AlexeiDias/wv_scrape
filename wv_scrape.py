import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Create a new instance of the Chrome driver
driver = webdriver.Chrome()

# Function to extract information between markers and save as JSON


def extract_and_save_property_info():
    try:
        # Find the table with the results
        results_table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-striped"))
        )

        # Find all rows in the table
        rows = results_table.find_elements(By.TAG_NAME, "tr")

        # List to store property information dictionaries
        properties_list = []

        # Variable to track whether we are between the markers
        between_markers = False

        # Dictionary to store current property information
        property_info = {}

        # Loop through rows
        for row in rows:
            # Extract text from the row
            row_text = row.text.strip()

            # Check for the start marker
            if "Cert No" in row_text:
                if property_info:
                    # Add current property_info to the list
                    properties_list.append(property_info)
                    property_info = {}  # Reset the dictionary

                between_markers = True
                continue

            # Check for the end marker
            elif "Status" in row_text:
                between_markers = False
                continue

            # If between markers, extract information
            elif between_markers:
                # Handle specific keyword rows
                if "Cert No" in row_text:
                    # Extract Cert No using appropriate logic
                    cert_no = row.find_element(
                        By.ID, "UltraWideContent_lvResults_lblCertNo_0").text
                    property_info["Cert No"] = cert_no
                elif "County" in row_text:
                    # Extract County using appropriate logic
                    county = row_text.split(":", 1)[1].strip()
                    property_info["County"] = county
                # Add more conditions for other key-value pairs...

                # If no specific keyword is found, try the general key-value pair extraction
                split_row = [item.strip() for item in row_text.split(":", 1)]
                if len(split_row) >= 2:
                    key, value = split_row[0], split_row[1]
                    # Add key-value pair to property_info dictionary
                    property_info[key] = value
                else:
                    print(f"Skipping row: {row_text}")
                    continue  # Skip to the next iteration of the loop

        # Save properties_list as JSON
        with open("deep_research_result_file_level_1.json", "w") as json_file:
            json.dump(properties_list, json_file, indent=2)

        print("Property information saved to deep_research_result_file_level_1.json")

    except Exception as e:
        print(f"Error during information extraction: {e}")


# Open the webpage
driver.get("https://www.wvsao.gov/CountyCollections/Default")

# Find the dropdown element and select the option with value "4" (No Bid)
status_dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "ctl00$UltraWideContent$ddStatus")))
status_dropdown.find_element(By.CSS_SELECTOR, "option[value='4']").click()

# Find and click the Search button
search_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "UltraWideContent_btnSearch")))
search_button.click()

# Extract and save information for all properties
extract_and_save_property_info()

# Find the first <a> tag with the "View Map" text and click on it
view_map_link = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'View Map')]")))
view_map_link.click()

# Wait for the user to press Enter before closing the browser
input("Press Enter to close the browser...")

# Close the browser window
driver.quit()
