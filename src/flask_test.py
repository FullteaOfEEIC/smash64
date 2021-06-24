from flask import Flask, jsonify
api = Flask(__name__)

@api.route("/0")
def player0():
    d = {
    "START_BUTTON": 0,
    "U_CBUTTON": 0,
    "L_DPAD": 0,
    "A_BUTTON": 1,
    "B_BUTTON": 0,
    "X_AXIS": -80,
    "L_CBUTTON": 0,
    "R_CBUTTON": 0,
    "R_TRIG": 0,
    "R_DPAD": 0,
    "D_CBUTTON": 0,
    "Z_TRIG": 0,
    "Y_AXIS": 80,
    "L_TRIG": 0,
    "U_DPAD": 0,
    "D_DPAD": 0
    }

    return jsonify(d)

api.run(port=8082)
