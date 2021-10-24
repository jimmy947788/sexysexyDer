import os
import sys
import traceback
import facebook
sys.path.append(os.path.realpath('.'))
from sexpackges.models.enum import Status


if __name__ == '__main__':
    status_filter = [ Status.WAIT, Status.FAILED, Status.FB_POST_TO_PAGE]

    sfilter = ','.join( str(x.value)  for x in status_filter)
    filter = f" and status in ({sfilter}) "

    print(filter)
