import sys
import button
import pygame
import SpriteSheet

from text import *


class Game:
    TILE_SIZE = 30
    TILES = (20, 25)

    SCREEN_WIDTH = TILES[1] * TILE_SIZE
    SCREEN_HEIGHT = TILES[0] * TILE_SIZE
    SIDE_PANEL = 200*1

    def __init__(self):
        self.mouse_pressed = False
        self.x_shift = 0
        self.y_shift = 0
        self.scroll_x = 0
        self.scroll_y = 0

        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH + self.SIDE_PANEL, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Game of Life")
        self.clock = pygame.time.Clock()
        
        # Buttons
        sprite_sheet = SpriteSheet.SpriteSheet("graphics/HUD/HUD_spritesheet.png")
        images = SpriteSheet.get_ratio_images(50, sprite_sheet, "save.png", "home.png", "plus.png", "minus.png")
        posx = self.SCREEN_WIDTH + self.SIDE_PANEL // 2
        self.simulate_button = button.ToggleButton(posx, 45, *sprite_sheet.get_sprites("right.png", "pause.png"))
        self.buttons = [button.Button(posx, 170+images.get_height()*h, images) for h, images in enumerate(images, 1)]
        self.button_action = [self.store_tiles, self.reload_tiles, self.increase_simulation_speed,
                              self.decrease_simulation_speed]

        # self.points = {(5, 6), (5, 7), (5, 8)}
        self.points = {(4, 1), (5, 2), (3, 3), (4, 3), (5, 3)}
        self.back_points = set()

        self.simulation_speed = 1000
        self.font = pygame.font.Font('fonts/Pixeltype.ttf', 50)
        self.speed_o_meter = SpeedOMeter(self.simulation_speed, pygame.font.Font('fonts/Pixeltype.ttf', 40),
                                         (self.SCREEN_WIDTH + 10, int(self.screen.get_height() // 8 + 110)))

        self.timer = pygame.USEREVENT + 1
        self.change_simulation_speed(self.simulation_speed)
        self.iterations = 0

        self.scroll_timer = pygame.USEREVENT + 2
        pygame.time.set_timer(self.scroll_timer, 60)

        self.stopped = True

    def show_background(self):
        self.screen.fill("grey70")
        # print("green")

    def show_grid(self):
        tile_size = self.TILE_SIZE
        scr_height, scr_width = self.SCREEN_HEIGHT, self.SCREEN_WIDTH
        cols = scr_width // tile_size
        rows = scr_width // tile_size

        for c in range(cols + 1):
            pygame.draw.line(self.screen, "white", (c * tile_size, 0), (c * tile_size, scr_height))
        for r in range(rows + 1):
            pygame.draw.line(self.screen, "white", (0, r * tile_size), (scr_width, r * tile_size))

    def show_side_panel(self):
        pygame.draw.rect(self.screen, "blue", (self.SCREEN_WIDTH, 0, self.SIDE_PANEL, self.SCREEN_HEIGHT))
        self.simulate_button.draw(self.screen)
        for btn in self.buttons:
            btn.draw(self.screen)
        score_surf = self.font.render(f"Iteration: {self.iterations}", True, "black")
        score_rect = score_surf.get_rect(topleft=(self.SCREEN_WIDTH + 10, int(self.screen.get_height() // 8 + 60)))
        self.screen.blit(score_surf, score_rect)
        self.speed_o_meter.draw(self.screen)

    def show_tiles(self):
        for x, y in self.points:
            surface = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
            surface.fill("yellow")
            self.screen.blit(surface, ((x + self.x_shift) * self.TILE_SIZE, (y + self.y_shift) * self.TILE_SIZE))

    def draw_tiles(self):
        if self.stopped and self.mouse_pressed:
            mx, my = pygame.mouse.get_pos()
            if not (mx < self.SCREEN_WIDTH and my < self.SCREEN_HEIGHT):
                return
            pos = (mx//self.TILE_SIZE, my // self.TILE_SIZE)
            but_l, but_m, but_r = pygame.mouse.get_pressed(3)

            if but_l and not (but_m or but_r):
                if pos not in self.points:
                    print(f"add {pos}")
                    self.points.add(pos)
            elif but_r and not (but_m or but_l):
                if pos in self.points:
                    self.points.remove(pos)
                    print(f"rem {pos}")

    def scroll(self):
        if self.scroll_y:
            self.y_shift += 1 * self.scroll_y
        if self.scroll_x:
            self.x_shift += 1 * self.scroll_x
        # print(self.x_shift, self.y_shift)

    def store_tiles(self):
        self.back_points = self.points.copy()
        export_to_csv(self.points)
        print("points stored")

    def reload_tiles(self):
        # self.points = self.back_points.copy() TODO make seperate function for export handling
        self.points = load_from_csv()
        self.x_shift, self.y_shift = 0,0
        print("points reloaded")

    def change_simulation_speed(self, speed):
        self.simulation_speed = speed
        pygame.time.set_timer(self.timer, speed)  # Simulation speed
        self.speed_o_meter.get_text(self.simulation_speed)

    def increase_simulation_speed(self):
        speed = self.simulation_speed - 100 if self.simulation_speed - 100 > 0 else 10
        self.change_simulation_speed(speed)
        print(f"increase speed: {self.simulation_speed}")

    def decrease_simulation_speed(self):
        self.change_simulation_speed(self.simulation_speed + 100)
        print(f"decrease speed: {self.simulation_speed}")

    # def save(self):
    #     pass
    #     export_to_bitmap(self.points)

    def simulate(self):
        temp_cells = self.points.copy()

        def find_neighbors(ref_cell):
            x, y = ref_cell
            cells = set()
            for xr in range(x-1, x+2):
                for yr in range(y-1, y+2):
                    cells.add((xr, yr))
            return cells-{ref_cell}

        for cell in self.points:
            neighbors = find_neighbors(cell)
            # print(cell, neighbors)
            living_neighbors = self.points.intersection(neighbors)
            dead_neighbors = neighbors - living_neighbors
            # print(f"{living_neighbors=}\n{dead_neighbors=}")
            if not (1 < len(living_neighbors) <= 3):
                # cell dies
                temp_cells.remove(cell)
            for dn in dead_neighbors:
                dead_neigh_neigbors = find_neighbors(dn)
                living_neighbors = self.points.intersection(dead_neigh_neigbors)
                if len(living_neighbors) == 3:
                    temp_cells.add(dn)
        self.points = temp_cells


    def run(self):
        while True:
            self.stopped = not self.simulate_button.get_state()
            # print(self.stoped)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(42)
                if event.type == self.timer:
                    if not self.stopped:
                        self.simulate()
                        self.iterations += 1
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # print("MOUSE")
                    self.mouse_pressed = True
                    for i, btn in enumerate(self.buttons):
                        if btn.check_collision():
                            self.button_action[i]()

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_pressed = False

                if event.type == pygame.MOUSEWHEEL:
                    if event.y < 0:
                        if (size := self.TILE_SIZE - 3) > 0:
                            self.TILE_SIZE = size
                    elif event.y > 0:
                        self.TILE_SIZE += 3
                    # print(self.TILE_SIZE)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.scroll_y = -1
                    if event.key == pygame.K_UP:
                        self.scroll_y = 1

                    if event.key == pygame.K_RIGHT:
                        self.scroll_x = -1
                    if event.key == pygame.K_LEFT:
                        self.scroll_x = 1
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                        self.scroll_y = 0

                    if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                        self.scroll_x = 0

                if event.type == self.scroll_timer:
                    self.scroll()

            self.draw_tiles()
            self.show_background()
            self.show_tiles()
            if self.TILE_SIZE > 12:
                self.show_grid()
            self.show_side_panel()

            pygame.display.update()
            self.clock.tick(60)


def main():
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
