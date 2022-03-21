import sys

import pygame


class Game:
    TILE_SIZE = 30
    TILES = (20, 25)

    SCREEN_WIDTH = TILES[1] * TILE_SIZE
    SCREEN_HEIGHT = TILES[0] * TILE_SIZE
    SIDE_PANEL = 200*1

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH + self.SIDE_PANEL, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Game of Life")
        self.clock = pygame.time.Clock()

        self.points = {(5, 6), (5, 7), (5, 8), (8, 5)}
        print(self.points)

    def draw_background(self):
        self.screen.fill("grey70")
        # print("green")

    def draw_grid(self):
        tile_size = self.TILE_SIZE
        scr_height, scr_width = self.SCREEN_HEIGHT, self.SCREEN_WIDTH
        cols = scr_width // tile_size
        rows = scr_width // tile_size

        for c in range(cols + 1):
            pygame.draw.line(self.screen, "white", (c * tile_size, 0), (c * tile_size, scr_height))
        for r in range(rows + 1):
            pygame.draw.line(self.screen, "white", (0, r * tile_size), (scr_width, r * tile_size))

    def draw_side_panel(self):
        pygame.draw.rect(self.screen, "blue", (self.SCREEN_WIDTH, 0, self.SIDE_PANEL, self.SCREEN_HEIGHT))

    def draw_tiles(self):
        for x, y in self.points:
            surface = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
            surface.fill("yellow")
            self.screen.blit(surface, (x * self.TILE_SIZE, y * self.TILE_SIZE))

    def simulate(self):
        tempcells = self.points.copy()
        def find_neighbors(cell):
            x, y = cell
            cells = set()
            for xr in range(x-1, x+2):
                for yr in range(y-1, y+2):
                    cells.add((xr, yr))
            return cells

        for cell in self.points:
            neighbors = find_neighbors(cell)
            living_neighbors = self.points.intersection(neighbors)
            dead_neighbors = neighbors - living_neighbors
            if not (1 < len(living_neighbors) < 3):
                # cell dies
                tempcells.remove(cell)
            for dn in dead_neighbors:
                dead_neigh_neigbors = find_neighbors(dn)
                living_neighbors = self.points.intersection(dead_neigh_neigbors)
                if len(living_neighbors) == 3:
                    tempcells.add(dn)
        self.points = tempcells


    def run(self):
        self.simulate()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(42)
            self.draw_background()
            self.draw_tiles()
            self.draw_grid()
            self.draw_side_panel()

            pygame.display.update()
            self.clock.tick(60)


def main():
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
