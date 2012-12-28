try:
    u = unicode
except NameError:                   #pragma NO COVER Python >= 3.0
    u = str
    b = bytes
else:                               #pragma NO COVER Python < 3.0
    b = str

try:
    from ConfigParser import ConfigParser
except ImportError:                 #pragma NO COVER Py3k
    from configparser import ConfigParser

try:
    from StringIO import StringIO
except ImportError:                 #pragma NO COVER Py3k
    from io import StringIO
    from io import BytesIO
else:                               #pragma NO COVER Py2
    BytesIO = StringIO

def must_decode(value):             #pragma NO COVER
    if type(value) is b:
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin1')
    return value

def must_encode(value):             #pragma NO COVER
    if type(value) is u:
        return value.encode('utf-8')
    return value
