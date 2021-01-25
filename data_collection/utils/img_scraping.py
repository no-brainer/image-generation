import time
import base64

import cv2.cv2 as cv2
import numpy as np
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def check_base64(source):
    split_result = source.split(",")
    header = split_result[0]
    if header.startswith("data") and header.endswith(";base64"):
        img_type = header.replace("data:image/", "").replace(";base64", "")
        return True, (img_type, split_result[1])
    return False, None


class GoogleImagesScraper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--incognito")
        options.add_argument("--headless")

        self.options = options

        self.sleep_time = 0.3
        self.max_load_wait = 5.0
        self.click_wait = 0.3

    def __enter__(self):
        self.driver = webdriver.Chrome(options=self.options)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.driver.close()

    def _get_image_resources(self, query):
        self.driver.get("https://www.google.com/imghp?hl=en")

        search_bar = WebDriverWait(self.driver, self.max_load_wait).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )

        search_bar.click()
        search_bar.send_keys(query)
        search_bar.submit()

        WebDriverWait(self.driver, self.max_load_wait).until(
            EC.presence_of_element_located((By.CLASS_NAME, "isv-r"))
        )
        img_thumbnails = self.driver.find_elements_by_class_name("isv-r")
        for img_thumbnail in img_thumbnails:
            img_thumbnail.click()
            img_thumbnail_img = WebDriverWait(self.driver, self.max_load_wait).until(
                EC.presence_of_element_located((By.TAG_NAME, "img"))
            )
            img_thumbnail_src = img_thumbnail_img.get_attribute("src")
            time.sleep(self.click_wait)

            img_data = WebDriverWait(self.driver, self.max_load_wait).until(
                EC.presence_of_element_located((By.ID, "Sva75c"))
            )
            img_element = None
            for potential_element in img_data.find_elements_by_class_name("n3VNCb"):
                if potential_element.is_displayed():
                    img_element = potential_element
                    break
            if img_element is None:
                print("No visible element for current image.")
                continue

            # waiting while element is loading
            wait_start = time.time()
            while (time.time() - wait_start < self.max_load_wait
                    and img_thumbnail_src == img_element.get_attribute("src")):
                time.sleep(self.sleep_time)

            yield img_element.get_attribute("src")

    def provide_images(self, query):
        for img_source in self._get_image_resources(query):
            # img_source is either base64 or a link
            is_base64, result = check_base64(img_source)

            if is_base64:
                img_format = result[0]
                content = base64.b64decode(result[1])
            else:
                try:
                    resp = requests.get(img_source, allow_redirects=True, timeout=self.max_load_wait)
                except Exception:
                    continue
                if resp.status_code != 200:
                    continue
                img_format = resp.headers.get("content-type")
                content = resp.content

            img = np.frombuffer(content, dtype=np.uint8)
            img = cv2.imdecode(img, cv2.IMREAD_COLOR)
            if img is None:
                continue

            yield img
