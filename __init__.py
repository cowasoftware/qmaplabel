# -*- coding: utf-8 -*-

from qgis.core import QgsApplication
import logging

logger = logging.getLogger()
def write_log_message(message, tag, level):
    with open('/tmp/crmap.log', 'a') as logfile:
        logfile.write('{tag}({level}): {message}'.format(tag=tag, level=level, message=message))


def classFactory(iface): 
    from .hdmap import HDMap
    logging.basicConfig(level=logging.DEBUG, 
                filename='/tmp/qgisapp.log', 
                filemode='w', 
                format='%(name)s - %(levelname)s - %(message)s')

    #QgsApplication.messageLog().messageReceived.connect(write_log_message)

    return HDMap(iface)
