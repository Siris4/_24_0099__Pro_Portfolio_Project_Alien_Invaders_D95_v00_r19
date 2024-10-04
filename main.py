import tkinter as tk
from PIL import Image, ImageTk
import random
import os

# Set up the main window
root = tk.Tk()
root.title("Space Invaders")
root.resizable(False, False)
root.geometry("800x600")

# Create the canvas for the game
canvas = tk.Canvas(root, width=800, height=600, bg="black")
canvas.pack()

# File to store the high score
high_score_file = "highscore.txt"


# Function to load high score from file
def load_high_score():
    if os.path.exists(high_score_file):
        with open(high_score_file, "r") as f:
            return int(f.read().strip())
    return 0


# Function to save high score to file
def save_high_score(new_high_score):
    with open(high_score_file, "w") as f:
        f.write(str(new_high_score))


# Load the high score from the file
high_score = load_high_score()

# Score, high score, and lives variables
score = 0
lives = 3

# Spaceship properties
spaceship_x = 380  # starting x position of the spaceship
spaceship_y = 550  # fixed y position (near the bottom of the window)
spaceship_speed = 5  # Adjusted to move at a smaller step for smoothness
spaceship_move_direction = 0  # 0 = not moving, -1 = left, 1 = right

# Create the spaceship using the image
spaceship_image = Image.open(
    r"C:\Users\Siris\Desktop\GitHub Projects 100 Days NewB\_24_0099__Day95_Pro_Portfolio_Project_Alien_Invaders__241001\NewProject\r00_env_START\r13\spaceship.png")
spaceship_image = spaceship_image.resize((40, 40), Image.Resampling.LANCZOS)  # Resize image to fit
spaceship_photo = ImageTk.PhotoImage(spaceship_image)
spaceship = canvas.create_image(spaceship_x, spaceship_y, image=spaceship_photo, anchor="nw")

# Load the splat image for alien explosion
splat_image = Image.open(
    r"C:\Users\Siris\Desktop\GitHub Projects 100 Days NewB\_24_0099__Day95_Pro_Portfolio_Project_Alien_Invaders__241001\NewProject\r00_env_START\r13\splat_only.png")
splat_image = splat_image.resize((40, 40), Image.Resampling.LANCZOS)  # Resize to match alien size
splat_photo = ImageTk.PhotoImage(splat_image)

# Variable to keep track of the active bullet
active_bullet = None

# List to keep track of barriers and their pixel positions
barriers = []

# List to keep track of aliens and their pixel positions
aliens = []

# Alien movement properties
alien_move_direction = 1  # 1 for right, -1 for left
alien_speed = 10  # Number of pixels to move horizontally each time
alien_move_down = 1  # Pixels to move down when reaching the screen edge
alien_move_interval = 500  # Time between each movement in milliseconds

# Bomb properties
active_bombs = []  # Store all active bombs
max_bombs = 8  # Maximum number of bombs at one time

# Flag to check if a side has been hit to prevent zig-zagging
edge_hit = False  # Initialize edge_hit

# Display score, high score, and lives
score_label = canvas.create_text(50, 20, text=f"Score: {score}", fill="white", font=("Retro Gaming", 16))
high_score_label = canvas.create_text(750, 20, text=f"High Score: {high_score}", fill="white",
                                      font=("Retro Gaming", 16))
lives_label = canvas.create_text(400, 20, text=f"Lives: {lives}", fill="white", font=("Retro Gaming", 16))


# Function to update score, high score, and lives on the screen
def update_labels():
    global score, high_score, lives
    canvas.itemconfig(score_label, text=f"Score: {score}")
    canvas.itemconfig(high_score_label, text=f"High Score: {high_score}")
    canvas.itemconfig(lives_label, text=f"Lives: {lives}")


# Function to end the game
def game_over():
    canvas.create_text(400, 300, text="Game Over", fill="red", font=("Retro Gaming", 32))


