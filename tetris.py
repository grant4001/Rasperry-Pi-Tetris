from sense_hat import SenseHat
import time
import random

# Global variables
hat = SenseHat()
BLANK = (0, 0, 0)
Re = (255, 0, 0)
Gr = (0, 255, 0)
Bl = (0, 0, 255)
Ye = (255, 255, 0)
Or = (255, 165, 0)
Pu = (128, 0, 128)
Gy = (220, 220, 220)
COLORS = [Re, Gr, Bl, Ye, Or, Pu, Gy]
LEDs = [BLANK for q in range(0, 64)]
FIELD = [BLANK for s in range(0, 64)]
PIECES = [
    2, 4, 5, 7, #squiggly
    0, 2, 4, 6, #line piece
    4, 5, 6, 7, #square
    3, 4, 5, 6, #reverse squiggly
    2, 4, 5, 6, #notched
    2, 4, 6, 7, #L piece
    3, 5, 6, 7  #reverse L piece
]

def draw():
    hat.set_pixels(LEDs)

def joystick_handler():
    for event in hat.stick.get_events():
            if event.action == "pressed" or event.action == "held":
                return event.direction
    return 0

def init_tile_points(x_init, y_init, piece_type):
    points = []
    for i in range(0, 4):
        y = y_init + int(PIECES[4*piece_type + i] / 2)
        x = x_init + int(PIECES[4*piece_type + i] % 2)
        points.append((x, y))
    return points

def draw_piece(tile_points, piece_type):
    for i in range(0, 4):
        x_tile, y_tile = tile_points[i]
        if x_tile>=0 and x_tile<=7 and y_tile>=0 and y_tile<=7:
            LEDs[y_tile*8 + x_tile] = COLORS[piece_type]

def draw_field():
    for i in range(0, 64):
        LEDs[i] = FIELD[i]
            
def delete_old_piece(tile_points):
    for i in range(0, 4):
        x_tile, y_tile = tile_points[i]
        if x_tile>=0 and x_tile<=7 and y_tile>=0 and y_tile<=7:
            LEDs[y_tile*8 + x_tile] = BLANK
    
def check_landing(tile_points):
    for i in range(0, 4):
        x_tile, y_tile = tile_points[i]
        if y_tile >= 7:
            return True
        elif y_tile >= -1:
            if FIELD[(y_tile+1)*8 + x_tile] != BLANK:
                return True
    return False

def collision_handler(tile_points, piece_color):
    for i in range(0, 4):
        x_tile, y_tile = tile_points[i]
        if y_tile < 0:
            return True #Game over
        FIELD[y_tile*8 + x_tile] = COLORS[piece_color]
    return False

def score_handler(FIELD):
    add2score = 0
    for a in range(0, 8):
        for b in range(0, 8):
            if FIELD[a*8+b] == BLANK:
                break
            if b == 7:
                del FIELD[a*8:a*8+8]
                FIELD = [BLANK]*8 + FIELD
                add2score += 1000
    return FIELD, add2score
                
def valid_shift(shift, tile_points):
    for i in range(0, 4):
        x_tile, y_tile = tile_points[i]
        if x_tile + shift < 0 or x_tile + shift > 7:
            return False
        if y_tile >= 0:
            if FIELD[y_tile*8 + x_tile + shift] != BLANK:
                return False
    return True

def update_tile_points(tile_points, dx, dy):
    new_points = []
    for i in range(0, 4):
        y_prime = tile_points[i][1] + dy
        x_prime = tile_points[i][0] + dx
        new_points.append((x_prime, y_prime))
    return new_points

def rotate_piece(tile_points):
    
    # Get rotated points
    rotated_points = []
    for i in range(0, 4):
        delta_x = tile_points[i][0] - tile_points[1][0]
        delta_y = tile_points[i][1] - tile_points[1][1]
        new_x = tile_points[1][0] + delta_y
        new_y = tile_points[1][1] - delta_x
        rotated_points.append((new_x, new_y))
        
    # Check that rotated piece is in bounds. 
    xshift = 0
    for j in range(0, 2):
        for k in range(0, 4):
            if rotated_points[k][0] < 0:
                xshift = 1
            elif rotated_points[k][0] > 7:
                xshift = -1
        rotated_points = [(p[0]+xshift, p[1]) for p in rotated_points]
        xshift = 0
    
    # Check if rotated piece collides with field
    collided = True
    loop_count = 0
    while (collided == True):
        collided = False
        for e in range(0, 4):
            if rotated_points[e][1] >= 0 and rotated_points[e][1] <= 7:
                if FIELD[rotated_points[e][1]*8+rotated_points[e][0]] != BLANK:
                    collided = True
                    for f in range(0, 4):
                        if (rotated_points[e][0], rotated_points[e][1] - 1) == rotated_points[f]:
                            rotated_points = [(p[0], p[1] - 1) for p in rotated_points]
                            break
                        elif (rotated_points[e][0] + 1, rotated_points[e][1]) == rotated_points[f]:
                            rotated_points = [(p[0] + 1, p[1]) for p in rotated_points]
                            break
                        elif (rotated_points[e][0] - 1, rotated_points[e][1]) == rotated_points[f]:
                            rotated_points = [(p[0] - 1, p[1]) for p in rotated_points]
                            break
        loop_count += 1
        if loop_count == 6:
            return tile_points
    
    # Finally check again for tiles in bound
    for u in range(0, 4):
        if rotated_points[u][0]<0 or rotated_points[u][0]>7 or rotated_points[u][1]>7:
            return tile_points
        
    # If we get to this point, we passed all checks!
    return rotated_points

