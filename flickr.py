import requests
import json
import os
import sys
import re
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
import sqlite3


def main():
    # TODO change this to use get_api_key function. It does not work with debugging at the moment.

    flickr_api_key = "0fb4b0b9f60569d4e7feb311b85d2953"
    base_url = "https://www.flickr.com/services/rest/?method="
    method = "flickr.photos.search"
    params = {"format": "json",
              "content_type": 1,
              "privacy_filter": 1,
              "api_key": flickr_api_key,
              "extras": "description,url_o,url_q,date_taken,date_upload,views",
              "lat": "-37.840935",
              "lon": "144.946457",
              "radius": 20,
              }
    n_photos = 20
    max_photo_per_page = 2
    all_flickr_response_list = all_flickr_api_calls(base_url, method, params, n_photos, max_photo_per_page)
    img_set = dl_flickr_photos(all_flickr_response_list)

    # print(img_set)
    model = ResNet50(weights='imagenet')
    tags_probs = tag_all_photos_Resnet50(model, "flickr_photo_dl/", img_set, 3)
    print(tags_probs)

    conn = sqlite3.connect("flickr.db")


def all_flickr_api_calls(base_url, method, params, n_photos, max_photo_per_call):
    all_flickr_response_json_list = []
    url = base_url + method
    n_calls = int(n_photos / max_photo_per_call)
    params["per_page"] = max_photo_per_call
    for i in range(n_calls):
        params["page"] = i + 1
        flickr_single_response = single_flickr_api_call(url, params)
        flickr_single_response_json = flickr_response_to_json(flickr_single_response)
        all_flickr_response_json_list.append(flickr_single_response_json)
    return all_flickr_response_json_list


def single_flickr_api_call(url, params):
    response = requests.get(url, params=params)
    return response


def tag_all_photos_Resnet50(model, path, img_set, n_tags):
    tags_probs = []
    for img in img_set:
        img_path = path + img
        img_id = re.sub("\.jpg$", "", img)
        tag_probs = tag_single_photo_ResNet50(model, img_path, n_tags)
        tags_probs.append({
            "photo_id": img_id,
            "tag_probs": tag_probs
        })
    return tags_probs


def tag_single_photo_ResNet50(model, img_path, n_tag):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    y = np.expand_dims(x, axis=0)
    z = preprocess_input(y)

    preds = model.predict(z)
    # decode the results into a list of tuples (class, description, probability)
    # (one such list for each sample in the batch)
    decoded_preds = decode_predictions(preds, top=n_tag)[0]
    tags_probs = []
    for i in range(len(decoded_preds)):
        tag = str(decoded_preds[i][1])
        prob = decoded_preds[i][2]
        tags_probs.append((tag, prob))

    return tags_probs


def flickr_response_to_json(flickr_response):
    resp_text = flickr_response.text
    resp_text_reged = re.sub("^jsonFlickrApi\(", "", resp_text)
    resp_text_reged = re.sub("\)$", "", resp_text_reged)
    flickr_response_json = json.loads(resp_text_reged)
    return flickr_response_json


def dl_flickr_photos(all_flickr_response_list):
    n_lists = len(all_flickr_response_list)
    img_set = set()
    for i in range(n_lists):
        for photo in all_flickr_response_list[i]["photos"]["photo"]:
            try:
                img_url = photo["url_o"]
            except KeyError:
                img_url = photo["url_q"]
            img_data = requests.get(img_url).content
            path = "flickr_photo_dl/"
            name = f"{photo['id']}.jpg"
            path_name = path + name
            with open(path_name, 'wb') as f:
                f.write(img_data)
            img_set.add(name)
    return img_set


def create_photo_table():
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    #TODO change photo_id to flicker_photo_id
    c.execute("""CREATE TABLE photos(
        photo_id TEXT,
        owner_id TEXT,
        views INTEGER,
        url_o TEXT,
        url_q TEXT
        )""")


def create_photo_tag_table():
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE photo_tag(
        photo_id INTEGER,
        tag_id INTEGER,
        prob REAL
        )""")

def create_tag_table():
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE tags(
        tag TEXT
        )""")


def create_input_for_photo_table(all_flickr_response_list):
    photo_input_list = []
    n_lists = len(all_flickr_response_list)
    for i in range(n_lists):
        for photo in all_flickr_response_list[i]["photos"]["photo"]:
            try:
                photo_input = (
                    photo["id"],
                    photo["owner"],
                    int(photo["views"]),
                    photo["url_o"],
                    photo["url_q"]
                )
            except KeyError:
                photo_input = (
                    photo["id"],
                    photo["owner"],
                    int(photo["views"]),
                    None,
                    photo["url_q"]
                )
            photo_input_list.append(photo_input)
    return photo_input_list


def creat_input_for_tag_table(tags_probs_list):
    tag_set = set()
    for item in tags_probs_list:
        for tag_prob in item["tag_probs"]:
            tag_set.add(tag_prob[0])
    tag_list = list(tag_set)
    tag_list_tuple = [(elem,) for elem in tag_list]
    return list(tag_list_tuple)


def create_input_for_photo_tag_table(tags_probs_list):
    photo_tag_input_list = []
    for item in tags_probs_list:
        item_photo_input_list = []
        flickr_photo_id = item["photo_id"]
        db_photo_id = get_db_photo_id(flickr_photo_id)
        for tag_prob in item["tag_probs"]:
            tag = tag_prob[0]
            prob = float(tag_prob[1])
            formatted_prob = f"{prob:.3f}"
            tag_id = get_tag_id(tag)
            item_photo_input_list.append((db_photo_id, tag_id, formatted_prob))

        photo_tag_input_list.extend(item_photo_input_list)

    return photo_tag_input_list


def get_db_photo_id(flickr_photo_id):
    flickr_photo_id = (flickr_photo_id,)
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    # TODO Change photo_id to flickr_photo_id
    c.execute("SELECT rowid FROM photos WHERE photo_id = ?", flickr_photo_id)
    db_photo_id = c.fetchone()
    conn.close()
    return db_photo_id[0]


def get_tag_id(tag):
    tag = (tag,)
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    c.execute("SELECT rowid FROM tags WHERE tag = ?", tag)
    tag_id = c.fetchone()
    conn.close()
    return tag_id[0]

def add_photos_to_photo_table(photo_input_list):
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    c.executemany("INSERT INTO photos VALUES (?,?,?,?,?)", photo_input_list)
    conn.commit()
    conn.close()


def add_tags_to_tag_table(tag_list):
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    c.executemany("INSERT INTO tags VALUES (?)", tag_list)
    conn.commit()
    conn.close()


def add_photo_tags_to_photo_tag_table(photo_tag_input_list):
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    c.executemany("INSERT INTO photo_tag VALUES (?,?,?)", photo_tag_input_list)
    conn.commit()
    conn.close()

def get_api_key():
    try:
        return os.environ["FLICKR_API_KEY"]
    except KeyError:
        sys.exit("Provide the FLICKR_API_KEY as an environment variable")


if __name__ == "__main__":
    main()
