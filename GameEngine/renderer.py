import pygame
from .base import SceneBase
from .structures import *
from .troops import *

TILE_SIZE = 20  # Each tile is 32x32 pixels
PADDING_SIZE = SceneBase.BASE_PADDING * TILE_SIZE  # Padding space in pixels
WINDOW_WIDTH = SceneBase.BASE_WIDTH * TILE_SIZE + 2 * PADDING_SIZE
WINDOW_HEIGHT = SceneBase.BASE_HEIGHT * TILE_SIZE + 2 * PADDING_SIZE

GRASS_GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)

class SceneRenderer:
    def __init__(self, scene: SceneBase):
        pygame.init()
        self.scene = scene
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Scene Visualizer")
        self.clock = pygame.time.Clock()
        self.running = True
        self.image_cache = {}

    def load_image(self, image_path, width=1, height=1):
        """ Load and scale images, caching them to optimize performance. """
        if (image_path, width, height) not in self.image_cache:
            image = pygame.image.load(image_path).convert_alpha()
            image = pygame.transform.scale(image, (width * TILE_SIZE, height * TILE_SIZE))
            self.image_cache[(image_path, width, height)] = image
        return self.image_cache[(image_path, width, height)]

    def draw_scene(self):
        """ Draw the entire scene. """
        self.screen.fill(DARK_GREEN)  # Background padding color
        pygame.draw.rect(self.screen, GRASS_GREEN, (PADDING_SIZE, PADDING_SIZE,
                                                     SceneBase.BASE_WIDTH * TILE_SIZE,
                                                     SceneBase.BASE_HEIGHT * TILE_SIZE))

        for y in range(SceneBase.BASE_HEIGHT):
            for x in range(SceneBase.BASE_WIDTH):
                draw_x = x * TILE_SIZE + PADDING_SIZE
                draw_y = y * TILE_SIZE + PADDING_SIZE

                tile = self.scene.map[y, x]
                if tile is None:
                    continue

                # Draw buildings (only at their top-left tile)
                if tile["building"] is not None and (x, y) == (tile["building"].x, tile["building"].y):
                    building = tile["building"]
                    img = self.load_image(building.get_image_path(), building.width, building.height)
                    self.screen.blit(img, (draw_x, draw_y))

                troop_size = TILE_SIZE // 1.5  # Shrink troop image to fit multiple in a tile
                max_per_row = TILE_SIZE // 1.5

                troops = list(tile["troops"])
                num_troops = len(troops)

                tile_center_x = draw_x + TILE_SIZE // 2
                tile_center_y = draw_y + TILE_SIZE // 2

                img_size = int(TILE_SIZE * 1)

                for i, troop in enumerate(troops):
                    img = self.load_image(troop.image_path)
                    img = pygame.transform.scale(img, (img_size, img_size))

                    troop_x = tile_center_x - img_size // 2
                    troop_y = tile_center_y - img_size // 2
                    self.screen.blit(img, (troop_x, troop_y))


                # Draw grid outline
                # pygame.draw.rect(self.screen, (0, 0, 0), (draw_x, draw_y, TILE_SIZE, TILE_SIZE), 1)


    def run(self):
        while self.running:
            self.clock.tick(30)
            self.handle_events()
            self.draw_scene()
            pygame.display.flip()

        pygame.quit()

    def handle_events(self):
        """ Handle user interactions like closing the window. """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
