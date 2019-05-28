#! /usr/bin/python
#-*- coding: utf-8 -*-

from PyQt4.QtGui import QGraphicsScene,  QMessageBox,  QBrush, QColor, QPixmap, QGraphicsRectItem
from PyQt4.QtCore import SIGNAL,  QPointF
from PyQt4 import QtCore,  Qt
from robot import Robot
import time,  os,  random
from outPrint import outPrint
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
import sys
sys.path.insert(0, os.path.join(dir_path, '../Robots/super_hiper_pro_bot.py'))

from super_hiper_pro_bot import SuperHiperProBot

import tensorflow as tf
import random


class Model:
    def __init__(self, num_states, num_actions, batch_size):
        self._num_states = num_states
        self._num_actions = num_actions
        self._batch_size = batch_size
        # define the placeholders
        self._states = None
        self._actions = None
        # the output operations
        self._logits = None
        self._optimizer = None
        self._var_init = None
        # now setup the model
        self._define_model()

    def _define_model(self):
        self._states = tf.placeholder(shape=[None, self._num_states], dtype=tf.float32)
        self._q_s_a = tf.placeholder(shape=[None, self._num_actions], dtype=tf.float32)
        # create a couple of fully connected hidden layers
        fc1 = tf.layers.dense(self._states, 50, activation=tf.nn.relu)
        fc2 = tf.layers.dense(fc1, 50, activation=tf.nn.relu)
        self._logits = tf.layers.dense(fc2, self._num_actions)
        loss = tf.losses.mean_squared_error(self._q_s_a, self._logits)
        self._optimizer = tf.train.AdamOptimizer().minimize(loss)
        self._var_init = tf.global_variables_initializer()

    def predict_one(self, state, sess):
        return sess.run(self._logits, feed_dict={self._states:
                                                     state.reshape(1,
                                                       self._num_states)})

    def predict_batch(self, states, sess):
        return sess.run(self._logits, feed_dict={self._states: states})

    def train_batch(self, sess, x_batch, y_batch):
        sess.run(self._optimizer,
                 feed_dict={self._states: x_batch, self._q_s_a: y_batch})


class Memory:
    def __init__(self, max_memory):
        self._max_memory = max_memory
        self._samples = []

    def add_sample(self, sample):
        self._samples.append(sample)
        if len(self._samples) > self._max_memory:
            self._samples.pop(0)

    def sample(self, no_samples):
        if no_samples > len(self._samples):
            return random.sample(self._samples, len(self._samples))
        else:
            return random.sample(self._samples, no_samples)


class Graph(QGraphicsScene):
    
    def __init__(self,  parent, width,  height):
        QGraphicsScene.__init__(self,  parent)
        self.setSceneRect(0, 0, width, height)
        self.Parent = parent
        
        #self.Parent.graphicsView.centerOn(250, 250)
        self.width = width
        self.height = height
        self.grid = self.getGrid()
        self.setTiles()

        
    def AddRobots(self, botList):
        
        """
        """
        self.aliveBots = []
        self.deadBots = []
        try:
            posList = random.sample(self.grid, len(botList))
            for bot in botList:
                try:
                    # here the bots are created (probably)
                    print bot
                    if 'Super' in str(bot):

                        model = Model(2, 3, 50)
                        memory = Memory(50000)

                        sess = tf.Session()
                        print "OPENED"
                        sess.run(model._var_init)
                        robot = bot(self.sceneRect().size(), self, str(bot),
                                    sess, model, memory)
                    else:
                        robot = bot(self.sceneRect().size(), self, str(bot))
                    self.aliveBots.append(robot)
                    self.addItem(robot)
                    robot.setPos(posList.pop())
                    self.Parent.addRobotInfo(robot)
                except Exception,  e:
                    print "Problem with bot file '%s': %s" % (bot, str(e))
            self.Parent.battleMenu.close()
        except ValueError:
            QMessageBox.about(self.Parent, "Alert", "Too many Bots for the map's size!")
        except AttributeError:
            pass

    def  battleFinished(self):
        print "battle terminated"
        try:
            self.deadBots.append(self.aliveBots[0])
            self.removeItem(self.aliveBots[0])
        except IndexError:
            pass
        j = len(self.deadBots)
        
        
        for i in range(j):
            print "N°",  j - i , ":", (self.deadBots[i])
            if j-i == 1: #first place
                self.Parent.statisticDico[repr(self.deadBots[i])].first += 1
            if j-i == 2: #2nd place
                self.Parent.statisticDico[repr(self.deadBots[i])].second += 1
            if j-i ==3:#3rd place
                self.Parent.statisticDico[repr(self.deadBots[i])].third += 1
                
            self.Parent.statisticDico[repr(self.deadBots[i])].points += i
                
        self.Parent.chooseAction()       

                    
    def setTiles(self):
        #background
        brush = QBrush()
        pix = QPixmap(os.getcwd() + "/robotImages/tile.png")
        brush.setTexture(pix)
        brush.setStyle(24)
        self.setBackgroundBrush(brush)
        
        #wall
        #left
        left = QGraphicsRectItem()
        pix = QPixmap(os.getcwd() + "/robotImages/tileVert.png")
        left.setRect(QtCore.QRectF(0, 0, pix.width(), self.height))
        brush.setTexture(pix)
        brush.setStyle(24)
        left.setBrush(brush)
        left.name = 'left'
        self.addItem(left)
        #right
        right = QGraphicsRectItem()
        right.setRect(self.width - pix.width(), 0, pix.width(), self.height)
        right.setBrush(brush)
        right.name = 'right'
        self.addItem(right)
        #top
        top = QGraphicsRectItem()
        pix = QPixmap(os.getcwd() + "/robotImages/tileHori.png")
        top.setRect(QtCore.QRectF(0, 0, self.width, pix.height()))
        brush.setTexture(pix)
        brush.setStyle(24)
        top.setBrush(brush)
        top.name = 'top'
        self.addItem(top)
        #bottom
        bottom = QGraphicsRectItem()
        bottom.setRect(0 ,self.height - pix.height() , self.width, pix.height())
        bottom.setBrush(brush)
        bottom.name = 'bottom'
        self.addItem(bottom)
        
    def getGrid(self):
        w = int(self.width/80)
        h = int(self.height/80)
        l = []
        for i in range(w):
            for j in range(h):
                l.append(QtCore.QPointF((i+0.5)*80, (j+0.5)*80))
        return l
