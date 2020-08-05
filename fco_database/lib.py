import os
import string
import uuid
from django.utils.deconstruct import deconstructible
from random import randint
import random


@deconstructible
class RandomFileName(object):
    def __init__(self, path):
        self.path = os.path.join(path, "%s%s")

    def __call__(self, _, filename):
        # @note It's up to the validators to check if it's the correct file type in name or if one even exist.
        extension = os.path.splitext(filename)[1]
        return self.path % (uuid.uuid4().hex, extension)


domains = ["hotmail.com", "gmail.com", "aol.com", "mail.com" , "mail.kz", "yahoo.com"]

letters = string.ascii_lowercase[:12]


def get_random_domain(domains):
    return random.choice(domains)


def get_random_name(letters, length):
    return ''.join(random.choice(letters) for i in range(length))


def generate_random_email(length):
    return get_random_name(letters, length) + '@' + get_random_domain(domains)


def generate_random_date():
    return str(randint(2018, 2020)) + "-" + str(randint(1, 12)) + "-" + str(randint(1, 28))


def generate_random_ip():
    return str(randint(000, 999)) + "." + \
           str(randint(000, 999)) + "." + \
           str(randint(000, 999)) + "." + \
           str(randint(000, 999))


def generate_random_image():
    return "test_images/" + str(random.randint(0, 16)) + ".jpg"


def generate_random_lat():
    return random.uniform(-36.256084, -36.788364)


def generate_random_lng():
    return random.uniform(147.949859, 148.371674)


def random_data():
    rtn = {'date_obs': generate_random_date(), 'description': "---This is a computer generated record---",
           'email': generate_random_email(10), 'loc_lat': generate_random_lat(), 'loc_lng': generate_random_lng(),
           'contact': bool(random.getrandbits(1)), 'image_apr': bool(random.getrandbits(1)),
           'verified': bool(random.getrandbits(1)), 'verified_by': "computer", 'entered_ip': generate_random_ip(),
           'image': generate_random_image()}
    return rtn
