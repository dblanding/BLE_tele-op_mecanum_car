# 2D geometry helper functions

from math import atan2, sin, cos, pi, sqrt

def p2r(r, theta):
    """Convert polar coords (r, theta) to rectangular coords (x,y)"""
    x = r * cos(theta)
    y = r * sin(theta)
    return (x, y)

def r2p(x, y):
    """Convert rect coords (x, y) to polar (r, theta)"""
    r = sqrt(x*x + y*y)
    theta = atan2(y, x)
    return (r, theta)
