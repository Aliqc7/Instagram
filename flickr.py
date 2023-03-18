import requests
import json
import os
import sys
import re


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
    # dl_flickr_photos(all_flickr_response_list)

    print(all_flickr_response_list)


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


def flickr_response_to_json(flickr_response):
    resp_text = flickr_response.text
    resp_text_reged = re.sub("^jsonFlickrApi\(", "", resp_text)
    resp_text_reged = re.sub("\)$", "", resp_text_reged)
    flickr_response_json = json.loads(resp_text_reged)
    return flickr_response_json


def dl_flickr_photos(all_flickr_response_list):
    n_lists = len(all_flickr_response_list)
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


def get_api_key():
    try:
        return os.environ["FLICKR_API_KEY"]
    except KeyError:
        sys.exit("Provide the FLICKR_API_KEY as an environment variable")


if __name__ == "__main__":
    main()
