# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MESAWildfireLoader
                                 A QGIS plugin
 This plugin loads Active Wildfire text files to the Layers Panel
                             -------------------
        begin                : 2016-11-24
        copyright            : (C) 2016 by Thembani Moitlhobogi, MESA SADC THEMA
        email                : taxmanyana@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MESAWildfireLoader class from file MESAWildfireLoader.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .mesa_wildfire_loader import MESAWildfireLoader
    return MESAWildfireLoader(iface)
