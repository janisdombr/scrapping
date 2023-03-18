from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("/Users/janisdombr/Desktop/SpbRent/flipperlab-bdabe-firebase-adminsdk-8kaua-a84cbdde54.json")
app = firebase_admin.initialize_app(cred)
firestore_client = firestore.client()


baseurl = "https://asunnot.oikotie.fi/vuokra-asunnot?locations=%5B%5B39,6,%22Espoo%22%5D%5D&cardType=101&pagination="


service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
delay = 30 # seconds
startpage = 130
endpage = 131
for page in range(startpage, endpage+1):
    url = baseurl + str(page)
    #driver = webdriver.Firefox()
    driver.get(url)

    try:
        print("Scanning "+str(page)+" page")
        if page == startpage:
            button_container = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'sp_message_container_761217')))
            print ("Message exists!")
            frames = driver.find_elements(By.TAG_NAME, "iframe")
            for frame in frames:
                if frame.get_attribute("id") == "sp_message_iframe_761217":
                    print ("Found frame!")
                    driver.switch_to.frame(frame)
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    if len(buttons)>1:
                        print ("Button exists!")
                        buttons[1].click()
                    else:
                        print ("Button not exists!")
                        body = driver.find_element(By.XPATH, "html/body")
                        print(body.text)
                else:
                    print(frame.get_attribute("id"))
            
            driver.switch_to.default_content()
        WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.CLASS_NAME, 'card-v2-text-container__text')))
        print ("Page is ready!")
        
        house_containers = driver.find_elements(By.CLASS_NAME, "cards-v2__card")
        print(len(house_containers))
        for house in house_containers:
            if (not "cards-v2__card--ad-" in house.get_attribute("class")) and (not "cards-v2__card--csat" in house.get_attribute("class")):
                #print(house.get_attribute("class"))
                link = house.find_element(By.TAG_NAME, "a")
                ad_url = link.get_attribute("href")
                #print(ad_url)
                ad_id = link.get_attribute("analytics-click-card-id")
                print(ad_id)
                imgurl = house.find_element(By.TAG_NAME, "source").get_attribute("srcset").split(",")[1][1:-3]
                #print("["+imgurl+"]")
                address = house.find_element(By.CLASS_NAME, "card-v2-text-container__text").text
                #print("["+address+"]")
                data2 = house.find_elements(By.CLASS_NAME, "card-v2-text-container__group")
                data3 = data2[0].find_elements(By.TAG_NAME, "div")
                housetype = data3[0].text
                #print(housetype)
                houserooms = '';
                if (len(data3)>1):
                    houserooms = data3[2].text
                #print(houserooms)
                data3 = data2[1].find_elements(By.TAG_NAME, "h2")

                price = data3[0].text
                if price != 'Kysy hintaa':
                    #print(price)
                    price = int(price[:-6].replace(" ", ""))
                else:
                    price = 0
                print(price)
                square = data3[1].text
                square = square[:-3].replace(",", ".").replace(" ", "")
                #print(square)
                data = {
                    u'ad_url': ad_url,
                    u'address': address,
                    u'house_type': housetype,
                    u'img_url': imgurl,
                    u'object_type': houserooms,
                    u'price': int(price),
                    u'square': float(square)
                }
                firestore_client.collection(u'asunnot.oikotie.fi-rent').document(ad_id).set(data)
    except TimeoutException:
        print ("Couldn't load page")