# Function to drop alien bombs
def drop_alien_bombs():
    if len(active_bombs) < max_bombs:
        # Randomly select a column for dropping bombs
        columns_with_aliens = {}
        for alien in aliens:
            alien_x = min([canvas.coords(pixel)[0] for pixel in alien[2]])  # Current x of alien
            if alien_x not in columns_with_aliens or columns_with_aliens[alien_x][1] < alien[1]:
                columns_with_aliens[alien_x] = alien

        if columns_with_aliens:
            selected_column = random.choice(list(columns_with_aliens.values()))
            alien_x = min([canvas.coords(pixel)[0] for pixel in selected_column[2]])
            alien_y = max([canvas.coords(pixel)[1] for pixel in selected_column[2]])

            # Create the bomb just below the selected alien
            bomb = canvas.create_rectangle(alien_x + 20 - 2, alien_y + 5, alien_x + 20 + 2, alien_y + 15,
                                           fill="red")  # Longer alien bomb
            active_bombs.append(bomb)
            move_bomb(bomb)

    root.after(1000, drop_alien_bombs)  # Continue dropping bombs at random intervals


# Function to move the bomb
def move_bomb(bomb):
    bomb_coords = canvas.coords(bomb)
    if bomb_coords[1] >= 600:  # If bomb goes out of bounds
        canvas.delete(bomb)
        active_bombs.remove(bomb)
    else:
        canvas.move(bomb, 0, 5)  # Move bomb down by 5 pixels
        check_bomb_collision(bomb)  # Check if bomb hits something
        root.after(50, lambda: move_bomb(bomb))


# Function to check if a bomb hits a barrier, the spaceship, or a bullet
def check_bomb_collision(bomb):
    global active_bullet, lives

    bomb_coords = canvas.coords(bomb)
    bomb_x = bomb_coords[0] + 2
    bomb_y = bomb_coords[1]

    # Check each barrier (top-down collision)
    for barrier_item in barriers:
        pixel_x, pixel_y, pixel_rectangle = barrier_item
        if pixel_x <= bomb_x <= pixel_x + 5 and pixel_y <= bomb_y <= pixel_y + 5:
            # Delete the pixel from the canvas
            canvas.delete(pixel_rectangle)
            barriers.remove(barrier_item)  # Remove the pixel from the barriers list
            canvas.delete(bomb)  # Remove the bomb
            active_bombs.remove(bomb)  # Remove from active bombs list
            return

    # Check if the bomb hits the spaceship
    spaceship_coords = canvas.coords(spaceship)
    spaceship_x1, spaceship_y1, spaceship_x2, spaceship_y2 = spaceship_coords[0], spaceship_coords[1], spaceship_coords[
                                                                                                           0] + 40, \
                                                                                                       spaceship_coords[
                                                                                                           1] + 40
    if spaceship_x1 <= bomb_x <= spaceship_x2 and spaceship_y1 <= bomb_y <= spaceship_y2:
        # Bomb hits the spaceship, lose one life
        lives -= 1
        update_labels()  # Update lives
        canvas.delete(bomb)
        active_bombs.remove(bomb)

        # Show the splat image over the spaceship
        splat = canvas.create_image(spaceship_coords[0], spaceship_coords[1], image=splat_photo, anchor="nw")
        root.after(1000, canvas.delete, splat)

        # End game if no lives are left
        if lives == 0:
            game_over()
        return

    # Check if a bomb collides with a bullet (cancel out both)
    if active_bullet is not None:
        bullet_coords = canvas.coords(active_bullet)
        bullet_x = bullet_coords[0] + 2
        bullet_y = bullet_coords[1]

        if bullet_x == bomb_x and bullet_y <= bomb_y:  # Bomb and bullet collide
            # Cancel both projectiles
            canvas.delete(bomb)
            active_bombs.remove(bomb)
            canvas.delete(active_bullet)
            active_bullet = None
            return


# Function to move the spaceship left or right
def move_spaceship():
    x1, y1 = canvas.coords(spaceship)
    # Update spaceship's position based on the direction
    if spaceship_move_direction == -1 and x1 > 0:  # Move left
        canvas.move(spaceship, -spaceship_speed, 0)
    elif spaceship_move_direction == 1 and x1 < 760:  # Move right
        canvas.move(spaceship, spaceship_speed, 0)

    # Continuously call this function to create smooth movement
    root.after(20, move_spaceship)


# Function to start moving left
def start_move_left(event):
    global spaceship_move_direction
    spaceship_move_direction = -1


# Function to start moving right
def start_move_right(event):
    global spaceship_move_direction
    spaceship_move_direction = 1


# Function to stop moving
def stop_move(event):
    global spaceship_move_direction
    spaceship_move_direction = 0


# Function to fire a bullet (white pebble)
def fire_bullet(event):
    global active_bullet
    # If there's already an active bullet, do nothing
    if active_bullet is not None:
        return

    # Create a new bullet
    x1, y1 = canvas.coords(spaceship)
    bullet = canvas.create_rectangle(x1 + 20 - 2, y1 - 10, x1 + 20 + 2, y1, fill="white")  # Short white bullet
    active_bullet = bullet
    move_bullet()


