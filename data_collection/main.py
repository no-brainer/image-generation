import os
import zipfile

import cv2.cv2 as cv2  # this is the same as import cv2, but avoids warnings in pycharm

from utils.img_scraping import Scraper
from utils.query_queue import QueryQueue

TMP_FOLDER = "../imgs"
READY_ZIP = "../imgs/data.zip"

FINAL_IMG_DIMENSIONS = (64, 64)


class ImageCollection:
    def __init__(self):
        with zipfile.ZipFile(READY_ZIP, "a") as zip_file:
            self.cur_img_idx = len(zip_file.namelist())
        self.face_bbox = []
        self.is_drawing = False
        self.is_crop_ready = False

        self.window_name = "Dataset prep"

        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.on_mouse_event)

    def __del__(self):
        cv2.destroyAllWindows()

        for root, _, files in os.walk(TMP_FOLDER):
            for file_name in files:
                os.remove(os.path.join(root, file_name))

    def on_mouse_event(self, event, x, y, flags, params):
        def sgn(val):
            if val == 0:
                return val
            return -1 if val < 0 else 1

        if self.is_crop_ready:
            return

        if event == cv2.EVENT_LBUTTONDOWN:
            self.face_bbox = [(x, y)]
            self.is_drawing = True

        elif self.is_drawing and event == cv2.EVENT_MOUSEMOVE:
            diff = abs(x - self.face_bbox[0][0])
            if diff > abs(y - self.face_bbox[0][1]):
                diff = abs(y - self.face_bbox[0][1])
            next_x = self.face_bbox[0][0] + sgn(x - self.face_bbox[0][0]) * diff
            next_y = self.face_bbox[0][1] + sgn(y - self.face_bbox[0][1]) * diff

            if len(self.face_bbox) > 1:
                self.face_bbox.pop()
            self.face_bbox.append((next_x, next_y))

        elif event == cv2.EVENT_LBUTTONUP:
            self.is_drawing = False
            self.is_crop_ready = True

    def write_out(self, img):
        tmp_file = os.path.join(TMP_FOLDER, "tmp.png")
        cv2.imwrite(tmp_file, img)
        with zipfile.ZipFile(READY_ZIP, "a") as zip_file:
            zip_file.write(tmp_file, f"img{self.cur_img_idx}.png")
        self.cur_img_idx += 1
        os.remove(tmp_file)

    def img_prep(self):
        scraper = Scraper()
        queries = QueryQueue()
        for query in queries.get_all():
            is_new_query_requested = False
            for img in scraper.traverse_images(query):
                self.is_crop_ready = False
                is_done = False
                while not is_done:
                    img_cpy = img
                    if len(self.face_bbox) == 2:
                        img_cpy = img.copy()
                        cv2.rectangle(img_cpy, self.face_bbox[0], self.face_bbox[1], (0, 255, 0), 2)
                        if self.is_crop_ready:
                            x1, y1 = self.face_bbox[0]
                            x2, y2 = self.face_bbox[1]

                            if x1 > x2:
                                x1, x2 = x2, x1
                            if y1 > y2:
                                y1, y2 = y2, y1

                            cropped_region = img[y1:y2, x1:x2]
                            cropped_region = cv2.resize(cropped_region, FINAL_IMG_DIMENSIONS)

                            self.write_out(cropped_region)

                            self.is_crop_ready = False
                            self.face_bbox = []

                    cv2.imshow(self.window_name, img_cpy)

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("w"):
                        return
                    elif key == ord("s"):
                        is_done = True
                        is_new_query_requested = True
                    elif key == ord("d"):
                        is_done = True

                if is_new_query_requested:
                    break


if __name__ == "__main__":
    ImageCollection().img_prep()
