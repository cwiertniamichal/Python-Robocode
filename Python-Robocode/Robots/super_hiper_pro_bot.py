#! /usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import random
import tensorflow as tf
from robot import Robot  # Import a base Robot


def log_to_file(msg):
    with open('logs.log', 'a+') as f:
        f.write(msg + '\n')


COLLIDED_WALL = 'collided_wall'
COLLIDED_ENEMY = 'collided_enemy'

MOVE_FORWARD = 0
MOVE_BACKWARD = 1
# TURN_LEFT_AND_MOVE_FORWARD = 3
# TURN_RIGHT_AND_MOVE_FORWARD = 4
STAY = 2

GAMMA = 0.9


class SuperHiperProBot(Robot):  # Create a Robot
    def move_forward(self):
        self.move(50)

    def move_backward(self):
        self.move(-50)

    def init(self, sess, model, memory):
        print "mem" + str(memory)
        # Set the bot color in RGB
        self.setColor(0, 0, 0)
        self.setGunColor(200, 200, 0)
        self.setRadarColor(255, 60, 0)
        self.setBulletsColor(0, 200, 100)

        self.radarVisible(True)  # show the radarField

        self._eps = 0.1
        print sess
        self.sess = sess
        self.model = model
        self.memory = memory

        # collided with enemy, collided with wall
        self.old_state = {
            COLLIDED_WALL: 0,
            COLLIDED_ENEMY: 0
        }
        self.state = {
            COLLIDED_WALL: 0,
            COLLIDED_ENEMY: 0
        }
        self.action = STAY
        self.actions = {
            STAY: self.stop,
            MOVE_FORWARD: self.move_forward,
            MOVE_BACKWARD: self.move_backward,
        }

        self.reward = 0

        # get the map size
        size = self.getMapSize()  # get the map size
        log_to_file('Map size: {}'.format(size))
        log_to_file('init')

    def run(self):  # NECESARY FOR THE GAME  main loop to command the bot
        self.memory.add_sample((self.old_state.values(), self.action, self.reward,
                               self.state.values()))
        print "sess + {}".format(self.sess)
        self._replay()
        self.old_state = self.state

        # restart reward, perform action based on state
        self.reward = 0
        self.action = self._choose_action(np.array(self.state.values()))
        self.actions[self.action]()


    def sensors(self):  # NECESARY FOR THE GAME
        """Tick each frame to have data about the game"""

        pos = self.getPosition()  # return the center of the bot
        x = pos.x()  # get the x coordinate
        y = pos.y()  # get the y coordinate

        angle = self.getGunHeading()  # Returns the direction that the robot's gun is facing
        angle = self.getHeading()  # Returns the direction that the robot is facing
        angle = self.getRadarHeading()  # Returns the direction that the robot's radar is facing
        list = self.getEnemiesLeft()  # return a list of the enemies alive in the battle
        for robot in list:
            id = robot["id"]
            name = robot["name"]
            # each element of the list is a dictionnary with the bot's id and the bot's name

    def onHitByRobot(self, robotId, robotName):
        self.reward -= 30
        self.state[COLLIDED_ENEMY] = 1

        self.rPrint("damn a bot collided me!")

    def onHitWall(self):
        self.reward -= 30
        self.state[COLLIDED_WALL] = 1

        self.reset()
        self.rPrint('ouch! a wall !')
        self.setRadarField("large")  # Change the radar field form

    def onRobotHit(self, robotId, robotName):  # when My bot hit another
        self.reward -= 30
        self.state[COLLIDED_ENEMY] = 1

        self.rPrint('collision with:' + str(robotName))

    def onHitByBullet(self, bulletBotId, bulletBotName,
                      bulletPower):  # NECESARY FOR THE GAME
        """ When i'm hit by a bullet"""
        self.reward -= 50
        self.reset()
        self.rPrint("hit by {} with power: {}".format(bulletBotName,
                                                      bulletPower))

    def onBulletHit(self, botId, bulletId):  # NECESARY FOR THE GAME
        """when my bullet hit a bot"""
        self.rPrint("fire done on " + str(botId))

    def onBulletMiss(self, bulletId):  # NECESARY FOR THE GAME
        """when my bullet hit a wall"""
        self.rPrint("the bullet " + str(bulletId) + " fail")
        self.pause(10)  # wait 10 frames

    def onRobotDeath(self):  # NECESARY FOR THE GAME
        """When my bot die"""
        self.reward -= 100
        self.rPrint("damn I'm Dead")

    def onTargetSpotted(self, botId, botName, botPos):  # NECESARY FOR THE GAME
        "when the bot see another one"
        self.fire(5)
        self.rPrint("I see the bot:" + str(botId) + "on position: x:" + str(
            botPos.x()) + " , y:" + str(botPos.y()))

    # Below functions for AI

    def _choose_action(self, state):
        if random.random() < self._eps:
            return random.randint(0, self.model._num_actions - 1)
        else:
            return np.argmax(self.model.predict_one(state, self.sess))

    def _replay(self):
        batch = self.memory.sample(self.model._batch_size)
        print "batch: {}".format(batch)
        states = np.array([val[0] for val in batch])
        next_states = np.array([(np.zeros(self.model._num_states)
                                 if val[3] is None else val[3]) for val in batch])
        # predict Q(s,a) given the batch of states
        q_s_a = self.model.predict_batch(states, self.sess)
        # predict Q(s',a') - so that we can do gamma * max(Q(s'a')) below
        q_s_a_d = self.model.predict_batch(next_states, self.sess)
        # setup training arrays
        x = np.zeros((len(batch), self.model._num_states))
        y = np.zeros((len(batch), self.model._num_actions))
        for i, b in enumerate(batch):
            state, action, reward, next_state = b[0], b[1], b[2], b[3]
            # get the current q values for all actions in state
            current_q = q_s_a[i]
            # update the q value for action
            if next_state is None:
                # in this case, the game completed after action, so there is no max Q(s',a')
                # prediction possible
                current_q[action] = reward
            else:
                current_q[action] = reward + GAMMA * np.amax(q_s_a_d[i])
            x[i] = state
            y[i] = current_q
        self.model.train_batch(self.sess, x, y)

    def state_to_int(self, state):
        num = 0
        if state[COLLIDED_WALL]:
            num += 1
        if state[COLLIDED_ENEMY]:
            num += 2
        return num
