import gym
from gym import spaces
from mupen64plus_env import Mupen64PlusEnv

import cv2

class SmashEnv(Mupen64PlusEnv):

    def __init__(self, player1='pikachu', player2='dk', p1_color='CUP', p2_color='CLEFT', CPU_Lv=10, map="DreamLand"):

        super().__init__(rom_path="/rom/smash.n64", player1=True, player2=False, player3=False, player4=False)
        buttons = {'R_DPAD', 'R_CBUTTON', 'L_DPAD', 'Y_AXIS', 'D_DPAD', 'A_BUTTON', 'L_CBUTTON', 'B_BUTTON', 'R_TRIG', 'Z_TRIG', 'U_DPAD', 'X_AXIS', 'U_CBUTTON', 'START_BUTTON', 'L_TRIG', 'D_CBUTTON'}
        self._wait(count=170)# Hal Screen
        obs = self._observation() 
        self._press_button("START_BUTTON")
        for button in buttons:
            print(button)
            self._press_button(button)
        self._wait(count=150)# Splash Screen
        obs = self._observation()
        cv2.imwrite("splash.png", obs) 
        self.close()
        return 
        self._press_button("START_BUTTON")
        self._wait(count=30)# Load Main Menu
        self._press_button("DOWN")
        self._press_button("START_BUTTON")
        #set time infinity
        self._wait(count=30)# Load VS Menu
        self._press_button("DOWN")
        self._press_button("DOWN")
        self._press_button("LEFT")
        self._press_button("LEFT")
        self._press_button("LEFT")
        #Turn off items
        self._press_button("DOWN")
        self._press_button("START_BUTTON")
        self._wait(count=30)# Load Options Menu
        self._press_button("LEFT")
        self._press_button("LEFT")
        self._press_button("LEFT")
        obs = self._observation()
        cv2.imwrite("scr.png", obs)  

if __name__=="__main__":
    env = SmashEnv()
    env.close()
