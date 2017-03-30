# -*- coding: utf-8 -*-

import random
import math
import numpy as np

import pygame
from pygame.color import THECOLORS

import pymunk
from pymunk.vec2d import Vec2d
from pymunk.pygame_util import draw

# PyGame init
width = 1000
height = 700
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Turn off alpha since we don't use it.
screen.set_alpha(None)

# Showing sensors and redrawing slows things down.
show_sensors = True
draw_screen = True


class GameState:
    def __init__(self):
        # Global-ish.
        self.crashed = 0
        self.caught = 0
        # Physics stuff.
        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0., 0.)

        # Create the car.
        self.create_car(100, 100, 0.5)

        # Record steps.
        self.num_steps = 0

        # Create walls.
        static = [
            pymunk.Segment(
                self.space.static_body,
                (0, 2), (0, height), 2),
            pymunk.Segment(
                self.space.static_body,
                (2, height), (width, height), 2),
            pymunk.Segment(
                self.space.static_body,
                (width-2, height), (width-2, 2), 2),
            pymunk.Segment(
                self.space.static_body,
                (2, 2), (width, 2), 2)
        ]
        for s in static:
            s.friction = 1.
            s.group = 1
            s.collision_type = 1
            s.elasticity = 5
            s.color = THECOLORS['red']
        self.space.add(static)

        # Create some obstacles, semi-randomly.
        # We'll create three and they'll move around to prevent over-fitting.

        # self.obstacles = []
        # self.obstacles.append(self.create_obstacle(200, 350, 70))
        # self.obstacles.append(self.create_obstacle(700, 200, 80))
        # self.obstacles.append(self.create_obstacle(600, 600, 70))

        # Create a cat.
        self.create_cat()
        # self.create_dog()

    def create_obstacle(self, x, y, r):
        c_body = pymunk.Body(pymunk.inf, pymunk.inf)
        c_shape = pymunk.Circle(c_body, r)
        c_shape.elasticity = 1.0
        c_body.position = x, y
        c_shape.color = THECOLORS["blue"]
        self.space.add(c_body, c_shape)
        return c_body

    # def create_cat(self):
    #     inertia = pymunk.moment_for_circle(1, 0, 14, (0, 0))
    #     self.cat_body = pymunk.Body(1, inertia)
    #     self.cat_body.position = 50, height - 100
    #     self.cat_shape = pymunk.Circle(self.cat_body, 35)
    #     self.cat_shape.color = THECOLORS["orange"]
    #     self.cat_shape.elasticity = 1.0
    #     self.cat_shape.angle = 0.5
    #     direction = Vec2d(1, 0).rotated(self.cat_body.angle)
    #     self.space.add(self.cat_body, self.cat_shape)

    # def create_dog(self):
    #     inertia = pymunk.moment_for_circle(1, 0, 14, (0, 0))
    #     self.dog_body = pymunk.Body(1, inertia)
    #     self.dog_body.position = 900, height - 600
    #     self.dog_shape = pymunk.Circle(self.dog_body, 40)
    #     self.dog_shape.color = THECOLORS["yellow"]
    #     self.dog_shape.elasticity = 2.0
    #     self.dog_shape.angle = 0.5
    #     direction = Vec2d(1, 0).rotated(self.dog_body.angle)
    #     self.space.add(self.dog_body, self.dog_shape)

    def create_cat(self):
        inertia = pymunk.moment_for_circle(1, 0, 14, (0, 0))
        self.cat_body = pymunk.Body(1, inertia)
        self.cat_body.position = 50, height - 100
        self.cat_shape = pymunk.Circle(self.cat_body, 25)
        self.cat_shape.color = THECOLORS["orange"]
        self.cat_shape.elasticity = 2.0
        self.cat_shape.angle = 0.5
        moving_direction = Vec2d(1, 0).rotated(self.cat_body.angle)
        self.cat_body.apply_impulse(moving_direction)
        self.space.add(self.cat_body, self.cat_shape)

    def create_car(self, x, y, r):
        inertia = pymunk.moment_for_circle(1, 0, 14, (0, 0))
        self.car_body = pymunk.Body(1, inertia)
        self.car_body.position = x, y
        self.car_shape = pymunk.Circle(self.car_body, 25)
        self.car_shape.color = THECOLORS["green"]
        self.car_shape.elasticity = 2.0
        self.car_body.angle = r
        driving_direction = Vec2d(1, 0).rotated(self.car_body.angle)
        self.car_body.apply_impulse(driving_direction)
        self.space.add(self.car_body, self.car_shape)

    def frame_step(self, action, action2):
        if action == 0:  # Turn left.
            self.car_body.angle -= .2
        elif action == 1:  # Turn right.
            self.car_body.angle += .2

        elif action2 == 0:  # Turn right.
            self.cat_body.angle += .2  

        elif action2 == 1:  # Turn right.
            self.cat_body.angle += .2

        # Move obstacles.
        # if self.num_steps % 50 == 0:
        #     self.move_obstacles()

        # Move cat.
        # if self.num_steps % 5 == 0:
        #     self.move_cat()

        # if self.num_steps % 5 == 0:
        #     self.move_dog()

        driving_direction = Vec2d(1, 0).rotated(self.car_body.angle)
        self.car_body.velocity = 30 * driving_direction

        moving_direction = Vec2d(1, 0).rotated(self.cat_body.angle)
        self.cat_body.velocity = 30 * moving_direction

        # Update the screen and stuff.
        screen.fill(THECOLORS["black"])
        draw(screen, self.space)
        self.space.step(1./10)  #original 1./10
        if draw_screen:
            pygame.display.flip()
        clock.tick()

        # Get the current location and the readings there.
        x, y = self.car_body.position
        x_cat, y_cat = self.cat_body.position

        # if ball out of screen, seng them back
        if x_cat < 1 or x_cat > 1000 or y_cat <1 or y_cat > 700:
            self.cat_body.position = random.randint(100,900), random.randint(100,600)    
            x_cat, y_cat = self.car_body.position

        readings = self.get_sonar_readings(x, y, self.car_body.angle)
        readings2 = self.get_sonar_readings(x_cat, y_cat, self.cat_body.angle)
        # readings.append([x,y])
        # readings.append([x_cat,y_cat])

        state = np.array([readings])
        state2 = np.array([readings2])
        
        print readings, readings2

        # Set the reward.
        # Car crashed when any reading == 1

        if self.car_is_crashed(readings):
            self.crashed = 1
            reward = -10
            self.recover_from_crash(driving_direction)

        # if self.car_is_crashed(readings2):
        #     self.crashed = 1
        #     reward2 = -10
        #     self.recover_from_crash(moving_direction)

        # elif self.cat_is_caught(readings):
        #     self.caught = 1
        #     reward = 500
        #     self.recover_from_caught(driving_direction)

        if self.cat_is_caught(readings, readings2):
            self.caught = 1
            reward = 500
            reward2 = -500
            self.recover_from_caught(moving_direction)

        if readings[0][1] == -5 or readings[1][1] == -5 or readings[2][1] == -5:
            
            reward = 100 - int(self.sum_readings(readings) / 10)

        else: reward = -12 + int(self.sum_readings(readings) / 10)


        if readings2[0][1] == -5 or readings2[1][1] == -5 or readings2[2][1] == -5:

            reward2 = -100 + int(self.sum_readings(readings2) / 10)
        
        else: reward2 = -12 + int(self.sum_readings(readings) / 10)
        
         # else:
         #    # Higher readings are better, so return the sum.
         #    reward = -12 + int(self.sum_readings(readings) / 10)

        print("current reward: %s, %s" % (reward, reward2)) 

        self.num_steps += 1

        return reward, reward2, state, state2

    # def move_obstacles(self):
    #     # Randomly move obstacles around.
    #     for obstacle in self.obstacles:
    #         speed = random.randint(1, 5)
    #         direction = Vec2d(1, 0).rotated(self.car_body.angle + random.randint(-2, 2))
    #         obstacle.velocity = speed * direction

    # def move_cat(self):
    #     speed = random.randint(50, 100)
    #     self.cat_body.angle -= random.randint(-1, 1)
    #     direction = Vec2d(1, 0).rotated(self.cat_body.angle)
    #     self.cat_body.velocity = speed * direction

    # def move_dog(self):
    #     speed = random.randint(40, 60)
    #     self.dog_body.angle -= random.randint(-1, 1)
    #     direction = Vec2d(1, 0).rotated(self.dog_body.angle)
    #     self.dog_body.velocity = speed * direction


    def car_is_crashed(self, readings):
        
    
        if (readings[0][0]==1 and readings[0][1] != -5) \
            or (readings[1][0] == 1 and readings[1][1] != -5 ) \
            or (readings[2][0] == 1 and readings[2][1] != -5 ) :

            return 1
        else:
            return 0
    
    def cat_is_caught(self, readings, readings2):
        
        if (readings[0][0]==1 and readings[0][1] == -5) \
            or (readings[1][0] == 1 and readings[1][1] == -5 ) \
            or (readings[2][0] == 1 and readings[2][1] == -5 ) \
            or (readings2[0][0]==1 and readings2[0][1] == -5) \
            or (readings2[1][0] == 1 and readings2[1][1] == -5 ) \
            or (readings2[2][0] == 1 and readings2[2][1] == -5 ):
            
            return True
        else:
            return False

    def recover_from_crash(self, driving_direction):
        """
        We hit something, so recover.
        """
        while self.crashed:
            # Go backwards.
            self.car_body.velocity = -30 * driving_direction
            self.crashed = False
            for i in range(10):
                self.car_body.angle += .2  # Turn a little.
                screen.fill(THECOLORS["red"])  # Red is scary!
                draw(screen, self.space)
                self.space.step(1./10)
                if draw_screen:
                    pygame.display.flip()
                clock.tick()

    def recover_from_caught(self, moving_direction):
        """
        We hit something, so recover.
        """
        while self.caught:
            # Go backwards.
            self.cat_body.position = random.randint(100,900), random.randint(100,600)    
            #self.car_body.velocity = -100 * driving_direction
            self.caught = False
            for i in range(10):
                self.car_body.angle += .2  # Turn a little.
                screen.fill(THECOLORS["green"])  # green is satisfying!
                draw(screen, self.space)
                self.space.step(1./10)
                if draw_screen:
                    pygame.display.flip()
                clock.tick()

    def sum_readings(self, readings):
        """Sum the number of non-zero readings."""
        readings = np.asarray(readings)
        a = np.transpose(readings)
        #print a[0],a[1]
       

        return sum (a[0][:3])

            
    def get_sonar_readings(self, x, y, angle):
        readings = []
        """
        Instead of using a grid of boolean(ish) sensors, sonar readings
        simply return N "distance" readings, one for each sonar
        we're simulating. The distance is a count of the first non-zero
        reading starting at the object. For instance, if the fifth sensor
        in a sonar "arm" is non-zero, then that arm returns a distance of 5.
        """
        # Make our arms.
        arm_left = self.make_sonar_arm(x, y)
        arm_middle = arm_left
        arm_right = arm_left

        # arm_back = arm_left

        # Rotate them and get readings.
        readings.append(self.get_arm_distance(arm_left, x, y, angle, 0.75))
        readings.append(self.get_arm_distance(arm_middle, x, y, angle, 0))
        readings.append(self.get_arm_distance(arm_right, x, y, angle, -0.75))

        # readings.append(self.get_arm_distance(arm_back, x, y, angle, 1.5))
        # readings.append(self.get_arm_distance(arm_back, x, y, angle, -0.75))
        # readings.append(self.get_arm_distance(arm_back, x, y, angle, -1.5))


        if show_sensors:
            pygame.display.update()

        return readings

    def get_arm_distance(self, arm, x, y, angle, offset):
        # Used to count the distance.
        i = 0
        obs = 0
        # Look at each point and see if we've hit something.
        for point in arm:
            i += 1

            # Move the point to the right spot.
            rotated_p = self.get_rotated_point(
                x, y, point[0], point[1], angle + offset
            )

            # Check if we've hit something. Return the current i (distance)
            # if we did.
            if rotated_p[0] <= 0 or rotated_p[1] <= 0 \
                    or rotated_p[0] >= width or rotated_p[1] >= height:
                return i, self.get_track_or_not(obs)  # Sensor is off the screen.
            else:
                obs = screen.get_at(rotated_p)
                if self.get_track_or_not(obs) != 0:
                    if show_sensors:       
                        pygame.draw.circle(screen, (255, 255, 255), (rotated_p), 10)
                    return i, self.get_track_or_not(obs)

            if show_sensors:
                pygame.draw.circle(screen, (255, 255, 255), (rotated_p), 2)

        # Return the distance for the arm.
        return i, self.get_track_or_not(obs)

    def make_sonar_arm(self, x, y):
        spread = 10  # Default spread.
        distance = 20  # Gap before first sensor.
        arm_points = []
        # Make an arm. We build it flat because we'll rotate it about the
        # center later.
        for i in range(1, 40):
            arm_points.append((distance + x + (spread * i), y))

        return arm_points

    def get_rotated_point(self, x_1, y_1, x_2, y_2, radians):
        # Rotate x_2, y_2 around x_1, y_1 by angle.
        x_change = (x_2 - x_1) * math.cos(radians) + \
            (y_2 - y_1) * math.sin(radians)
        y_change = (y_1 - y_2) * math.cos(radians) - \
            (x_1 - x_2) * math.sin(radians)
        new_x = x_change + x_1
        new_y = height - (y_change + y_1)
        return int(new_x), int(new_y)

    def get_track_or_not(self, reading):
        if reading == THECOLORS['black']:
            return 0
        if reading == THECOLORS['white']:
            return 0
        elif reading == THECOLORS['yellow']:
            return 5
        elif reading == THECOLORS['blue']:
            return 1
        elif reading == THECOLORS['orange']:
            return -5
        elif reading == THECOLORS['green']:
            return -5
        else :
            return 0 # red 
            
if __name__ == "__main__":
    game_state = GameState()
    while True:
        game_state.frame_step(random.randint(0, 2))
