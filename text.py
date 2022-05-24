import numpy
import numpy as np

class SpeedOMeter:
    def __init__(self, speed, font, pos):
        self.pos = pos
        self.font = font
        self.get_text(speed)
        print(font)

    def get_text(self, speed):
        self.text = self.font.render(f"Delay: {speed} ms", True, "black")
        self.rect = self.text.get_rect(topleft=self.pos)

    def draw(self, screen):
        screen.blit(self.text, self.rect)

def points_to_array(points):
    max_x = max(points, key=lambda a: a[0])
    max_y = max(points, key=lambda a: a[1])
    print(max_x[0], max_y[1])
    arr = np.zeros((max_y[1] + 1, max_x[0] + 1), dtype=bool)
    for y, x in points:
        arr[x][y] = True
    print(arr)
    return arr


def export_to_bitmap(points):
    arr = points_to_array(points)

def export_to_csv(points):
    arr = points_to_array(points)
    numpy.savetxt("export.csv", arr, delimiter=",", fmt='%d')

def load_from_csv():
    arr = numpy.genfromtxt("export.csv", delimiter=",")
    points_x, points_y = np.where(arr == True)
    points = set(zip(points_y, points_x))
    print(points)
    return points


