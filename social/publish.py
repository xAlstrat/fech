import os
import io

from PIL import Image

from social.credentials import get_instagram_api, get_twitter_api


def get_path(file):
    module_dir = os.path.dirname(__file__)  # get current directory
    return os.path.join(module_dir, file)


def convert_filename_to_jpg(file):
    file_name, file_extension = os.path.splitext(file)
    return '%s.jpg' % file_name


def convert_to_jpg(file):
    file = get_path(file)
    file_name, file_extension = os.path.splitext(file)
    if file_extension.lower() != 'jpg':
        im = Image.open(file)
        rgb_im = im.convert('RGB')
        file = '%s.jpg' % file_name
        rgb_im.save(file)
        return file
    return file


def remove_jpg_cache(file):
    file_name, file_extension = os.path.splitext(get_path(file))
    if file_extension.lower() != 'jpg':
        os.remove('%s.jpg' % file_name, dir_fd=None)


def publish_img_to_instagram(description='', media=None):

    api = get_instagram_api()
    api.login()  # login

    photo_path = media
    api.uploadPhoto(convert_to_jpg(media), caption=description)

    remove_jpg_cache(photo_path)


def publish_img_to_twitter(description='', media=None):

    api = get_twitter_api()
    photo_path = media
    media = convert_to_jpg(media)
    caption = description
    api.PostUpdate(caption, media=media)

    remove_jpg_cache(photo_path)