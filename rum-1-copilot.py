#!/usr/bin/env python
# -*- coding: utf-8 -*-
# !pip install osmnx
# !pip install scikit-learn

import os
import sys
import json
from datetime import datetime, timezone
import numpy as np
print ("Numpy Version: %s" % np.__version__)
import scipy
print ("Scipy Version: %s" % scipy.__version__)
import osmnx as ox
print ("Osmnx Version: %s" % ox.__version__)
#import networkx as nx
#import taxicab as tc
#!pip install taxicab
import matplotlib.pyplot as plt

import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, Point
from shapely.ops import transform

import pyproj
geod = pyproj.Geod(ellps="WGS84")

dir_app = os.path.dirname(sys.argv[0])
print ("Directory: %s" % dir_app)