# Function to check if a bullet hits an alien or barrier
def check_collision():
    global active_bullet, score, high_score

    if active_bullet is None:
        return

    bullet_coords = canvas.coords(active_bullet)
    bullet_x = bullet_coords[0] + 2  # Center of the bullet
    bullet_y = bullet_coords[1]

    # Check each alien for collision (updated to check current alien position)
    for alien in aliens:
        alien_x = min([canvas.coords(pixel)[0] for pixel in alien[2]])  # Current leftmost pixel of alien
        alien_y = min([canvas.coords(pixel)[1] for pixel in alien[2]])  # Current top pixel of alien

        if alien_x <= bullet_x <= alien_x + 40 and alien_y <= bullet_y <= alien_y + 40:
            # Remove all pixels of the alien
            for pixel_rectangle in alien[2]:
                canvas.delete(pixel_rectangle)
            aliens.remove(alien)  # Remove alien from the list

            # Replace the alien with the splat image for 1 second
            splat = canvas.create_image(alien_x, alien_y, image=splat_photo, anchor="nw")
            root.after(1000, canvas.delete, splat)

            # Remove the bullet after collision
            canvas.delete(active_bullet)
            active_bullet = None

            # Increase score and update high score if necessary
            score += 100
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            update_labels()
            return

    # Check each barrier (each pixel block)
    for barrier_item in barriers:
        pixel_x, pixel_y, pixel_rectangle = barrier_item
        if pixel_x <= bullet_x <= pixel_x + 5 and pixel_y <= bullet_y <= pixel_y + 5:
            # Delete the pixel from the canvas
            canvas.delete(pixel_rectangle)
            barriers.remove(barrier_item)  # Remove the pixel from the barriers list

            # Remove the bullet after collision
            canvas.delete(active_bullet)
            active_bullet = None
            return


# Function to move the active bullet
def move_bullet():
    global active_bullet
    if active_bullet is not None:
        # Check if the active_bullet still exists before getting its coordinates
        try:
            bullet_coords = canvas.coords(active_bullet)
        except tk.TclError:
            return  # The bullet has been deleted, so we stop here

        canvas.move(active_bullet, 0, -10)
        check_collision()  # Check for collision with barriers or aliens

        # If the bullet goes off-screen, remove it
        if bullet_coords[1] < 0:
            canvas.delete(active_bullet)
            active_bullet = None  # Reset the active bullet variable

    # Continue moving the bullet until it goes off-screen or is deleted
    if active_bullet is not None:
        root.after(50, move_bullet)


