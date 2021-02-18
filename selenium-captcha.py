# Chương trình thử vượt qua recaptcha v2 của Google
import os
import time

# selenium libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# recaptcha libraries
import speech_recognition as sr
import urllib
import pydub


# Decode audio thành text
def decode_audio(src):
    urllib.request.urlretrieve(src, os.getcwd() + "\\sample.mp3")
    sound = pydub.AudioSegment.from_mp3(os.getcwd() + "\\sample.mp3")
    sound.export(os.getcwd() + "\\sample.wav", format="wav")
    sample_audio = sr.AudioFile(os.getcwd() + "\\sample.wav")
    r = sr.Recognizer()

    with sample_audio as source:
        audio = r.record(source)

    # translate audio to text with google voice recognition
    key = r.recognize_google(audio)
    return key


# User profile cho Chrome
userdata = webdriver.ChromeOptions()
Options.add_argument(userdata, "user-data-dir=C:\\Users\\dev2\\AppData\\Local\\Google\\Chrome\\User Data\\Default")

chrome_driver_path = "chromedriver.exe"

tries = 0
bypass = 0
failed = 0
driver = webdriver.Chrome(executable_path=chrome_driver_path, options=userdata)
while tries < 1000:
    tries += 1
    print('{} try\tbypass: {}|failed: {}'.format(tries - 1, bypass, failed))
    try:
        driver.get("https://www.google.com/recaptcha/api2/demo")
        # switch to recaptcha frame
        frames = driver.find_elements_by_tag_name("iframe")
        driver.switch_to.frame(frames[0])

        # click on checkbox to activate recaptcha
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "recaptcha-checkbox-border"))
        ).click()

        # switch to recaptcha audio control frame
        driver.switch_to.default_content()
        frames = driver.find_element_by_xpath("/html/body/div[2]/div[4]").find_elements_by_tag_name("iframe")
        driver.switch_to.frame(frames[0])
        # delay()

        # click on audio challenge
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "recaptcha-audio-button"))
        ).click()

        is_repeat = True
        while is_repeat:
            is_repeat = False
            driver.switch_to.default_content()
            frames = driver.find_element_by_xpath("/html/body/div[2]/div[4]").find_elements_by_tag_name("iframe")
            driver.switch_to.frame(frames[0])
            # click on the play button
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[3]/div/button"))
            ).click()

            # get the mp3 audio file url
            src = driver.find_element_by_id("audio-source").get_attribute("src")
            print("[INFO] Audio src: %s" % src)

            key = decode_audio(src)
            if key == "":
                print("[ERROR] cant decode audio")
            else:
                print("[INFO] Recaptcha Passcode: %s" % key)

            # key in results and submit
            driver.find_element_by_id("audio-response").send_keys(key.lower())
            driver.find_element_by_id("audio-response").send_keys(Keys.ENTER)
            driver.switch_to.default_content()
            # delay()

            # Repeat if recaptcha required  2 challenges
            try:
                WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.ID, "recaptcha-demo-submit"))
                ).click()
            except Exception as ex:
                time.sleep(0.5)
                is_repeat = True

        bypass += 1
        time.sleep(1)

    except Exception as e:
        print('Error: {}'.format(e))
        failed += 1
        time.sleep(1)

x = input()
while x != 'q':
    x = input()

exit()