def game_over_handler(score):
    time.sleep(0.5)
    while True:
        if joystick_handler() == "middle":
            return
        hat.show_message("Score: ", 0.04)
        if joystick_handler() == "middle":
            return
        hat.show_message(str(score), 0.15, (0, 255, 0))
    time.sleep(0.5)

def pause():
    while True:
        if joystick_handler() == "middle":
            return
    
if __name__ == "__main__":
    score = 0
    dy = 0
    dx = 0
    land_timer = 0.0
    curr_land_time = 0.0
    fall_timer = 0.0
    curr_fall_time = 0.0
    rotate_timer = 0.0
    curr_rotate_time = 0.0
    left_timer = 0.0
    curr_left_time = 0.0
    right_timer = 0.0
    curr_right_time = 0.0
    piece_color = random.randint(0, 6)    
    tile_points = init_tile_points(3, -4, piece_color)
    landed = False
    random.shuffle(COLORS)
    ROTATE_DELAY = 0.1
    SHIFT_DELAY = 0.1
    SHIFT_ANGLE = 10.0
    DOWN_ANGLE = 40.0
    
    # Game loop
    while True:
        
        # Set game level based on score
        if score <= 5000:
            LAND_DELAY = 1.5
            FALL_DELAY = 1.5
        elif score <= 10000:
            LAND_DELAY = 1.25
            FALL_DELAY = 1.25
        elif score <= 15000:
            LAND_DELAY = 1.0
            FALL_DELAY = 1.0
        elif score <= 20000:
            LAND_DELAY = 0.75
            FALL_DELAY = 0.75
        else:
            LAND_DELAY = 0.6
            FALL_DELAY = 0.6
        
        # Check for landing
        if check_landing(tile_points):
            if landed:
                land_timer += time.time() - curr_land_time
            curr_land_time = time.time()
            landed = True
            
            # If landed, drop a new piece and RESET
            if land_timer > LAND_DELAY:
                land_timer = 0.0
                
                # Check for game over
                if collision_handler(tile_points, piece_color):
                    game_over_handler(score)
                    FIELD = [BLANK]*64
                    score = 0
                else:
                    FIELD, score_increase = score_handler(FIELD)
                    score += score_increase
                piece_color = random.randint(0, 6)
                tile_points = init_tile_points(3, -4, piece_color)
                landed = False
        else:
            land_timer = 0.0
            landed = False
        
        # Update dy if we reach a game tick
        dy = 0
        fall_timer += time.time() - curr_fall_time
        curr_fall_time = time.time()
        if fall_timer > FALL_DELAY:
            fall_timer = 0.0
            if not landed:
                dy = 1
        
        # Check if joystick is pressed/held
        direction = joystick_handler()
        if ((hat.orientation["pitch"] >= SHIFT_ANGLE and hat.orientation["pitch"] <= 180.0) or direction == "left") and valid_shift(-1, tile_points):
            left_timer += time.time() - curr_left_time
            curr_left_time = time.time()
            if left_timer > SHIFT_DELAY:
                left_timer = 0.0
                dx = -1
        elif ((hat.orientation["pitch"] <= 360.0 - SHIFT_ANGLE and hat.orientation["pitch"] > 180.0) or direction == "right") and valid_shift(1, tile_points):
            right_timer += time.time() - curr_right_time
            curr_right_time = time.time()
            if right_timer > SHIFT_DELAY:
                right_timer = 0.0
                dx = 1
        elif direction == "middle":
            rotate_timer += time.time() - curr_rotate_time
            curr_rotate_time = time.time()
            if rotate_timer > ROTATE_DELAY:
                rotate_timer = 0.0
                dy = 0
                tile_points = rotate_piece(tile_points)
        elif ((hat.orientation["roll"] > DOWN_ANGLE and hat.orientation["roll"] < 180.0) or direction == "down") and (not landed):
            dy = 1
        #elif direction == "middle":
        #    pause()
            
        # Update tile points
        tile_points = update_tile_points(tile_points, dx, dy)
        
        # Reset dx and dy
        dx = 0
        dy = 0
        
        # Draw field
        draw_field()
        
        # Draw piece
        draw_piece(tile_points, piece_color)
        
        # Draw
        draw()
        
        # Delete old piece
        delete_old_piece(tile_points)