import requests
import json
import os
import sys
from urllib.parse import urljoin
def main():

    flickr_api_key = "0fb4b0b9f60569d4e7feb311b85d2953"
    base_url = "https://www.flickr.com/services/rest/?method="
    method = "flickr.photos.search"
    params = {"format": "json",
              "content_type": 1,
              "privacy_filter": 1,
              "api_key": flickr_api_key,
              "tags": "dog",
              "per_page": 2,
              "extras": ["description", "license", "url_o"],
              "page": 2}
    response = get_flickr_photo_info(base_url, method, params)

    print(response)

def get_flickr_photo_info(base_url, method, params):
    url = base_url + method
    response = requests.get(url, params=params)
    return response
def get_api_key():
    try:
        return os.environ["FLICKR_API_KEY"]
    except KeyError:
        sys.exit("Provide the FLICKR_API_KEY as an environment variable")




if __name__ == "__main__":
    main()
