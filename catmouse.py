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
        self.crashed2 = 0
        self.caught = 0
        # Physics stuff.
        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0., 0.)

        # Create the cat.
        self.create_cat(100, 100, 0.5)
        self.create_mouse(900, 600, 0.5)

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
                (width - 2, height), (width - 2, 2), 2),
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

        self.obstacles = []
        self.obstacles.append(self.create_obstacle(200, 350, 70))
        self.obstacles.append(self.create_obstacle(700, 200, 80))
        self.obstacles.append(self.create_obstacle(600, 600, 70))

        # Create a mouse.
        # self.create_dog()

    def create_obstacle(self, x, y, r):
        c_body = pymunk.Body(pymunk.inf, pymunk.inf)
        c_shape = pymunk.Circle(c_body, r)
        c_shape.elasticity = 1.0
        c_body.position = x, y
        c_shape.color = THECOLORS["blue"]
        self.space.add(c_body, c_shape)
        return c_body

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

    def create_cat(self, x, y, r):
        inertia = pymunk.moment_for_circle(1, 0, 14, (0, 0))
        self.cat_body = pymunk.Body(3, inertia)
        self.cat_body.position = x, y
        self.cat_shape = pymunk.Circle(self.cat_body, 30)
        self.cat_shape.color = THECOLORS["green"]
        self.cat_shape.elasticity = 2.0
        self.cat_body.angle = r
        chasing_direction = Vec2d(1, 0).rotated(self.cat_body.angle)
        self.cat_body.apply_impulse(chasing_direction)
        self.space.add(self.cat_body, self.cat_shape)

    def create_mouse(self, x, y, r):
        inertia = pymunk.moment_for_circle(1, 0, 14, (0, 0))
        self.mouse_body = pymunk.Body(2, inertia)
        self.mouse_body.position = x, y
        self.mouse_shape = pymunk.Circle(self.mouse_body, 20)
        self.mouse_shape.color = THECOLORS["orange"]
        self.mouse_shape.elasticity = 2.0
        self.mouse_shape.angle = r
        running_direction = Vec2d(1, 0).rotated(self.mouse_body.angle)
        self.mouse_body.apply_impulse(running_direction)
        self.space.add(self.mouse_body, self.mouse_shape)

    def frame_step(self, action, action2):

        chasing_direction = Vec2d(1, 0).rotated(self.cat_body.angle)
        # self.cat_body.velocity = 20 * chasing_direction
        self.cat_body.velocity = 20 * chasing_direction

        running_direction = Vec2d(1, 0).rotated(self.mouse_body.angle)
        # self.mouse_body.velocity = 20 * running_direction
        self.cat_body.velocity =  20 * chasing_direction

        reward = 0
        reward2 = 0

        if action == 0:  # Turn left.
            # self.cat_body.angle -= .2
            chasing_direction = Vec2d(1, 0).rotated(self.cat_body.angle + 0.2)
            self.cat_body.apply_force((0.01, 0),chasing_direction)
            reward = -2

        elif action == 1:  # Turn right.
            # self.cat_body.angle += .2
            chasing_direction = Vec2d(1, 0).rotated(self.cat_body.angle - 0.2)
            self.cat_body.apply_force((0.01, 0),chasing_direction)
            reward = -2

        # elif action == 2:  # Turn right.
        #     # self.cat_body.angle += .2
        #     chasing_direction = Vec2d(1, 0).rotated(self.cat_body.angle)
        #     self.cat_body.apply_force((0.02,0),chasing_direction)

        # elif action == 3:
        #     chasing_direction = Vec2d(1, 0).rotated(self.cat_body.angle)
        #     self.cat_body.apply_force((0.02,0),-chasing_direction)
            # self.cat_body.velocity *= 0.8

        elif action2 == 0:  # Turn right.
            # self.mouse_body.angle += .2  
            running_direction = Vec2d(1, 0).rotated(self.mouse_body.angle + 0.2)
            self.mouse_body.apply_force((0.01,0),running_direction)
            reward2 = -2

        elif action2 == 1:  # Turn right.
            # self.mouse_body.angle += .2
            running_direction = Vec2d(1, 0).rotated(self.mouse_body.angle - 0.2)
            self.mouse_body.apply_force((0.01,0),running_direction)
            reward2 = -2

        # elif action2 == 2:
        #     running_direction = Vec2d(1, 0).rotated(self.mouse_body.angle)
        #     self.mouse_body.apply_force((0.02,0),running_direction)

        # elif action2 == 3:
        #     running_direction = Vec2d(1, 0).rotated(self.mouse_body.angle)
        #     self.mouse_body.apply_force((0.02,0),-running_direction)


        # Move obstacles.
        # if self.num_steps % 50 == 0:
        #     self.move_obstacles()

        # Move mouse.
        # if self.num_steps % 5 == 0:
        #     self.move_mouse()

        # if self.num_steps % 5 == 0:
        #     self.move_dog()

        # chasing_direction = Vec2d(1, 0).rotated(self.cat_body.angle)
        # self.cat_body.velocity = 30 * chasing_direction

        # running_direction = Vec2d(1, 0).rotated(self.mouse_body.angle)
        # self.mouse_body.velocity = 30 * running_direction

        

        # Update the screen and stuff.
        screen.fill(THECOLORS["black"])
        draw(screen, self.space)
        self.space.step(1./10)  #original 1./10
        if draw_screen:
            pygame.display.flip()
        clock.tick()

        # Get the current lomouseion and the readings there.
        x, y = self.cat_body.position
        x_mouse, y_mouse = self.mouse_body.position

        # if ball out of screen, seng them back
        if x_mouse < 5 or x_mouse > 995 or y_mouse < 5 or y_mouse > 695:
            self.mouse_body.position = random.randint(100,900), random.randint(100,600)    
            x_mouse, y_mouse = self.mouse_body.position

        if x < 5 or x > 995 or y < 5 or y > 695:
            self.cat_body.position = random.randint(100,900), random.randint(100,600)    
            x, y = self.cat_body.position

        readings = self.get_sonar_readings(x, y, self.cat_body.angle)
        readings2 = self.get_sonar_readings(x_mouse, y_mouse, self.mouse_body.angle)


        # add velocity to state space
        readings.append(self.cat_body.velocity)
        readings2.append(self.mouse_body.velocity)

        state = np.array([readings])
        state2 = np.array([readings2])

        print("current state: cat %s mouse %s " %(readings, readings2))

        # Set the reward.
        # cat crashed when any reading == 1

        if self.hit_the_wall(readings):
            self.crashed = 1
            reward += -100
            self.recover_from_crash(chasing_direction)

        if self.hit_the_wall(readings2):
            self.crashed2 = 1
            reward2 += -100
            self.recover_from_crash2(running_direction)


        if self.mouse_is_caught(readings, readings2):
            self.caught = 1
            reward = 500
            reward2 = -500
            self.recover_from_caught(running_direction)

        if readings[0][1] == -7 or readings[1][1] == -7 or readings[2][1] == -7:
            
            reward += 100 - int(self.sum_readings(readings) / 10)

        else: reward += -20 + int(self.sum_readings(readings) / 10)


        if readings2[0][1] == -7 or readings2[1][1] == -7 or readings2[2][1] == -7:

            reward2 += -100 + int(self.sum_readings(readings2) / 10)
        
        else: reward2 += -20 + int(self.sum_readings(readings2) / 10)
        
         # else:
         #    # Higher readings are better, so return the sum.
         #    reward = -12 + int(self.sum_readings(readings) / 10)

        print("current reward: cat %s, mouse %s" % (reward, reward2)) 

        self.num_steps += 1

        return reward, reward2, state, state2

    # def move_obstacles(self):
    #     # Randomly move obstacles around.
    #     for obstacle in self.obstacles:
    #         speed = random.randint(1, 5)
    #         direction = Vec2d(1, 0).rotated(self.cat_body.angle + random.randint(-2, 2))
    #         obstacle.velocity = speed * direction

    # def move_mouse(self):
    #     speed = random.randint(50, 100)
    #     self.mouse_body.angle -= random.randint(-1, 1)
    #     direction = Vec2d(1, 0).rotated(self.mouse_body.angle)
    #     self.mouse_body.velocity = speed * direction

    # def move_dog(self):
    #     speed = random.randint(40, 60)
    #     self.dog_body.angle -= random.randint(-1, 1)
    #     direction = Vec2d(1, 0).rotated(self.dog_body.angle)
    #     self.dog_body.velocity = speed * direction


    def hit_the_wall(self, readings):
        
        if (readings[0][0]== 1 and readings[0][1] != -7) \
            or (readings[1][0] == 1 and readings[1][1] != -7 ) \
            or (readings[2][0] == 1 and readings[2][1] != -7 ) :

            return 1
        else:
            return 0
    
    def mouse_is_caught(self, readings, readings2):
        
        if (readings[0][0]== 1 and readings[0][1] == -7) \
            or (readings[1][0] == 1 and readings[1][1] == -7 ) \
            or (readings[2][0] == 1 and readings[2][1] == -7 ) \
            or (readings2[0][0]==1 and readings2[0][1] == -7) \
            or (readings2[1][0] == 1 and readings2[1][1] == -7 ) \
            or (readings2[2][0] == 1 and readings2[2][1] == -7 ):
            
            return True
        else:
            return False

    def recover_from_crash(self, chasing_direction):
        """
        We hit something, so recover.
        """
        while self.crashed:
            # Go backwards.
            self.cat_body.velocity = -20 * chasing_direction
            self.crashed = False
            for i in range(10):
                self.cat_body.angle += .2  # Turn a little.
                # screen.fill(THECOLORS["red"])  # Red is scaty!
                draw(screen, self.space)
                self.space.step(1./10)
                if draw_screen:
                    pygame.display.flip()
                clock.tick()

    def recover_from_crash2(self, running_direction):
        """
        We hit wall, so recover.
        """
        while self.crashed2:
            # Go backwards.
            self.mouse_body.velocity = -20 * running_direction
            self.crashed2 = False
            for i in range(10):
                self.mouse_body.angle += .2  # Turn a little.
                # screen.fill(THECOLORS["red"])  # Red is scaty!
                draw(screen, self.space)
                self.space.step(1./10)
                if draw_screen:
                    pygame.display.flip()
                clock.tick()


    def recover_from_caught(self, running_direction):
        """
        We hit something, so recover.
        """
        while self.caught:
            # Go backwards.
            self.mouse_body.position = random.randint(100, 900), random.randint(100, 600)    
            #self.cat_body.velocity = -100 * chasing_direction
            self.caught = False
            for i in range(10):
                self.cat_body.angle += .2  # Turn a little.
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
        elif reading == THECOLORS['red']:
            return 1
        # elif reading == THECOLORS['yellow']:
        #     return 5 
        elif reading == THECOLORS['blue']:
            return 1 # obstacle
        elif reading == THECOLORS['orange']:
            return -7 # mouse
        elif reading == THECOLORS['green']:
            return -7 # cat
        else :
            return 0 # wall 
            
if __name__ == "__main__":
    game_state = GameState()
    while True:
        game_state.frame_step(random.randint(0, 5),random.randint(0, 5))
