import pygame
import sys

pygame.init()

WINDOW_SIZE = 800  # Example window size
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))

# Load the background image
background_image = pygame.image.load('background.jpg')

# Calculate the tile size to fit 2 tiles exactly on the screen
tile_height = WINDOW_SIZE // 2  # Half of the window height
tile_width = WINDOW_SIZE  # Full width of the window

# Scale the background image to the calculated size
background_image = pygame.transform.scale(background_image, (tile_width, tile_height))


# Function to draw the tiled background with a y offset
def draw_tiled_background(offset_y):
    # Draw the first tile
    screen.blit(background_image, (0, offset_y))
    # Draw the second tile below the first
    screen.blit(background_image, (0, offset_y + tile_height))

    # Draw the third tile above the first if the first tile is starting to move off the screen
    if offset_y > 0:
        screen.blit(background_image, (0, offset_y - tile_height))


# Initialize scrolling variables
offset_y = 0
scroll_speed = 2  # Adjust this for faster or slower scrolling

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the offset for scrolling (move downwards)
    offset_y += scroll_speed
    if offset_y >= tile_height:
        offset_y = 0

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw the tiled background with the y offset
    draw_tiled_background(offset_y)

    pygame.display.flip()

    pygame.time.delay(30)  # Adjust this for smoother or faster updates

pygame.quit()
sys.exit()
