import numpy as np


def otsu_threshold(image):
    min_px = np.amin(image)
    max_px = np.amax(image)
    delta_px = max_px - min_px
    hist = [image[image == min_px + i].size for i in range(delta_px + 1)]
    m = sum(map(lambda x, y: x * y, range(delta_px + 1), hist))
    n = sum(hist)
    max_sigma = -1
    alpha = 0
    beta = 0

    threshold = 0
    for t in range(delta_px):
        alpha += t * hist[t]
        beta += hist[t]
        w = beta / n
        a = alpha / beta - (m - alpha) / (n - beta)

        sigma = w * (1 - w) * a * a
        if sigma > max_sigma:
            max_sigma = sigma
            threshold = t
    threshold += min_px
    return threshold


def binarize(image):
    threshold = otsu_threshold(image)
    image[image > threshold] = 255
    image[image <= threshold] = 0