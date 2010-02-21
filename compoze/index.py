from setuptools.package_index import PackageIndex


class CompozePackageIndex(PackageIndex):

    def __init__(self, *args, **kwargs):
        PackageIndex.__init__(self, *args, **kwargs)
        self.debug_msgs = []
        self.info_msgs = []
        self.warn_msgs = []

    def debug(self, msg, *args):
        self.debug_msgs.append((msg, args))

    def info(self, msg, *args):
        self.info_msgs.append((msg, args))

    def warn(self, msg, *args):
        self.warn_msgs.append((msg, args))
