try:
    from ConfigParser import ConfigParser
except ImportError:                 #pragma NO COVER Py3k
    from configparser import ConfigParser
try:
    from StringIO import StringIO
except ImportError:                 #pragma NO COVER Py3k
    from io import StringIO
