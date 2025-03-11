# -*- coding: utf-8 -*-
"""Download Images

This code downloads images from two free image sources, **[Unsplash](https://unsplash.com/)** and **[Pixabay](https://pixabay.com/)**.

For Pixabay images, you need to obtain your own free API key from their website to access the direct image URLs. 
[How to get your Pixabay API key?](https://pixabay.com/api/docs/)

Simply run the script with the provided metadata JSON file, and it will save the images into the specified directory."""


import json
import requests
import os
import re


API_KEY = ''  # Replace with your actual Pixabay API key in the script. [How to get your Pixabay API key?](https://pixabay.com/api/docs/)
download_dir = './VAE_input_images'
json_file = './vae_images_metadata.json'



os.makedirs(download_dir, exist_ok=True)
with open(json_file, 'r') as f:
    images_data = json.load(f)


for filename, details in images_data.items():
    source = details.get('source', '').lower()

    direct_image_url = None

    if source == 'pixabay':
        match = re.search(r'pixabay_(\d+)\.jpg', filename)
        if match:
            image_id = match.group(1)

            api_url = f'https://pixabay.com/api/?key={API_KEY}&id={image_id}'
            try:
                api_response = requests.get(api_url)
                api_response.raise_for_status()
                api_data = api_response.json()

                if api_data.get('hits'):

                    direct_image_url = api_data['hits'][0].get('largeImageURL')
                    if not direct_image_url:
                        print(f"No direct image URL found for {filename}.")
                        continue
                else:
                    print(f"No image data returned for {filename} with ID {image_id}.")
                    continue

            except requests.exceptions.RequestException as e:
                print(f"Failed to retrieve data from Pixabay API for {filename}: {e}")
                continue
        else:
            print(f"Could not extract image ID from {filename}.")
            continue
    else:

        direct_image_url = details.get('image_url')

    if not direct_image_url:
        print(f"No valid image URL found for {filename}.")
        continue

    try:
        response = requests.get(direct_image_url, stream=True)
        response.raise_for_status()

        file_path = os.path.join(download_dir, filename)
        with open(file_path, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=8192):
                out_file.write(chunk)

        print(f"Downloaded {filename} from {direct_image_url}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to download {filename} from {direct_image_url}: {e}")
