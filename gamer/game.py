import pygame
import sys

# Initialize Pygame
pygame.init()

# Define colors
RED = (255, 0, 0)
PINK = (255, 192, 203)
WHITE = (255, 255, 255)

# Set the size of the chessboard
BOARD_SIZE = 12
SQUARE_SIZE = 100  # Size of each square

# Set up the display
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('Scrolling Chessboard')

# Define the character (a simple square for now)
character_width, character_height = 200, 200
character_color = WHITE
character_x = WINDOW_SIZE // 2 - character_width // 2
character_y = WINDOW_SIZE - character_height - 10  # Placed at the bottom of the screen

# Scrolling parameters
scroll_speed = 5
offset_y = 0

# Load and resize the character image
character_image = pygame.image.load('50.png')
character_image = pygame.transform.scale(character_image, (character_width, character_height))

# Update the character's position to be centered at the bottom
character_x = WINDOW_SIZE // 2 - character_width // 2
character_y = WINDOW_SIZE - character_height - 10

# Define sensitivity, acceleration, and drift parameters
sensitivity = 2  # Base speed
acceleration = 0.5  # How quickly the character accelerates
max_speed = 10  # Maximum speed the character can reach
drift = 0.95  # How quickly the character slows down after releasing the key

# Define initial velocities
velocity_x = 0
velocity_y = 0


def handle_input():
    global velocity_x, velocity_y

    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        velocity_y -= acceleration  # Accelerate upward
    if keys[pygame.K_DOWN]:
        velocity_y += acceleration  # Accelerate downward
    if keys[pygame.K_LEFT]:
        velocity_x -= acceleration  # Accelerate left
    if keys[pygame.K_RIGHT]:
        velocity_x += acceleration  # Accelerate right

    # Apply drift (deceleration) when no keys are pressed
    if not keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
        velocity_y *= drift
    if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
        velocity_x *= drift

    # Cap the velocity to max_speed
    velocity_x = max(-max_speed, min(max_speed, velocity_x))
    velocity_y = max(-max_speed, min(max_speed, velocity_y))

    # Update the character position based on velocity
    move_character()


def move_character():
    global character_x, character_y, velocity_x, velocity_y

    # Update character position based on velocity
    character_x += velocity_x * sensitivity
    character_y += velocity_y * sensitivity

    # Keep the character within screen bounds
    if character_x < 0:
        character_x = 0
        velocity_x = 0  # Stop movement when hitting the boundary
    if character_x > WINDOW_SIZE - character_width:
        character_x = WINDOW_SIZE - character_width
        velocity_x = 0  # Stop movement when hitting the boundary
    if character_y < 0:
        character_y = 0
        velocity_y = 0  # Stop movement when hitting the boundary
    if character_y > WINDOW_SIZE - character_height:
        character_y = WINDOW_SIZE - character_height
        velocity_y = 0  # Stop movement when hitting the boundary


def move_character_up():
    global character_y
    character_y -= scroll_speed * sensitivity  # Move the character up with sensitivity
    if character_y < 0:  # Prevent moving off the screen
        character_y = 0

def move_character_down():
    global character_y
    character_y += scroll_speed * sensitivity  # Move the character down with sensitivity
    if character_y > WINDOW_SIZE - character_height:  # Prevent moving off the screen
        character_y = WINDOW_SIZE - character_height

def move_character_left():
    global character_x
    character_x -= scroll_speed * sensitivity  # Move the character left with sensitivity
    if character_x < 0:  # Prevent moving off the screen
        character_x = 0

def move_character_right():
    global character_x
    character_x += scroll_speed * sensitivity  # Move the character right with sensitivity
    if character_x > WINDOW_SIZE - character_width:  # Prevent moving off the screen
        character_x = WINDOW_SIZE - character_width


def draw_chessboard(offset):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 0:
                color = RED
            else:
                color = PINK
            # Adjust the y position by the offset to create the scrolling effect
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, (row * SQUARE_SIZE) + offset, SQUARE_SIZE, SQUARE_SIZE))


def draw_character():
    screen.blit(character_image, (character_x, character_y))


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    handle_input()  # Handle the up and down movement based on key presses

    # Update the offset for scrolling
    offset_y += scroll_speed

    # Reset offset_y when it goes beyond a full board height to keep the scrolling continuous
    if offset_y >= BOARD_SIZE * SQUARE_SIZE:
        offset_y = 0

    # Draw the chessboard and character
    screen.fill((0, 0, 0))  # Clear the screen
    draw_chessboard(-offset_y)
    draw_chessboard(-offset_y + BOARD_SIZE * SQUARE_SIZE)  # Draw a second board to handle the wrap-around
    draw_character()

    pygame.display.flip()

    pygame.time.delay(30)  # Control the frame rate

pygame.quit()
sys.exit()
