import gym
from gym import spaces

import subprocess
import threading
from flask import Flask, jsonify
import numpy as np
import time
import logging
from PIL import ImageGrab
import timeout_decorator

class Mupen64PlusEnv(gym.Env):

    def __init__(self, rom_path="/rom/smash.n64", player1=True, player2=False, player3=False, player4=False):
        self.NO_OP = {"START_BUTTON": 0, "U_CBUTTON": 0, "L_DPAD": 0, "A_BUTTON": 0, "B_BUTTON": 0, "X_AXIS": 0, "L_CBUTTON": 0,
                      "R_CBUTTON": 0, "R_TRIG": 0, "R_DPAD": 0, "D_CBUTTON": 0, "Z_TRIG": 0, "Y_AXIS": 0, "L_TRIG": 0, "U_DPAD": 0, "D_DPAD": 0}
        
    
        self.observation_space = \
            spaces.Box(low=0, high=255, shape=(600, 440, 3))

        self.rom_path = rom_path

        # note: when playerx == False, playerx send NO Operation (which means no buttons are pressed) instead of unplugged.
        self.player1 = player1
        self.player2 = player2
        self.player3 = player3
        self.player4 = player4

        self.wait_for_player1 = True
        self.wait_for_player2 = True
        self.wait_for_player3 = True
        self.wait_for_player4 = True
        self.controller_state_player1 = self.NO_OP
        self.controller_state_player2 = self.NO_OP
        self.controller_state_player3 = self.NO_OP
        self.controller_state_player4 = self.NO_OP
        api = self._get_controll_server()
        self.controller_server = threading.Thread(
            target=api.run, kwargs={"port": 8082})
        self.controller_server.start()

        self.mupen64plus = None
        self._start_mupen64plus(self.rom_path)

    def _step(self, action):
        """
        input
            action: {
                        "player1": {
                            "START_BUTTON": 0,
                            "U_CBUTTON": 0,
                            "L_DPAD": 0,
                            "A_BUTTON": 0,
                            "B_BUTTON": 0,
                            "X_AXIS": 0,
                            "L_CBUTTON": 0,
                            "R_CBUTTON": 0,
                            "R_TRIG": 0,
                            "R_DPAD": 0,
                            "D_CBUTTON": 0,
                            "Z_TRIG": 0,
                            "Y_AXIS": 0,
                            "L_TRIG": 0,
                            "U_DPAD": 0,
                            "D_DPAD": 0
                        }
                        "palyer2": {
                            ...
                        }
                    }

        output
            observation, reward, done, info

            observation: a game screen (numpy.ndarray, (600*440*3)).
            reward: a reward of game. You have to implement self._get_reward() at inheritance destination (number).
            done: whether game is over. You have to implement self._is_done() at inheritance destination (bool).
            info: extra information.

        """
        if self.player1 == False:
            action["player1"] = self.NO_OP
        if self.player2 == False:
            action["player2"] = self.NO_OP
        if self.player3 == False:
            action["player3"] = self.NO_OP
        if self.player4 == False:
            action["player4"] = self.NO_OP


        self._act(action)

        observation = self._observation()
        reward = self._get_reward()
        done = self._is_done()
        info = {}
        return observation, reward, done, info

    @timeout_decorator(3)
    def _act(self, action):
        assert set(action.keys()) == {"player1",
                                      "player2", "player3", "player4"}
        self.controller_state_player1 = action["player1"]
        self.wait_for_player1 = False
        self.controller_state_player2 = action["player2"]
        self.wait_for_player2 = False
        self.controller_state_player3 = action["player3"]
        self.wait_for_player3 = False
        self.controller_state_player4 = action["player4"]
        self.wait_for_player4 = False
        while (self.wait_for_player1 and self.wait_for_player2 and self.wait_for_player3 and self.wait_for_player4) != True:
            continue
        
        return 

    
    def _render(self, mode="rgb_array"):
        assert mode == "rgb_array"
        return self._observation()

    def _close(self):
        self.mupen64plus.kill()
        self.controller_server.stop()

    def _observation(self):
        bbox = (212, 164, 812, 604)
        screenshot = ImageGrab.grab(bbox=bbox)
        return np.asarray(screenshot)

    def _get_reward(self):
        return 0

    def _is_done(self):
        return False

    def _start_mupen64plus(self, rom_path):
        cmd_mupen64plus = ["mupen64plus", "--input",
                           "/usr/local/lib/mupen64plus/mupen64plus-input-bot.so", "--set", "Input-Bot-Control0[plugged]=1", rom_path]
        self.mupen64plus = subprocess.Popen(
            cmd_mupen64plus)

    def _end_mupen64plus(self):
        if self.mupen64plus is None:
            return
        self.mupen64plus.kill()
        self.mupen64plus = None

    def _get_controll_server(self):
        logger = logging.getLogger("werkzeug")
        logger.setLevel(logging.ERROR)
        
        api = Flask(__name__)

        @api.route("/0")
        def player1():
            while self.wait_for_player1:
                continue

            self.wait_for_player1 = True
            return jsonify(self.controller_state_player1)

        @api.route("/1")
        def player2():
            while self.wait_for_player2:
                continue

            self.wait_for_player2 = True
            return jsonify(self.controller_state_player2)

        @api.route("/2")
        def player3():
            while self.wait_for_player3:
                continue

            self.wait_for_player3 = True
            return jsonify(self.controller_state_player3)

        @api.route("/3")
        def player4():
            while self.wait_for_player4:
                continue

            self.wait_for_player4 = True
            return jsonify(self.controller_state_player4)

        return api
    
    def _wait(self, count=1):
        action = {
            "player1": self.NO_OP,
            "player2": self.NO_OP,
            "player3": self.NO_OP,
            "player4": self.NO_OP
        }
        for c in range(count):
            self._act(action)
        return

    def _reset(self):
        return 

    def _press_button(self, op="A_BUTTON", player=1):
        buttons = {'R_DPAD', 'R_CBUTTON', 'L_DPAD', 'Y_AXIS', 'D_DPAD', 'A_BUTTON', 'L_CBUTTON', 'B_BUTTON', 'R_TRIG', 'Z_TRIG', 'U_DPAD', 'X_AXIS', 'U_CBUTTON', 'START_BUTTON', 'L_TRIG', 'D_CBUTTON'}
        sticks = {"LEFT","RIGHT","UP","DOWN"}
        assert op in buttons or op in sticks
        _action = {}
        for b in buttons:
            if b==op:
                _action[b]=1
            else:
                _action[b]=0
        if op=="LEFT":
            _action["X_AXIS"] = -80
        elif op=="RIGHT":
            _action["X_AXIS"] = 80
        elif op=="UP":
            _action["Y_AXIS"] = 80
        elif op=="DOWN":
            _action["Y_AXIS"] = -80
        action={}
        for p in range(1,5):
            if p==player:
                action["player{0}".format(p)] = _action
            else:
                action["player{0}".format(p)] = self.NO_OP
        self._act(action)#press button
        print(action)
        action={}
        for p in range(1,5):
            action["player{0}".format(p)] = self.NO_OP
        self._act(action)#release button



if __name__ == '__main__':
    from tqdm import tqdm
    env = Mupen64PlusEnv(player1=False)
    import cv2
    for i in tqdm(range(3000)):
        observation, reward, done, info = env._step({})
        
        if i%10 == 0:
            cv2.imwrite("iamge{0}.png".format(str(i).zfill(4)),observation)
            