from urllib import response
import requests
from flask import Flask, request, render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import shortuuid

from PIL import Image

import urllib.parse
import json
import re

# ===========================================
# =============  UNSPLASH Setup  ============
# ===========================================

access_key = 'your-access-key-from-Unsplash-API'
secret_key = 'your-secret-key-from-Unsplash-API'
no_of_pages = 1

# ===========================================
# =============  FLASK FORMS   ==============
# ===========================================
class SearchForm(FlaskForm):
    search_query = StringField('Search Query', validators=[DataRequired()])

app = Flask(__name__)
# For CSRF token
app.config['SECRET_KEY'] = 'Secret String for CSRF'

# ===========================================
# ===========================================

# Root Page
@app.route('/download', methods=['GET', 'POST'])
def unsplash_search():

    # Search Form
    form = SearchForm()

    # Handle input and perform search of images based on user's input
    if request.method=='POST':
        search_image_query = form.search_query.data
        # Clean Input
        search_image_query = search_image_query.strip() # Remove starting and ending whitespaces
        # Remove double spaces
        search_image_query = re.sub(' +', ' ', search_image_query)
        # URl Encode
        search_image_query = urllib.parse.quote_plus(search_image_query)
        # print(search_image_query)

        # Setup search get request
        api_request = f'https://api.unsplash.com/search/photos/?page={no_of_pages}&query={search_image_query}&client_id={access_key}'
        
        # GET Request to unsplash API
        api_response_obj = requests.get(api_request)
        # Returned json object
        search_response = api_response_obj.content
        # Converting returned json object into python dict
        decoded_response = search_response.decode('utf-8')
        image_response_dict = json.loads(decoded_response)

        # Dictionaries to be sent to template - For Thumbnail and Download URLs
        image_thumbnail_url_array = []
        downloadURLArray = []

        for eachResult in image_response_dict['results']:
            # print(eachResult)
            thumbnail_url = eachResult['urls']['thumb']
            downloadURL = eachResult['links']['download_location'] + '&w=1280&h=720'
            downloadURLArray.append(downloadURL)
            image_thumbnail_url_array.append(thumbnail_url)

            # eachResult['description'] sometimes returns paragraphs so could not use that as image name
            # Instead, image name based on search query was used - Logic can be found in the /download/img handler

            # # Image Name:
            # img_name = eachResult['description']
            # # img_name = img_name.split(' ').join('-');
            # # img_name += '.jpg'
            # imageNameArray.append(img_name)
            # print(smallUrl)

        urls_thumbnail_download = {}        
        # urls__thumbail_imageName = {}
        for i in range(len(image_thumbnail_url_array)):
            urls_thumbnail_download[image_thumbnail_url_array[i]] = downloadURLArray[i]
            # urls__thumbail_imageName[image_thumbnail_url_array[i]] = imageNameArray[i]
        # print(urls_dict)

        return render_template('unsplash.html', urls_thumbnail_download=urls_thumbnail_download, image_name=search_image_query, form=form)

    return render_template('unsplash.html', form=form)

# Handle the Download of each Image
@app.route('/download/img', methods=['POST'])
def downloadImage():
    
    # print('===================================')
    # print('Content: ', request.data)
    # print('===================================')
    # Output: 
    # b'https://api.unsplash.com/photos/EwKXn5CapA4/download?ixid=MnwzNDM2MTZ8MHwxfHNlYXJjaHwxfHxOYXR1cmV8ZW58MHx8fHwxNjU3MDg1MTQ4&w=1280&h=720,Nature'

    requestData = request.data.decode('utf-8')
    # Separate the URL and Image Name
    url_imgName = requestData.split(',')
    imageName = url_imgName.pop()

    for url in url_imgName:
        urlReq = url + f'&client_id={access_key}'
        image_UUID = shortuuid.uuid()
        imageName = imageName + '-' + image_UUID
        request_download = requests.get(urlReq).content
        result_dict = json.loads(request_download) 
        img_url = result_dict['url']
        img_data = requests.get(img_url).content

        with open(f'./static/img/{imageName}.jpg', 'wb') as handler:
            handler.write(img_data)
        
        image = Image.open(f'./static/img/{imageName}.jpg')
        resizedImage = image.resize((1280,720))
        resizedImage.save(f'new-{imageName}.jpg')

    # # download_urls_unsplash_api = url_imgName[0]
    # # download_url_unsplash_api += f'&client_id={access_key}'

    
    # # print("Download Route Hit")
    # # print("Form Data: ", download_url_unsplash_api)

    # # Generate A Unique Image name with respect to the Query String
    # # imageName = request.form['image_name']
    # # image_UUID = shortuuid.uuid()
    # # imageName = imageName + '-' + image_UUID

    # # Folled Unsplash Documentation and we need to use the download link given by api    
    # request_download = requests.get(download_url_unsplash_api).content
    # # Returns a new URL to download the Image
    # result_dict = json.loads(request_download) 
    # # print(result_dict)

    # # Downloading the Image Data
    # img_url = result_dict['url']
    # img_data = requests.get(img_url).content

    # # Saving the image to /static/img with a unique image name
    # with open(f'./static/img/{imageName}.jpg', 'wb') as handler:
    #     handler.write(img_data)
    return "Image Downloaded to /static/img"

if __name__ == 'main':
    app.run(host='localhost', port=5000, debug=True)

# ===========================================
# =============  UNSPLASH LOGIC  ============
# ===========================================

# access_key = 'CJ05QB-r7s3oX9dFBN5nG7nHQvEFMUz-HS-B6W8Nm-4'
# secret_key = '-d7X4ZIekaQShEfIDoEqJqpyCQ2sek6SRLZ_MtdfJUI'

# search_query = 'Nature'
# no_of_pages = 1

# # , headers={'Authorization': 'Client-ID:CJ05QB-r7s3oX9dFBN5nG7nHQvEFMUz-HS-B6W8Nm-4'}
# r = requests.get(f'https://api.unsplash.com/search/photos/?page={no_of_pages}&query={search_query}&client_id=CJ05QB-r7s3oX9dFBN5nG7nHQvEFMUz-HS-B6W8Nm-4')

# print('==========================================================')
# print(r.status_code)
# print('==========================================================')
# print(r.headers)
# print('==========================================================')
# print(r.content)
# print('==========================================================')
# # print(r.text)
