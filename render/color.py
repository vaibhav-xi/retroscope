import colorsys


def rotate_hue(color, degrees: float):

    r, g, b = color

    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    h = (h + degrees / 360.0) % 1.0

    return colorsys.hsv_to_rgb(h, s, v)
