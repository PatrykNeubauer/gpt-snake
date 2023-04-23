import pygame
import random
from agent import Agent
import argparse

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--manual", action="store_true", help="manual control of the snake."
)
parser.add_argument("--api_key", type=str, help="OpenAI API key.")
parser.add_argument(
    "-v", "--verbose", action="store_true", help="output GPT-3 prompts and responses"
)
args = parser.parse_args()

# Define constants for the game window
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
CELL_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Define directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

dir2text = {(0, -1): "UP", (0, 1): "DOWN", (-1, 0): "LEFT", (1, 0): "RIGHT"}

# Initialize Pygame
pygame.init()

# Set up the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake Game")

# Set up the clock
clock = pygame.time.Clock()


# Define the Snake class
class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [((WINDOW_WIDTH / 2), (WINDOW_HEIGHT / 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = GREEN

    def get_head_position(self):
        return self.positions[0]

    def turn(self, point):
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return
        else:
            self.direction = point

    def move(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = (
            ((cur[0] + (x * CELL_SIZE)) % WINDOW_WIDTH),
            (cur[1] + (y * CELL_SIZE)) % WINDOW_HEIGHT,
        )
        if new in self.positions[2:]:
            self.reset()
            return False
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()
            return True

    def reset(self):
        self.length = 1
        self.positions = [((WINDOW_WIDTH / 2), (WINDOW_HEIGHT / 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

    def draw(self, surface):
        for p in self.positions:
            r = pygame.Rect((p[0], p[1]), (CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(surface, self.color, r)
            pygame.draw.rect(surface, BLACK, r, 1)

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.turn(UP)
                elif event.key == pygame.K_DOWN:
                    self.turn(DOWN)
                elif event.key == pygame.K_LEFT:
                    self.turn(LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.turn(RIGHT)


class GPTSnake(Snake):
    def __init__(self, api_key, verbose):
        super().__init__()
        self.agent = Agent(api_key, verbose)

    @staticmethod
    def normalize_position(position):
        return (int(position[0] // CELL_SIZE), int(position[1] // CELL_SIZE))

    def handle_state(self, food_position, grid_width, grid_height):
        """
        Instead of handling keys, send the game state to GPT-3 and then turn accordingly
        """
        game_state = {
            "snake_positions": [
                self.normalize_position(position) for position in self.positions
            ],
            "prev_direction": dir2text[self.direction],
            "food_position": self.normalize_position(food_position),
            "grid_width": grid_width,
            "grid_height": grid_height,
        }

        prediction = self.agent.predict(game_state)

        if "UP" in prediction:
            self.turn(UP)
        elif "DOWN" in prediction:
            self.turn(DOWN)
        elif "LEFT" in prediction:
            self.turn(LEFT)
        elif "RIGHT" in prediction:
            self.turn(RIGHT)


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def get_position(self):
        return self.position

    def randomize_position(self):
        self.position = (
            random.randint(0, GRID_WIDTH - 1) * CELL_SIZE,
            random.randint(0, GRID_HEIGHT - 1) * CELL_SIZE,
        )

    def draw(self, surface):
        r = pygame.Rect((self.position[0], self.position[1]), (CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, BLACK, r, 1)


# Define the game loop
def main():
    # Set up the font
    font = pygame.font.Font(None, 30)

    # Set up the score
    score = 0

    # Set up the snake and food
    if args.manual:
        snake = Snake()
    else:
        snake = GPTSnake(args.api_key, args.verbose)
    food = Food()

    # Game loop
    while True:
        # Handle events
        if type(snake) == Snake:
            snake.handle_keys()
        elif type(snake) == GPTSnake:
            snake.handle_state(
                food_position=food.position,
                grid_width=GRID_WIDTH,
                grid_height=GRID_HEIGHT,
            )

        # Move the snake
        # Check for collisions with the food
        if snake.move():
            if snake.get_head_position() == food.position:
                snake.length += 1
                score += 1
                food.randomize_position()
        else:
            score = 0

        # Draw everything
        screen.fill(WHITE)
        snake.draw(screen)
        food.draw(screen)
        text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(text, (10, 10))
        pygame.display.update()

        # Wait for the next frame
        clock.tick(10)


# Run the game
if __name__ == "__main__":
    main()

# Quit Pygame
pygame.quit()
