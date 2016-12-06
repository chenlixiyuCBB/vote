# encoding=utf-8
import base64
import re
from werkzeug._compat import text_type, PY2
import os

from app import app

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def secure_filename(filename):
    _filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9_.-]')
    _windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1',
                             'LPT2', 'LPT3', 'PRN', 'NUL')
    if isinstance(filename, text_type):
        from unicodedata import normalize
        filename = normalize('NFKD', filename).encode('utf-8', 'ignore')
        if not PY2:
            filename = filename.decode('utf-8')
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')
    filename = str(_filename_ascii_strip_re.sub('', '_'.join(
        filename.split()))).strip('._')

    if os.name == 'nt' and filename and \
                    filename.split('.')[0].upper() in _windows_device_files:
        filename = '_' + filename

    return filename


def competitor2dict(competitor):
    competitor_dict = {}
    competitor_dict['id'] = competitor.id
    competitor_dict['name'] = competitor.name
    competitor_dict['company'] = competitor.company
    competitor_dict['position'] = competitor.position
    competitor_dict['photo_name'] = competitor.photo
    try:
        with open(os.path.join(app.config['UPLOAD_FOLDER'], competitor.photo), 'rb') as image:
            competitor_dict['photo'] = image.read()
    except:
        competitor_dict['photo'] = ''
    competitor_dict['reason'] = competitor.reason
    competitor_dict['method'] = competitor.method
    competitor_dict['count'] = competitor.count
    competitor_dict['reference_id'] = competitor.reference_id
    competitor_dict['status'] = competitor.status
    return competitor_dict


def message2dict(message):
    message_dict = {}
    message_dict['content'] = message.content
    message_dict['we_id'] = message.we_id
    message_dict['time'] = str(message.time)
    return message_dict


def decode_base64(data):
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += b'=' * missing_padding
    data = data.decode('base64')
    return data

def competitors2list(competitors):
    competitors_list = []
    for cur_competitor in competitors:
        cur_competitor = competitor2dict(cur_competitor)
        competitors_list.append(cur_competitor)
    return competitors_list