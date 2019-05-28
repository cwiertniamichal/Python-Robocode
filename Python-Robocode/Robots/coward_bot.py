#! /usr/bin/python
# -*- coding: utf-8 -*-

from robot import Robot  # Import a base Robot
from utils import calculate_distance


def log_to_file(msg):
    with open('coward_bot_logs.log', 'a+') as f:
        f.write(msg + '\n')


class CowardBot(Robot):  # Create a Robot

    def init(self):
        # Set the bot color in RGB
        self.setColor(0, 0, 0)
        self.setGunColor(200, 200, 0)
        self.setRadarColor(255, 60, 0)
        self.setBulletsColor(0, 200, 100)

        self.radarVisible(True)  # show the radarField

        # get the map size
        size = self.getMapSize()  # get the map size
        log_to_file('Map size: {}'.format(size))

    def run(self):  # NECESARY FOR THE GAME  main loop to command the bot

        # self.move(90)  # for moving (negative values go back)
        # self.turn(360)  # for turning (negative values turn counter-clockwise)
        # self.stop()
        # """
        # the stop command is used to make moving sequences: here the robot will move 90steps and turn 360° at the same time
        # and next, fire
        # """
        #
        # self.move(100)
        # self.turn(50)
        # self.stop()
        # bulletId = self.fire(
        #     2)  # to let you you manage if the bullet hit or fail
        # self.move(180)
        # self.turn(180)
        # self.gunTurn(
        #     90)  # to turn the gun (negative values turn counter-clockwise)
        # self.stop()
        # self.fire(1)  # To Fire (power between 1 and 10)
        # self.radarTurn(
        #     180)  # to turn the radar (negative values turn counter-clockwise)
        self.stop()

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
        self.rPrint("damn a bot collided me!")

    def onHitWall(self):
        self.reset()  # To reset the run fonction to the begining (auomatically called on hitWall, and robotHit event)
        self.rPrint('ouch! a wall !')
        self.setRadarField("large")  # Change the radar field form

    def onRobotHit(self, robotId, robotName):  # when My bot hit another
        self.rPrint('collision with:' + str(
            robotName))  # Print information in the robotMenu (click on the righ panel to see it)

    def onHitByBullet(self, bulletBotId, bulletBotName,
                      bulletPower):  # NECESARY FOR THE GAME
        """ When i'm hit by a bullet"""
        self.reset()  # To reset the run fonction to the begining (auomatically called on hitWall, and robotHit event)
        self.rPrint(
            "hit by " + str(bulletBotName) + "with power:" + str(bulletPower))

    def onBulletHit(self, botId, bulletId):  # NECESARY FOR THE GAME
        """when my bullet hit a bot"""
        self.rPrint("fire done on " + str(botId))

    def onBulletMiss(self, bulletId):  # NECESARY FOR THE GAME
        """when my bullet hit a wall"""
        self.rPrint("the bullet " + str(bulletId) + " fail")
        self.pause(10)  # wait 10 frames

    def onRobotDeath(self):  # NECESARY FOR THE GAME
        """When my bot die"""
        self.rPrint("damn I'm Dead")

    def onTargetSpotted(self, targetId, targetName, targetPos):  # NECESARY FOR THE GAME
        "when the bot see another one"
        self.rPrint("I see the bot:{} on position: x: {}, y:{}"
                    .format(targetId, targetPos.x(), targetPos.y()))
        distance = calculate_distance(self.getPosition(), targetPos)
        self.rPrint("Distance from bot: {}".format(distance))

        if distance < 100:
            radar_heading = self.getRadarHeading()
            tank_heading = self.getHeading()
            self.turn(tank_heading - radar_heading)
            self.move(-100)

        self.rPrint("Pos: {}".format(self.getPosition()))
