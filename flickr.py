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
    # all_flickr_response_list = all_flickr_api_calls(base_url, method, params, n_photos, max_photo_per_page)
    # img_set = dl_flickr_photos(all_flickr_response_list)

    # print(img_set)
    model = ResNet50(weights='imagenet')
    tags_probs = tag_all_photos_resnet50(model, "flickr_photo_dl/", img_set, 3)
    print(tags_probs)


#DONE
def param_list_for_all_api_calls(params, n_photos, max_photo_per_page):
    params_list = []
    n_calls = int(n_photos / max_photo_per_page)
    params["per_page"] = max_photo_per_page
    for i in range(n_calls):
        params["page"] = i + 1
        params_list.append(params.copy())
    return params_list

#DONE
def all_flickr_api_calls(base_url, method, params_list):
    url = base_url + method
    n_calls = len(params_list)
    for i in range(n_calls):
        flickr_single_response = single_flickr_api_call(url, params_list[i])
        flickr_single_response_json = flickr_response_to_json(flickr_single_response)
        photo_input_list = create_input_for_photo_table(flickr_single_response_json)
        add_photos_to_photo_table(photo_input_list)

#DONE
def single_flickr_api_call(url, params):
    response = requests.get(url, params=params)
    return response


#DONE
def tag_all_photos_resnet50(model, dl_path, photo_list, n_tags):
    tags_probs = []
    for photo_id in photo_list:
        tag_probs = tag_single_photo_resNet50(model, photo_id, dl_path, n_tags)
        tags_probs.append({
            "photo_id": photo_id,
            "tag_probs": tag_probs
        })
    return tags_probs


#DONE
def tag_single_photo_resNet50(model, photo_id, dl_path, n_tags):
    name = f"{photo_id}.jpg"
    path_name = dl_path + name
    img = image.load_img(path_name, target_size=(224, 224))
    x = image.img_to_array(img)
    y = np.expand_dims(x, axis=0)
    z = preprocess_input(y)

    preds = model.predict(z)
    # decode the results into a list of tuples (class, description, probability)
    # (one such list for each sample in the batch)
    decoded_preds = decode_predictions(preds, top=n_tags)[0]
    tags_probs = []
    for i in range(len(decoded_preds)):
        tag = str(decoded_preds[i][1])
        prob = decoded_preds[i][2]
        tags_probs.append((tag, prob))

    return tags_probs

#DONE
def flickr_response_to_json(flickr_response):
    resp_text = flickr_response.text
    resp_text_reged = re.sub("^jsonFlickrApi\(", "", resp_text)
    resp_text_reged = re.sub("\)$", "", resp_text_reged)
    flickr_response_json = json.loads(resp_text_reged)
    return flickr_response_json



#DONE
def fetch_photo_url_form_db(photo_id):
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    c.execute("SELECT url_o FROM photos WHERE photo_id = ?", (photo_id,))
    url_o = c.fetchone()[0]
    c.execute("SELECT url_q FROM photos WHERE photo_id = ?", (photo_id,))
    url_q = c.fetchone()[0]
    conn.close()
    return url_o, url_q

#DONE
def dl_single_photo(photo_id, dl_path):
    url_o, url_q = fetch_photo_url_form_db(photo_id)
    if url_o is not None:
        img_data = requests.get(url_o).content
    else:
        img_data = requests.get(url_q).content
    name = f"{photo_id}.jpg"
    path_name = dl_path +name
    with open(path_name, "wb") as f:
        f.write(img_data)

#DONE
def fetch_photo_list_from_db():
    photo_list = []
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    c.execute("SELECT photo_id FROM photos")
    photo_list_db = c.fetchall()
    conn.close()
    [photo_list.append(int(photo)) for (photo,) in photo_list_db]
    return photo_list


def dl_all_photos(photo_list, dl_path):
    for photo_id in photo_list:
        dl_single_photo(photo_id, dl_path)


#Done
def create_photo_table():
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    #TODO change photo_id to flicker_photo_id
    c.execute("""CREATE TABLE photos(
        photo_id TEXT NOT NULL PRIMARY KEY,
        owner_id TEXT,
        views INTEGER,
        url_o TEXT,
        url_q TEXT
        )""")


#DONE
def create_photo_tag_table():
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE photo_tag(
        photo_id INTEGER,
        tag_id INTEGER,
        prob REAL
        )""")

#DONE
def create_tag_table():
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE tags(
        tag TEXT
        )""")

#DONE
def create_input_for_photo_table(flickr_response_json):
    photo_input_list = []
    for photo in flickr_response_json["photos"]["photo"]:
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

#DONE
def creat_input_for_tag_table(tags_probs_list):
    tag_set = set()
    for item in tags_probs_list:
        for tag_prob in item["tag_probs"]:
            tag_set.add(tag_prob[0])
    tag_list = list(tag_set)
    tag_list_tuple = [(elem,) for elem in tag_list]
    return list(tag_list_tuple)


#DONE
def create_input_for_photo_tag_table(tags_probs_list):
    photo_tag_input_list = []
    for item in tags_probs_list:
        item_photo_input_list = []
        photo_id = item["photo_id"]
        for tag_prob in item["tag_probs"]:
            tag = tag_prob[0]
            prob = float(tag_prob[1])
            formatted_prob = f"{prob:.3f}"
            tag_id = get_tag_id(tag)
            item_photo_input_list.append((photo_id, tag_id, formatted_prob))

        photo_tag_input_list.extend(item_photo_input_list)

    return photo_tag_input_list


# def get_db_photo_id(flickr_photo_id):
#     flickr_photo_id = (flickr_photo_id,)
#     conn = sqlite3.connect("flickr.db")
#     c = conn.cursor()
#     # TODO Change photo_id to flickr_photo_id
#     c.execute("SELECT rowid FROM photos WHERE photo_id = ?", flickr_photo_id)
#     db_photo_id = c.fetchone()
#     conn.close()
#     return db_photo_id[0]

#DONE
def get_tag_id(tag):
    tag = (tag,)
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    c.execute("SELECT rowid FROM tags WHERE tag = ?", tag)
    tag_id = c.fetchone()
    conn.close()
    return tag_id[0]

#DONE
def add_photos_to_photo_table(photo_input_list):
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    c.executemany("INSERT INTO photos VALUES (?,?,?,?,?) ON CONFLICT(photo_id) DO NOTHING", photo_input_list)
    conn.commit()
    conn.close()

#DONE
def add_tags_to_tag_table(tag_list):
    conn = sqlite3.connect("flickr.db")
    c = conn.cursor()
    c.executemany("INSERT INTO tags VALUES (?)", tag_list)
    conn.commit()
    conn.close()

#DONE
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
