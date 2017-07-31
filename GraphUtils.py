import numpy as np

class Point:
    def __init__(self, coord, index, start, depth=0):
        self.coord = coord
        self.index = index
        self.depth = depth
        self.start = start


def vectorSearch(current_xy, key_pixels, matrix, depth=0, start_xy=None, parent=None, is_start=False, vector_points=None):
    if start_xy is None:
        start_xy = current_xy
    x, y = current_xy
    nearest = [(x - 1, y - 1), (x - 1, y), (x - 1, y + 1),
               (x, y - 1),                 (x , y + 1),
               (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)]
    if is_start:
        vectors = []
        if np.sum(matrix[x - 1: x + 2, y - 1: y + 2]) != 3:
            return None
        for i, j in nearest:
            if matrix[i, j] == 1 and (i, j) != (x, y):
                vector_points.append([])
                final_vector = vectorSearch(np.array((i, j)), key_pixels,
                                             matrix,
                                             parent=current_xy,
                                             vector_points=vector_points[len(vector_points) - 1], start_xy=start_xy)
                vectors.append(final_vector)
        return vectors
    else:
        for i, j in nearest:
            if (i, j) != tuple(parent) and [i, j] in key_pixels.tolist():
                vector_points.append(current_xy)
                return (current_xy - start_xy) * (2 ** -depth)
        if current_xy.tolist() in key_pixels.tolist():
            return 0, 0
        else:
            for i, j in nearest:
                if matrix[i, j] == 1 and (i, j) != tuple(parent) and (i, j) != (x, y):
                    vector_points.append(current_xy)
                    # print("35: debug", current_xy, start_xy, current_xy - start_xy, depth)
                    return (current_xy - start_xy) * (2 ** -depth) + \
                           vectorSearch(np.array((i, j)), key_pixels, matrix, depth=depth + 1,
                                         parent=current_xy, vector_points=vector_points, start_xy=start_xy)


def find_neighbours(xy, points):
    nearest = []
    for i in points:
        if -1 <= (i[0] - xy[0]) <= 1 and -1 <= (i[1] - xy[1]) <= 1 and i != xy:
            nearest.append(i)
    return nearest


def leeAlgorithm(start_points, all_points):
    queue = []
    temp_edges = []
    final_edges = []
    marked_points = {}
    k = 0
    for start in start_points:
        marked_points[start] = Point(start, 0, start)
        for neighbour in find_neighbours(start, all_points):
            temp_edges.append([marked_points[start]])
            neighbour_point = Point(neighbour, k, start, 1)
            temp_edges[k].append(neighbour_point)
            queue.append(neighbour_point)
            marked_points[neighbour] = neighbour_point
            k += 1

    while len(queue) != 0:
        current_point = queue.pop(0)
        for neighbour in find_neighbours(current_point.coord, all_points):
            temp_point = Point(neighbour, current_point.index, current_point.start, current_point.depth + 1)
            if not contains_tuple(neighbour, marked_points.keys()):
                marked_points[neighbour] = temp_point
                queue.append(temp_point)
                temp_edges[temp_point.index].append(temp_point)
            elif marked_points[neighbour].start != current_point.start:
                final_edges.append(temp_edges[current_point.index] + temp_edges[marked_points[neighbour].index][::-1])
    return final_edges



def contains_tuple(obj, iterable) -> bool:
    for i in iterable:
        if tuple(i) == tuple(obj):
            return True
    return False


def contains_reversed(obj, iterable) -> bool:
    for i in iterable:
        if not i == obj and not i.is_reversed(obj):
            return True
    return False


def fullLen(edge):
    sm = 0
    for i in range(len(edge) - 1):
        sm += np.sqrt((edge[i][0] - edge[i + 1][0]) ** 2 + (edge[i][1] - edge[i + 1][1]) ** 2)
    return sm
