from configparser import ConfigParser
import os


class Utils(object):
    def __init__(self, root_path):
        self.config = ConfigParser()
        self.config.read_file(open(os.path.join(root_path, "config.ini")))

    def get_token(self):
        return self.config["TELEGRAM"]['token']
