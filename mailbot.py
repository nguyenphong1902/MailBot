import imaplib
import email
import datetime
import os
import pandas as pd
import html2text
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from order import Order


class MailBot:

    def __init__(self, user, password, url):
        self.con = imaplib.IMAP4_SSL(url)
        self.user = user
        self.password = password
        self.url = url
        self.attach_dir = "Attachments"

    def login_imap(self):
        self.con.login(self.user, self.password)
        self.con.select('INBOX')

    def get_mail_info(self, uid):
        global body, local_message_date
        result, email_data = self.con.fetch(uid, '(RFC822)')
        raw_email = email_data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        # Header Details
        date_tuple = email.utils.parsedate_tz(email_message['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            local_message_date = "%s" % (str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
        email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
        email_to = str(email.header.make_header(email.header.decode_header(email_message['To'])))
        subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))

        # Body details
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode('utf-8')
            elif part.get_content_type() == "text/html":
                body = html2text.html2text(part.get_payload(decode=True).decode('utf-8'))
            else:
                continue

        return {'MailID': uid.decode('utf-8'), 'From': email_from, 'To': email_to, 'Date': local_message_date,
                'Title': subject, 'Body': body}

    def get_attachments(self, uid):
        result, email_data = self.con.fetch(uid, '(RFC822)')
        msg = email.message_from_bytes(email_data[0][1])
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            fileName = part.get_filename()

            if bool(fileName):
                project_root = os.getcwd()
                output_path = project_root + "\\" + self.attach_dir + "\\" + uid.decode('utf-8') + "\\"

                if not os.path.exists(output_path):
                    os.makedirs(output_path)
                filePath = os.path.join(output_path, fileName)
                with open(filePath, 'wb') as f:
                    f.write(part.get_payload(decode=True))

    def write_to_csv(self, search_data, csv_path):
        if len(search_data[0]) > 0:
            df = pd.DataFrame(columns=['MailID', 'From', 'To', 'Date', 'Title', 'Body'])
            rows_list = []
            for uid in search_data[0].split():
                di = self.get_mail_info(uid)
                self.get_attachments(uid)
                rows_list.append(di)

            df = pd.DataFrame(rows_list)
            if os.path.exists(csv_path):
                df.to_csv(csv_path, mode='a', index=False, header=False)
            else:
                df.to_csv(csv_path, index=False, header=True)

    def post_data(self, search_data, url):
        re = ""
        if len(search_data[0]) > 0:
            for uid in search_data[0].split():
                mail_info = self.get_mail_info(uid)
                mail_body = mail_info.get('Body')
                order = Order()
                order.getinfo(mail_body)
                payload = order.toDict()
                headers = {'Content-Type': 'application/json'}
                re += "posting data to: " + url + "\n"
                response = requests.post(url, headers=headers, json=payload, verify=False)
                re += str(response.status_code) + " " + response.text

        return re

    # Hàm import data từ email lên trang pleiger
    def pleiger_input(self, search_data):
        re = ""
        if len(search_data[0]) > 0:
            # Khởi tạo chrome driver
            chrome_driver_path = "chromedriver.exe"
            userdata = webdriver.ChromeOptions()
            Options.add_argument(userdata,
                                 "user-data-dir=C:\\Users\\dev2\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
            driver = webdriver.Chrome(chrome_driver_path)

            # Mở trang pleiger bằng chrome và đăng nhập
            USERNAME = "0000000005"
            PASSWORD = "admin"
            driver.get("http://pleiger.thlsoft.com/")
            user_input = driver.find_element_by_id('txtUserName')
            user_input.send_keys(USERNAME)
            password_input = driver.find_element_by_id('txtPassword')
            password_input.send_keys(PASSWORD)
            login_button = driver.find_element_by_id('btnLogin')
            login_button.click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "btnlanguage"))
            ).click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[@href='/ko/Home/OnGetSetCultureCookie?cltr=en']"))
            ).click()

            # Vòng lặp cho từng email tìm được
            for uid in search_data[0].split():
                print("\n"+str(uid))

                # Lấy dữ liệu từ email
                mail_info = self.get_mail_info(uid)
                mail_body = mail_info.get('Body')
                order = Order()
                order.getinfo(mail_body)
                if order.OrderNumber[1] == "":
                    continue

                # Click đến phần form create
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.LINK_TEXT, "SCM"))
                    ).click()
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//a[@menu-id='75']"))
                    ).click()
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//a[@menu-id='67']"))
                    ).click()
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        "//button[@title='Create' and @menu-id='67']"))
                    ).click()
                except Exception as e:
                    print(str(e) + " ")
                    driver.refresh()
                    continue

                # Nhập liệu từ order lên form
                for attr, value in order.__dict__.items():
                    field = str(attr)
                    if field == 'Customer':
                        field = 'PartnerCode'
                    elif field == 'Product':
                        field = 'ItemCode'
                    elif field == 'ExchangeRate':
                        field = 'ExchangRate'

                    xpath = '//div[@class=\'modal-content\']//div[contains(@id,\'{}\')]//input[@type=\'text\']'.format(
                        field)
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH,
                                                            xpath))
                        ).send_keys(value[1])
                        # input_info = driver.find_element_by_xpath(xpath)
                        # input_info.send_keys(value[1])
                        if value[2] == "dropdown":
                            WebDriverWait(driver, 2).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, '//div[contains(text(),\'{}\') and @class=\'dx-item-content dx-list-item-content\']'.format(value[1])))
                            ).click()
                        # time.sleep(2)

                    except Exception as e:
                        try:
                            input_info = driver.find_element_by_xpath(xpath)
                            input_info.clear()
                            input_info.send_keys(value[1].split()[0])
                            if value[2] == "dropdown":
                                WebDriverWait(driver, 2).until(
                                    EC.presence_of_element_located(
                                        (By.XPATH, '//div[contains(text(),\'{}\')]'.format(value[1].split()[0])))
                                ).click()
                        except:
                            print(str(e) + " ")
                # Click Close/Save
                try:
                    # # Close
                    # WebDriverWait(driver, 10).until(
                    #     EC.presence_of_element_located((By.XPATH,
                    #                                     "//button[@class='btn btn-sm btn-secondary']"))
                    # ).click()

                    # Save
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        "//button[contains(@id,'btnSave')]"))
                    ).click()

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        "//div[@class='dx-item-content dx-toolbar-item-content']"))
                    )
                    ele_found = driver.find_elements_by_xpath("//div[@class='dx-item-content dx-toolbar-item-content']//div[contains(text(),'Success')]")
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        "//div[@aria-label='OK' and @role='button']"))
                    ).click()
                    if len(ele_found)==0:
                        print("Import Fail")
                        # Close
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH,
                                                            "//button[@class='btn btn-sm btn-secondary']"))
                        ).click()
                    else:
                        print("Import Sucess")
                    # driver.refresh()
                except Exception as ex:
                    print(str(ex) + " ")
                    driver.refresh()
                    continue

            driver.quit()

        return re
