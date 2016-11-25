# encoding=utf-8
import re
from werkzeug._compat import text_type, PY2
import os

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
    competitor_dict['name'] = competitor.name
    competitor_dict['company'] = competitor.company
    competitor_dict['position'] = competitor.position
    competitor_dict['photo'] = competitor.photo
    competitor_dict['reason'] = competitor.reason
    competitor_dict['method'] = competitor.method
    competitor_dict['count'] = competitor.count
    return competitor_dict

def message2dict(message):
    message_dict = {}
    message_dict['content'] = message.content
    message_dict['we_id'] = message.we_id
    message_dict['time'] = str(message.time)
    return message_dict