# Function to create barriers manually (pixel blocks)
def create_barriers():
    barrier_y = spaceship_y - 150  # 150 pixels above the spaceship
    barrier_spacing = 160  # Evenly space the barriers horizontally
    pixel_size = 5  # Each pixel block will be 5x5 on the canvas

    # Shape of the barrier represented as a grid (1 = solid, 0 = empty)
    barrier_shape = [
        [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
    ]

    for i in range(4):  # Create four barriers
        barrier_x = 130 + i * barrier_spacing  # Shifted 20 pixels to the left from previous position

        # Create the barrier block by block using the shape
        for row in range(len(barrier_shape)):
            for col in range(len(barrier_shape[0])):
                if barrier_shape[row][col] == 1:
                    pixel_rectangle = canvas.create_rectangle(
                        barrier_x + col * pixel_size, barrier_y + row * pixel_size,
                        barrier_x + (col + 1) * pixel_size, barrier_y + (row + 1) * pixel_size,
                        fill="green", outline=""
                    )
                    barriers.append([barrier_x + col * pixel_size, barrier_y + row * pixel_size, pixel_rectangle])


# Function to create aliens (both alien1 and alien2)
def create_aliens():
    alien_spacing = 80  # Horizontal spacing between aliens
    pixel_size = 5  # Each pixel block will be 5x5 on the canvas

    # Shape of alien1 (grid of 1's and 0's)
    alien1_shape = [
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 1, 1, 0, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 0, 1, 1, 0, 1, 0],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [0, 1, 0, 0, 0, 0, 1, 0],
    ]

    # Adjusted Shape of alien2 to be an 8x8 grid, matching the size and spacing of alien1
    alien2_shape = [
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 1, 1, 1, 1, 0, 1],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [1, 0, 1, 1, 1, 1, 0, 1],
        [0, 1, 0, 1, 1, 0, 1, 0],
        [1, 0, 0, 0, 0, 0, 0, 1],
    ]

    # Create two rows of alien1
    for row_num in range(2):  # Two rows of alien1
        alien_y = 50 + row_num * 50  # Spaced vertically (adjusted from 100 to 50 for 100px from the top)
        for i in range(8):  # Create 8 aliens per row
            alien_x = 50 + i * alien_spacing
            alien_pixels = []
            for row in range(len(alien1_shape)):
                for col in range(len(alien1_shape[0])):
                    if alien1_shape[row][col] == 1:
                        pixel_rectangle = canvas.create_rectangle(
                            alien_x + col * pixel_size, alien_y + row * pixel_size,
                            alien_x + (col + 1) * pixel_size, alien_y + (row + 1) * pixel_size,
                            fill="green", outline=""
                        )
                        alien_pixels.append(pixel_rectangle)
            aliens.append([alien_x, alien_y, alien_pixels])

    # Create one row of alien2 below alien1 rows
    alien_y = 150  # Position for the alien2 row (adjusted from 200 to fit spacing)
    for i in range(8):  # Create 8 aliens for alien2
        alien_x = 50 + i * alien_spacing
        alien_pixels = []
        for row in range(len(alien2_shape)):
            for col in range(len(alien2_shape[0])):
                if alien2_shape[row][col] == 1:
                    pixel_rectangle = canvas.create_rectangle(
                        alien_x + col * pixel_size, alien_y + row * pixel_size,
                        alien_x + (col + 1) * pixel_size, alien_y + (row + 1) * pixel_size,
                        fill="green", outline=""
                    )
                    alien_pixels.append(pixel_rectangle)
        aliens.append([alien_x, alien_y, alien_pixels])


# Function to move aliens left and right, then down by 1 pixel
def move_aliens():
    global alien_move_direction, edge_hit

    # Get the leftmost and rightmost positions of aliens
    leftmost_x = min([min([canvas.coords(pixel)[0] for pixel in alien[2]]) for alien in aliens])
    rightmost_x = max([max([canvas.coords(pixel)[0] for pixel in alien[2]]) for alien in aliens])

    # Move aliens horizontally by the alien speed
    for alien in aliens:
        for pixel_rectangle in alien[2]:
            canvas.move(pixel_rectangle, alien_speed * alien_move_direction, 0)

    # Check if aliens hit the left or right edge of the screen
    if not edge_hit and (leftmost_x <= 0 or rightmost_x >= 800):
        alien_move_direction *= -1  # Reverse direction
        edge_hit = True  # Mark that the edge has been hit
        # Move aliens down by 1 pixel (this is now 1)
        for alien in aliens:
            for pixel_rectangle in alien[2]:
                canvas.move(pixel_rectangle, 0, alien_move_down)

    # Reset the flag when the aliens have moved away from the edge
    if edge_hit and 0 < leftmost_x < 800 and 0 < rightmost_x < 800:
        edge_hit = False

    root.after(alien_move_interval, move_aliens)  # Continue the movement loop


# Function to create and move stars
active_stars = []  # Store active stars
max_stars = 3


def create_stars():
    if len(active_stars) < max_stars:
        # Create a random star at the top
        star_x = random.randint(0, 800)
        star = canvas.create_oval(star_x, 0, star_x + 5, 5, fill="yellow", outline="")
        active_stars.append(star)
        move_star(star)

    # Continue creating stars
    root.after(1000, create_stars)


def move_star(star):
    star_coords = canvas.coords(star)
    if star_coords[1] >= 600:  # Star goes off-screen
        canvas.delete(star)
        active_stars.remove(star)
    else:
        canvas.move(star, 0, 5)  # Move star down by 5 pixels
        root.after(50, lambda: move_star(star))


# Create barriers and the aliens on the screen
create_barriers()
create_aliens()

# Start the alien movement
move_aliens()

# Start the floating star animation
create_stars()

# Bind key events to spaceship movement and firing
root.bind("<Left>", start_move_left)
root.bind("<Right>", start_move_right)
root.bind("<KeyRelease-Left>", stop_move)
root.bind("<KeyRelease-Right>", stop_move)
root.bind("<space>", fire_bullet)

# Start alien bomb dropping mechanism
drop_alien_bombs()

# Start smooth movement and the game loop
move_spaceship()

root.mainloop()
