__author__ = 'xSp4rkz'

# This file is part of Bread Buddy.

# Bread Buddy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Police Dash Pad is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Bread Buddy.  If not, see <http://www.gnu.org/licenses/>.

class TaskManager():

    def __init__(self):

        self._NumberOfTasks = 0
        self._TasksCompleted = 0
        self._CallBacks = []

    def AddTask(self, NumberOfTasksToAdd=1):

        self._NumberOfTasks += NumberOfTasksToAdd # Increase task count

    def RemoveTask(self, NumberOfTasksToRemove=1):

        self._NumberOfTasks -= NumberOfTasksToRemove

        if self._NumberOfTasks < 0: self._NumberOfTasks = 0 # Make sure the number of tasks doesnt fall below 0

    def CompleteTask(self, NumberOfTasksCompleted=1):

        self._TasksCompleted += NumberOfTasksCompleted # Increase the tasks completed count

        if self._TasksCompleted > self._NumberOfTasks: self._TasksCompleted = self._NumberOfTasks # Can't exceed the amount of tasks available

        for CallBack in self._CallBacks:

            CallBack()

    def NumberOfTasks(self):

        return self._NumberOfTasks

    def NumberOfTasksCompleted(self):

        return self._TasksCompleted

    def PercentCompleted(self):

        return int((self._TasksCompleted * 100) / self._NumberOfTasks) # Calculate the percentage

    def AddCallBack(self, CallBackFunction):

        # Create a list of call back functions that wish to be notified any time a task is completed.
        # Aids in the use of progress bars and tracking progress
        for CallBack in self._CallBacks:

            if CallBack == CallBackFunction:

                return

        self._CallBacks.append(CallBackFunction)