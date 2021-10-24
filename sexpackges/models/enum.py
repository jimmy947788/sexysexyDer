from enum import IntEnum
from sys import intern

class Status(IntEnum):
    WAIT = 1
    IG_POST_DOWNLOADED = 2
    FB_POST_TO_PAGE = 3
    FB_PUBLISH_TO_GROUP = 4
    FAILED = -1

class FbPostType(IntEnum):
    PHOTOS = 1
    VIDEO = 2