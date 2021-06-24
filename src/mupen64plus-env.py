import gym
from gym import spaces

import subprocess
import threading
import pyautogui
from flask import Flask, jsonify
import numpy as np
import time
import logging
from PIL import ImageGrab

class Mupen64PlusEnv(gym.Env):

    def __init__(self, rom_path="/rom/smash.n64", player1=True, player2=False, player3=False, player4=False):
        self.NO_OP = {"START_BUTTON": 0, "U_CBUTTON": 0, "L_DPAD": 0, "A_BUTTON": 0, "B_BUTTON": 0, "X_AXIS": 0, "L_CBUTTON": 0,
                      "R_CBUTTON": 0, "R_TRIG": 0, "R_DPAD": 0, "D_CBUTTON": 0, "Z_TRIG": 0, "Y_AXIS": 0, "L_TRIG": 0, "U_DPAD": 0, "D_DPAD": 0}

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

        observation = self._observation()
        reward = self._get_reward()
        done = self._is_done()
        info = {}
        return observation, reward, done, info
    
    def _render(self, mode="rgb_array"):
        assert mode == "rgb_array"
        return self._observation()

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
                           "/usr/local/lib/mupen64plus/mupen64plus-input-bot.so", rom_path]
        self.mupen64plus = subprocess.Popen(
            cmd_mupen64plus, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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


if __name__ == '__main__':
    from tqdm import tqdm
    env = Mupen64PlusEnv(player1=False)
    for i in tqdm(range(3000)):
        observation, reward, done, info = env._step({})
        
        if i%10 == 0:
            import cv2
            cv2.imwrite("iamge{0}.png".format(str(i).zfill(4)),observation)
            