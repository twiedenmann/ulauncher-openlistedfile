import glob

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent, PreferencesUpdateEvent, PreferencesEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from os.path import expanduser
import logging
import subprocess
import os
import re
import shlex

logger = logging.getLogger(__name__)

class OpenlistedfileExtension(Extension):

    def __init__(self):
        super(OpenlistedfileExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())

    def parse_config(self):
        home = expanduser("~")
        hosts = []

        try:
            with open(extension.configfile, "r") as config:
                for line in config:
                    line_lc = line.lower()
                    logger.debug("File = '{}'", line_lc)
                    hosts.append(line_lc.strip("host").strip("\n").strip())

        except:
            logger.debug("config not found!")

        return hosts

    def launch_file(self, addr):
        logger.debug("Launching file " + addr)

        if self.terminal:
            subprocess.Popen(["xdg-open", addr])

class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):
        data = event.get_data()
        extension.launch_terminal(data)

class PreferencesUpdateEventListener(EventListener):

    def on_event(self, event, extension):

        if event.id == "openlistedfile_file":
            extension.configfile = event.new_value

class PreferencesEventListener(EventListener):

    def on_event(self, event, extension):
        extension.configfile = event.preferences["openlistedfile_file"]

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        icon = "images/icon.png"
        items = []
        arg = event.get_argument()
        files = extension.parse_config()

        files = list(dict.fromkeys(files))
        files.sort()

        if arg is not None and len(arg) > 0:
            files = [x for x in files if arg in x]

        for file in files:
            items.append(ExtensionResultItem(icon=icon,
                                            name=file,
                                            description="Open file '{}' ".format(file),
                                            on_enter=ExtensionCustomAction(file, keep_app_open=False)))

        # If there are no results, let the user connect to the specified server.
        if len(items) <= 0:
            items.append(ExtensionResultItem(icon=icon,
                                            name=arg,
                                            description="Open file {} ".format(arg),
                                            on_enter=ExtensionCustomAction(arg, keep_app_open=False)))

        return RenderResultListAction(items)

if __name__ == '__main__':
    OpenlistedfileExtension().run()
