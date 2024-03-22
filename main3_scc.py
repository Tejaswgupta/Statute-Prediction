import csv
import os
from datetime import datetime

import pandas as pd
import pg8000
import psycopg2
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

cnx = psycopg2.connect(user="tejasw", password="Password1234",
                       host="legalscraperserver.postgres.database.azure.com", port=5432, database="postgres")



def check_case_exists(case_name):
    try:
        cursor = cnx.cursor()
        select_query = "SELECT COUNT(*) FROM scc_table WHERE case_name = %s"
        
        # Execute the SELECT query with the provided scc_id
        cursor.execute(select_query, (case_name,))
        
        # Fetch the result
        result = cursor.fetchone()
        
        # Check if any rows exist with the provided scc_id
        if result[0] > 0:
            return True  # Case exists
        else:
            return False  # Case does not exist
        
    except (Exception, psycopg2.Error) as error:
        print("Error while checking case existence in PostgreSQL:", error)
        return False  # Return False if an error occurs


def add_entry(bench_name, court_name, case_name, case_no, date, advocates, citations,case_text,scc_id):
    try:
        cursor = cnx.cursor()
        insert_query = """
           INSERT INTO scc_table (bench_name, court_name, case_name, case_no, date, advocates, citations,case_text,scc_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data = (bench_name, court_name, case_name, case_no, date, advocates, citations,case_text,scc_id)
        cursor.execute(insert_query, data)

        cnx.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error while inserting data into PostgreSQL:", error)
        cnx.rollback() 


from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

service = Service(executable_path=ChromeDriverManager().install())
options = webdriver.ChromeOptions()

driver = webdriver.Chrome(service=service, options=options)
# Open the main URL
main_url = 'https://www.scconline.com/'  # Replace with the actual main URL
driver.get(main_url)

wait = WebDriverWait(driver, 50)

try:
    notif_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div/div/div[2]/button[2]')))
    notif_link.click()
except Exception as e:
    print(e)

button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.close')))
driver.implicitly_wait(40)
button.click()

try:
    wait.until(EC.presence_of_element_located(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.close')))).click()
    print('accepted cookies')
except Exception as e:
    print('no cookie button!')

try:
    # Find and click the "LOGIN" link
    login_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'a#login-link-navbar.menu__link')))
    login_link.click()
except Exception as e:
    print(e)

# Handle the popup (replace with your login logic)
username_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, 'loginid')))
password_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, 'pass')))
login_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'big-btn')))

username_input.send_keys('Advbharatbagla@gmail.com')
password_input.send_keys('Bharat@1993')
login_button.click()

# Switch back to the main window
# driver.switch_to.window(driver.window_handles[0])

browse_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    (By.XPATH, '/html/body/form/section/div[2]/div[3]/div/div[2]/div/div[2]/div[3]/div')))
driver.execute_script(browse_link.get_attribute('onclick'))
# browse_link.click()

india_link = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
    (By.XPATH, '/html/body/form/div[13]/div[1]/div[2]/div[1]/div[2]/div[3]/div[2]/ul/li/ul/li[1]/span/span')))
india_link.click()

driver.implicitly_wait(50)

india_link = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
    (By.XPATH, '/html/body/form/div[13]/div[1]/div[2]/div[1]/div[2]/div[3]/div[2]/ul/li/ul/li[1]/span/span')))
india_link.click()

sc_link = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
    (By.XPATH, '/html/body/form/div[13]/div[1]/div[2]/div[1]/div[2]/div[3]/div[2]/ul/li/ul/li[1]/ul/li[1]/span/span')))
sc_link.click()

driver.implicitly_wait(50)

base_xpath = '/html/body/form/div[13]/div[1]/div[2]/div[1]/div[2]/div[3]/div[2]/ul/li/ul/li[1]/ul/li[1]'


def navigate_nested_lists(driver, base_xpath):
    for year_index in range(1, 9):
        current_xpath = f"{base_xpath}/ul/li[{year_index}]"
        try:
            current_link = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, current_xpath)))
            current_link.click()
            navigate_year(driver, current_xpath)
            if 'dynatree-lastsib' in current_link.get_attribute('class'):
                print('Last section found')
                break

        except Exception as e:
            print(f"Exception: {e}")
            print("Backtracking section...")

            stay_login = "/html/body/div[4]/div[3]/div/button[1]/span"
            close_button = driver.find_element(By.XPATH,
                                               stay_login)
            close_button.click()

            backtrack_xpath = f"{base_xpath}/ul/li[{year_index + 1}]"
            print(backtrack_xpath)
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, backtrack_xpath)))


def navigate_year(driver, base_xpath):
    for depth in range(1, 5):
        print("year")
        current_xpath = f"{base_xpath}/ul/li[{depth}]"
        try:
            # Wait for the element to be clickable
            current_link = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, current_xpath)))
            current_link.click()
            navigate_month(driver, current_xpath)
            if 'dynatree-lastsib' in current_link.get_attribute('class'):
                print('Last year found')
                break
                # Move to the next depth

        except Exception as e:
            print('Backtracking year')


def navigate_month(driver, base_xpath):
    for depth in range(1, 12):
        print("month")
        try:
            current_xpath = f"{base_xpath}/ul/li[{depth}]"
            # Wait for the element to be clickable
            print(f"month: {current_xpath}")
            current_link = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, current_xpath)))
            current_link.click()
            navigate_day(driver, current_xpath)
            if 'dynatree-lastsib' in current_link.get_attribute('class'):
                print('Last month found')
                break
            # Move to the next depth

        except Exception as e:
            print('Backtracking month')


def navigate_day(driver, base_xpath):
    ul_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, f"{base_xpath}/ul"))
    )

    days_len = ul_element.find_elements(By.XPATH, './li')

    for depth in range(1, len(days_len) + 1):
        current_xpath = f"{base_xpath}/ul/li[{depth}]"

        print(f"days: {len(days_len)} and loop: {depth}")

        current_link = WebDriverWait(driver, 0).until(
            EC.presence_of_element_located((By.XPATH, current_xpath)))
        if 'dynatree-lastsib' in current_link.get_attribute('class'):
            print('Last element found in days')

        try:
            # Wait for the element to be clickable
            current_link = WebDriverWait(driver, 0).until(
                EC.presence_of_element_located((By.XPATH, current_xpath)))
            current_link.click()

            ul_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"{current_xpath}/ul"))
            )

            li_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"{current_xpath}/ul/li")
                )
            )
            li_elements = ul_element.find_elements(By.XPATH, "./li")

            print(len(li_elements))
            for li in range(1, len(li_elements) + 1):
                current_link = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    f"{current_xpath}/ul/li[{li}]"))
                )
                # /html/body/form/div[13]/div[1]/div[2]/div[1]/div[2]/div[3]/div[2]/ul/li/ul/li[1]/ul/li[1]/ul/li[1]/ul/li[1]/ul/li[1]/ul/li[1]/ul/li/span/a/span
                # print(9)
                current_link.click()
                print("In")
                read_data(driver)
                print("Out")

                if 'dynatree-lastsib' in current_link.get_attribute('class'):
                    print('Last element found')
                    break

        except Exception as e:
            print(f'Backtracking day: {e}')
            pass


def read_data(driver):

    try:
        close_button = driver.find_element(By.XPATH,"//button[@class='btn_common' and text()='Stay logged in']")
        close_button.click()

    except Exception as e:
        pass

    try:
        date_element = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    f"//a[@class='BredCrumbNode breadcrumblist']/span[@class='fortootipBreadCrumb']",
                )
            )
        )
        if not date_element:
            print("No date elements found.")
            return


    except Exception as e:
        print(f"Error extracting date, month, and year: {e}")
        return


    # div_xpath = "/html/body/form/div[13]/div[1]/div[2]/div[1]/div[2]/div[3]/div[2]"
    div_xpath = f"/html/body/form/div[13]/div[1]/div[2]/div[2]/div[2]/div[3]/div[1]"

    try:
        target_div = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, div_xpath))
        )

        soup = BeautifulSoup(target_div.get_attribute(
            "outerHTML"), 'html.parser')

        try:
            tables = soup.find('table')
            for table in tables:
                df = pd.read_html(table.prettify())[0]
                markdown_table = df.to_markdown(index=False)
                table.string = f"\n{markdown_table}\n"
        except Exception as e:
            print("no tables found")

        # inner_text = target_div.text
        inner_text = soup.get_text()

        if inner_text != "":
            try:
                driver.implicitly_wait(0)
                judge_name = driver.find_element(By.CLASS_NAME, 'j').text
                print(f"judge name: {judge_name}")

                ssc_id = driver.find_element(
                    By.CLASS_NAME, 'SectionheadText'
                ).text

                print(f"ssc id: {ssc_id}")

                case_name = [e.text for e in driver.find_elements(
                    By.CLASS_NAME, 'app'
                )]

                case_name = " vs ".join(case_name)
                print(f"case name2: {case_name}")

                
                case_no = driver.find_element(By.CLASS_NAME, 'caseno').text

                print(f"Case no: {case_no}")
                    
                

                date = driver.find_element(By.CLASS_NAME, 'date').text
                print(f"date: {date}")

                # Parse the date from the input string
                date_obj = datetime.strptime(date, "Decided on %B %d, %Y")

                # Format the date into PostgreSQL-compatible format (YYYY-MM-DD)
                postgres_date = date_obj.strftime("%Y-%m-%d")

                advocates = [e.text for e in driver.find_elements(
                    By.CLASS_NAME, 'advo'
                )]
                print(f"advocates: {advocates}")

                citations = [a.get_attribute('onclick') for a in driver.find_elements(
                    By.CLASS_NAME, 'citalink'
                )]
                print(f"citations: {citations}")
            except TimeoutException:
                # / html / body / div[4] / div[3] / div / button[1] / span


                print("Timed out waiting for element to be located")

            # insert data
            add_entry(judge_name, 'Supreme Court of India', case_name, case_no, postgres_date, advocates, citations,inner_text, ssc_id)




    except Exception as e:
        print(f"Error extracting inner text: {e}")


# Call the function to navigate through nested lists starting from 'sc_link'
navigate_nested_lists(driver, base_xpath)  # Adjust max_depth as needed

# Close the browser window
# driver.quit()
