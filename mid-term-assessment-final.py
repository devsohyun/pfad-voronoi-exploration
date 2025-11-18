import numpy as np
from noise import pnoise2
from py5canvas import *
from scipy.spatial import Delaunay, Voronoi

canvas_width = 638
canvas_height = 900

PATTERN_TYPE = "perlin"  # Options: "random", "perlin", "none"
isPreviewEnabled = False  # perlin noise preview
num_points = 900  # defalt: 800
noise_scale = 0.005  # # defalt: 0.003 = zoon level (smaller: broader patterns, larger: tighter patterns)
diagram_colour = 255  # option: 0, 255

seed = 12  # seed for perlin noise
octaves = 4  # more octaves = more detail in noise (only integers are allowed)
persistence = 0.6  # defalt: 0.6
lacunarity = 4.0  # defalt: 2.0
power = 6.0  # defalt: 6.0 = value for clustering

t = 0


def perlin_value(_x, _y, _scale=0.01, _t=0):
    return pnoise2(
        _x * _scale,
        _y * _scale,
        octaves=octaves,
        persistence=persistence,
        lacunarity=lacunarity,
        repeatx=1024,
        repeaty=1024,
        base=int(_t * 100),
    )


# This one is for testing random distribution
def get_random_points(_num, _width, _height):
    # generate random points
    np.random.seed(24)
    points = np.random.rand(_num, 2) * [_width, _height]  # scale to canvas size
    return points


# Use this for clustered distribution
def get_perlin_noise_points(_num, _width, _height, _scale=0.003, _t=0):
    np.random.seed(seed)  # for consistency
    points = []
    attempts = 0
    max_attempts = _num * 100

    while len(points) < _num and attempts < max_attempts:
        # random position on canvas
        x = np.random.rand() * _width
        y = np.random.rand() * _height

        # sample Perlin noise at this position
        n = perlin_value(x, y, _scale, _t)

        # remap noise (-1..1 → 0..1)
        brightness = (n + 1) / 2

        # use brightness as probability (bright areas = more points)
        # probability = brightness
        probability = brightness**power  # add power value to make it more extream

        if np.random.rand() < probability:
            points.append([x, y])

        attempts += 1

    return np.array(points)


def draw_perlin_preview(_t):
    resolution = 100  # set lower resolution for faster drawing
    cell_width = canvas_width / resolution
    cell_height = canvas_height / resolution

    for i in range(resolution):
        for j in range(resolution):
            # use canvas coordinates (same as point generation)
            x = i * cell_width + cell_width / 2
            y = j * cell_height + cell_height / 2

            # sample at canvas coordinates
            n = perlin_value(x, y, noise_scale, _t)

            # remap to brightness
            brightness = (n + 1) / 2

            # apply same power function as point generation
            brightness = brightness**power

            fill(brightness * 255)
            no_stroke()
            rect(i * cell_width, j * cell_height, cell_width, cell_height)


def setup():
    create_canvas(canvas_width, canvas_height)
    no_loop()


def draw():
    # background(0, 0)  # fully resets the canvas
    background(0)  # comment if you export to AxiDraw

    if isPreviewEnabled:
        draw_perlin_preview(t)

    if PATTERN_TYPE == "random":
        points = get_random_points(num_points, canvas_width, canvas_height)
    elif PATTERN_TYPE == "perlin":
        points = get_perlin_noise_points(
            num_points, canvas_width, canvas_height, noise_scale, t
        )
    elif PATTERN_TYPE == "none":
        return

    # Create Voronoi and Delaunay structures
    vor = Voronoi(points)
    tri = Delaunay(points)

    ### ---- Comment/Uncomment each elements below to find your style ---- ###

    ## Draw Delaunay Triangulation
    stroke("#A85219")
    stroke_weight(1)
    no_fill()

    for simplex in tri.simplices:
        # each simplex contains indices of 3 points forming a triangle
        p0 = points[simplex[0]]
        p1 = points[simplex[1]]
        p2 = points[simplex[2]]

        # draw the three edges of the triangle
        line(p0[0], p0[1], p1[0], p1[1])
        line(p1[0], p1[1], p2[0], p2[1])
        line(p2[0], p2[1], p0[0], p0[1])

    ## Draw Voronoi edges (ridges)
    stroke(diagram_colour)
    stroke_weight(1)
    for ridge_vertices in vor.ridge_vertices:
        # skip ridges that go to infinity (contain -1)
        if -1 not in ridge_vertices:
            v0 = vor.vertices[ridge_vertices[0]]
            v1 = vor.vertices[ridge_vertices[1]]
            line(v0[0], v0[1], v1[0], v1[1])

    ## Draw Delaunay Triangulation points
    fill(diagram_colour)
    no_stroke()
    for point in vor.points:
        circle(point[0], point[1], 5)

    ## Draw Voronoi Points
    # fill(diagram_colour)
    # no_stroke()
    # for vertex in vor.vertices:
    #     circle(vertex[0], vertex[1], 3)


run()
