"""This is a module that generates result images."""
import csv
import os
import re
import pygame
from config_parse import load_config

pygame.image.init()
pygame.font.init()

class ResultImageGenerator:
    """Class that generates the images."""

    def __init__(self, config):
        self.config = config
        self.textures = {}
        self.avatars = {}
        self.results = []
        defaults = load_config("defaults.yml")
        ResultImageGenerator.set_defaults(self.config, defaults)
        self._load_textures()
        self._load_avatars()
        self._load_results()
        try:
            os.makedirs(self.config["output_folder"])
        except FileExistsError:
            if not os.access(self.config["output_folder"],
                             os.R_OK | os.W_OK | os.X_OK):
                raise Exception("Output folder does not have adequate perms!")
        if self.config["result_style"] == "leaderboard":
            self.options = self.config["ldrbd_options"]

    @staticmethod
    def set_defaults(config, defaults):
        """Sets default values for the configuration."""
        defaults = load_config("default.yml")
        for k, val in defaults.items():
            if k not in config:
                config[k] = val
            elif k in config and isinstance(val, dict):
                ResultImageGenerator.set_defaults(config[k], val[k])

    def _load_textures(self):
        files = os.listdir(self.config["texture_folder"])
        for filename in files:
            # Stores texture based on the filename without extension
            self.textures[filename.rpartition(".")[0]] = \
                pygame.image.load(
                    os.path.join(self.config["texture_folder"], filename))

    def _load_avatars(self):
        files = os.listdir(self.config["avatar_folder"])
        for filename in files:
            # Stores avatar based on the filename without extension
            self.avatars[filename.rpartition(".")[0]] = \
                pygame.image.load(
                    os.path.join(self.config["avatar_folder"], filename))

    def _load_results(self):
        # results file should NOT have file extension!
        with open(self.config["results_file"] + ".csv", "r") as file:
            reader = csv.reader(file)
            for rnum, row in enumerate(reader):
                # Constructs a dict for every contestant based on given result format.
                self.results.append({})
                ind = 0
                while ind < len(row):
                    fmt = self.config["result_format"][ind]
                    if res := re.match(r"(.*)\[(\d+)\]$", fmt):
                        # Multi-column data of constant size.
                        attr = res.group(1)
                        self.results[rnum][attr] = []
                        count = int(res.group(2))
                        for i in range(count):
                            self.results[rnum][attr].append(row[ind + i])
                        ind += count
                    elif res := re.match(r"(.*)\[(.*)\]$", fmt):
                        # Multi-column data of non-constant size.
                        attr = res.group(1)
                        var = res.group(2)
                        if not isinstance(count := self.results[rnum][var], int):
                            raise Exception("Variable size must be integer")
                        for i in range(count):
                            self.results[rnum][attr].append(row[ind + i])
                        ind += count
                    else:
                        self.results[rnum][fmt] = row[ind]
        self.results.sort(key=lambda x: x[self.config["sort_by"]],
                          reverse=self.config["sort_reverse"])

    def render_leaderboard(self):
        opts = self.options
