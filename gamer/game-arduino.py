import pygame
import sys
import serial
import threading
import random
import time


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
pygame.display.set_caption('Scrolling Chessboard with Joystick Control')

# Load and resize the character image
character_width, character_height = 200, 200
character_image = pygame.image.load('50.png')

# Load images of various game objects
bullet_image = pygame.image.load('bullet.png')
bullet_image = pygame.transform.flip(bullet_image, False, True)  # Reflect on x-axis
money_image = pygame.image.load('money.png')
money_width, money_height = (money_image.get_width() // 5, money_image.get_height() // 5)
bank_image = pygame.image.load('bank.png')
background_image = pygame.image.load('background.jpg')

# Optionally scale the background image to fit the window's width (adjust the scale factor as needed)
num_tiles = 2

# Calculate the tile height to fit the screen with the desired number of tiles
tile_height = WINDOW_SIZE // num_tiles
tile_width = WINDOW_SIZE  # Full width of the window

background_image = pygame.transform.scale(background_image, (tile_width, tile_height))

# Scale the bank image to 1/16th the size of the board
bank_size = WINDOW_SIZE // 8
bank_image = pygame.transform.scale(bank_image, (bank_size, bank_size))

# Position the bank image at the top right
bank_x = WINDOW_SIZE - bank_size - 50  # 10 pixels from the right edge
bank_y = 10  # 10 pixels from the top edge

# Bullet properties
bullet_width, bullet_height = bullet_image.get_width() // 5, bullet_image.get_height() // 5
bullet_speed = 5  # Adjustable speed for bullet movement
max_bullets = 5  # Maximum number of bullets on the screen

# Initialize a list to hold bullet positions and a timer for bullet spawning
bullets = []
last_bullet_time = time.time()  # Initialize the last bullet time
bullet_interval_min = 0.5  # Minimum time between bullets (in seconds)
bullet_interval_max = 2.0  # Maximum time between bullets (in seconds)
next_bullet_interval = random.uniform(bullet_interval_min, bullet_interval_max)

# Money properties
money_x = random.randint(0, WINDOW_SIZE - money_width)
money_y = random.randint(0, WINDOW_SIZE - money_height)

# Initialize the money respawn timer
money_visible = True
money_disappear_time = None
respawn_delay = None
respawn_delay = random.uniform(0.5, 1.5)  # Random delay between 0.5 and 1.5 seconds

# Scale the bullet image to be 5 times smaller
character_image = pygame.transform.scale(character_image, (character_width, character_height))
bullet_image = pygame.transform.scale(bullet_image, (bullet_width, bullet_height))
money_image = pygame.transform.scale(money_image, (money_width, money_height))

# Initial character position
character_x = WINDOW_SIZE // 2 - character_width // 2
character_y = WINDOW_SIZE - character_height - 10  # Placed at the bottom of the screen

# Scrolling parameters
scroll_speed = 2
offset_y = 0

# Movement parameters
sensitivity = 2  # Base speed
acceleration = 0.5  # How quickly the character accelerates
max_speed = 10  # Maximum speed the character can reach
drift = 0.90  # How quickly the character slows down after releasing the key

# Initial velocities
velocity_x = 0
velocity_y = 0

# Initialize serial connection
ser = serial.Serial('COM3', 9600, timeout=1)  # Replace 'COM3' with your Arduino's serial port

# Global variables to store joystick values
joystick_x = 503
joystick_y = 499

score = 0

collection_message = ""
message_visible = False
message_disappear_time = None
message_duration = 1.0  # Duration the message stays visible in seconds


# Function to draw the tiled background with a y offset
def draw_tiled_background(offset_y):
    # Draw the first tile
    screen.blit(background_image, (0, offset_y))
    # Draw the second tile below the first
    screen.blit(background_image, (0, offset_y + tile_height))

    # Draw the third tile above the first if the first tile is starting to move off the screen
    if offset_y > 0:
        screen.blit(background_image, (0, offset_y - tile_height))

def update_score():
    global score, collection_message, message_visible, message_disappear_time
    score_increase = random.choice([5, 20, 100])
    score += score_increase
    collection_message = f"+${score_increase}!"
    message_visible = True
    message_disappear_time = time.time()
    print(f"Score increased by {score_increase}. Total score: {score}")


def draw_collection_message():
    if message_visible:
        font = pygame.font.Font(None, 36)  # Use the default font, size 36
        message_text = font.render(collection_message, True, (255, 255, 0))
        screen.blit(message_text, (money_x, money_y - 40))  # Display above the money


def draw_score():
    font = pygame.font.Font(None, 36)  # Use the default font, size 36
    score_text = font.render(f"Score: ${score}", True, (255, 255, 255))
    score_x = bank_x + (bank_size - score_text.get_width()) // 2  # Centered under the bank image
    score_y = bank_y + bank_size + 5  # Slightly below the bank image
    screen.blit(score_text, (score_x, score_y))


def read_serial():
    global joystick_x, joystick_y
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            try:
                parts = line.split(',')
                x_part = parts[0].split(':')[1]
                y_part = parts[1].split(':')[1]
                joystick_x = int(x_part)
                joystick_y = int(y_part)
            except (IndexError, ValueError):
                pass  # Handle parsing errors if necessary


# Start the serial reading thread
serial_thread = threading.Thread(target=read_serial, daemon=True)
serial_thread.start()


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


def handle_joystick_input():
    global velocity_x, velocity_y

    # Define dead zone to prevent drift when joystick is near the center
    dead_zone = 100  # Adjust as needed

    # Invert the joystick_x value to correct the direction
    inverted_x = 1023 - joystick_x

    # Invert the joystick_y value to correct the direction
    inverted_y = 1023 - joystick_y

    # Map joystick X
    if inverted_x < (512 - dead_zone):
        velocity_x -= acceleration
    elif inverted_x > (512 + dead_zone):
        velocity_x += acceleration
    else:
        velocity_x *= drift  # Apply drift when in dead zone

    # Map joystick Y
    if inverted_y < (512 - dead_zone):
        velocity_y -= acceleration
    elif inverted_y > (512 + dead_zone):
        velocity_y += acceleration
    else:
        velocity_y *= drift  # Apply drift when in dead zone

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


def reset_bullet():
    global bullet_x, bullet_y
    bullet_x = random.randint(0, WINDOW_SIZE - bullet_width)
    bullet_y = 0


def move_bullets():
    global bullets, last_bullet_time, next_bullet_interval

    # Move each bullet downward
    for bullet in bullets:
        bullet[1] += bullet_speed

    # Remove bullets that have gone off the screen
    bullets = [bullet for bullet in bullets if bullet[1] <= WINDOW_SIZE]

    # Check if it's time to spawn a new bullet
    current_time = time.time()
    if len(bullets) < max_bullets and current_time - last_bullet_time > next_bullet_interval:
        spawn_bullet()
        last_bullet_time = current_time
        next_bullet_interval = random.uniform(bullet_interval_min, bullet_interval_max)

    # Draw each bullet on the screen
    for bullet in bullets:
        screen.blit(bullet_image, (bullet[0], bullet[1]))


def spawn_bullet():
    bullet_x = random.randint(0, WINDOW_SIZE - bullet_width)
    bullet_y = 0
    bullets.append([bullet_x, bullet_y])


def spawn_money():
    global money_x, money_y
    money_x = random.randint(0, WINDOW_SIZE - money_width)
    money_y = random.randint(0, WINDOW_SIZE - money_height)


def draw_money():
    screen.blit(money_image, (money_x, money_y))


def check_collision():
    character_rect = pygame.Rect(character_x, character_y, character_width, character_height)
    money_rect = pygame.Rect(money_x, money_y, money_width, money_height)
    return character_rect.colliderect(money_rect)


def draw_debug_bounding_boxes():
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(character_x, character_y, character_width, character_height), 2)
    pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(money_x, money_y, money_width, money_height), 2)


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    handle_joystick_input()  # Handle movement based on joystick input

    # Update the offset for scrolling
    offset_y += scroll_speed

    # Reset offset_y when it goes beyond a full board height to keep the scrolling continuous
    if offset_y >= tile_height:
        offset_y = 0

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw the tiled background
    draw_tiled_background(offset_y)

    # Draw the character
    draw_character()

    # Move and draw the bullets
    move_bullets()

    # Check for collision and handle money disappearance
    if money_visible and check_collision():
        update_score()  # Update the score and set the collection message
        money_visible = False
        money_disappear_time = time.time()
        respawn_delay = random.uniform(0.5, 1.5)  # Random delay between 0.5 and 1.5 seconds

    # Handle the money respawn
    if not money_visible and money_disappear_time:
        if time.time() - money_disappear_time > respawn_delay:
            spawn_money()
            money_visible = True
            money_disappear_time = None

    # Draw the money if visible
    if money_visible:
        draw_money()

    # Draw the collection message if visible
    if message_visible:
        draw_collection_message()
        # Check if the message duration has passed
        if time.time() - message_disappear_time > message_duration:
            message_visible = False

    # Draw the bank image
    screen.blit(bank_image, (bank_x, bank_y))

    # Draw the score
    draw_score()

    pygame.display.flip()

    pygame.time.delay(30)  # Control the frame rate

pygame.quit()
sys.exit()

