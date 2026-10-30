# import necessary tools from the selenium library
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def get_tasks_count(table):
    lines = table.split("<tr>")
    # print(lines)
    tasks = lines[1].strip().replace(" ", "")
    tasks = tasks.replace("<td>", "")
    tasks = tasks.replace("</td>", "")
    tasks = tasks.replace("</tr>", "")
    tasks = tasks.rstrip()

    while tasks.count("\n\n") != 0:
        tasks = tasks.replace("\n\n", "\n")

    tasks = tasks.split("\n")
    tasks_count = len(tasks) - 3
    return tasks_count

def get_table_data(table, tasks_count):
    lines = table.split("<tr>")
    lines = lines[2:-(3 + tasks_count)]
    for i in range(len(lines)):
        line = lines[i]
        line = line.strip().replace(" ", "")
        line = line.replace("<td>", "")
        line = line.replace("</td>", "")
        line = line.replace("</tr>", "")
        line = line.rstrip()
        while line.count("\n\n") != 0:
            line = line.replace("\n\n", "\n")
        line = line.split("\n")
        lines[i] = line
    return lines

def get_table(url_table):
    # set up chrome driver
    service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=service, options=options)
    username = "pavlov_bot"
    password = "QWErty_1"
    url_login = "https://informatics.msk.ru/login/index.php"

    # navigate to the target webpage
    driver.get(url_login)
    #time.sleep(5)
    driver.find_element("id", "username").send_keys(username)
    # find password input field and insert password as well
    driver.find_element("id", "password").send_keys(password)
    # click login button
    driver.find_element("id", "loginbtn").click()

    time.sleep(2)
    print("logged")
    ret_data = []
    for job in url_table:
        print("Parsing ", job["link"])
        driver.get(job["link"])
    #print(driver.text)
        #time.sleep(5)
        job_data = []
        try:
            element = WebDriverWait(driver, 20).until(
                #EC.element_to_be_clickable((By.ID, "MonitorResult"))
                EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr"))
            )
        except TimeoutException:
            print("Элемент не загрузился за 20 секунд")
            exit(-1)

        data = driver.find_element("id", "MonitorResult")
        content = data.get_attribute('innerHTML')
        tasks_count = get_tasks_count(content)
        stud_info = get_table_data(content, tasks_count)
        student_info = []
        for stud in stud_info:
            aref = stud[1]
            id = int(aref[aref.find("user_id=") + len("user_id="):aref.find("\">")])
            student_info.append([id, int(stud[2])])
        #print(content)
        job_data = [job, tasks_count, student_info]
        ret_data.append(job_data)
        #data = data.text
        #job["table"] = data
        #print(data)
        print("Parsing finished")

    # close the browser
    driver.quit()
    return ret_data