#from urllib import request
from flask import Flask, request
from numpy import angle
import position
app = Flask(__name__)

flag1 = False
flag2 = False
angle1 = None
angle2 = None

@app.route('/')
def hello_world():
    global flag1
    global flag2
    global angle1
    global angle2

    is_angle1 = request.args.get('angle1')  # parameter 꺼내서 angle1과 angle2 중 어느 것이 왔는지 확인 
    is_angle2 = request.args.get('angle2')

    if is_angle1 != None:   # angle1을 받은 경우
        flag1 = True
        angle1 = is_angle1
    if is_angle2 != None:   # angle2을 받은 경우
        flag2 = True
        angle2 = is_angle2

    print(angle1)
    print(angle2)

    if flag1 and flag2: # angle1과 angle2가 차례로 모두 받았을 떄
        position.position_server(float(angle1), float(angle2))
        flag1 = False
        flag2 = False   

    return 'Hello World!'

@app.route('/flag') # flag1,2를 확인하기 위한 
def show_flag():
    global flag1
    global flag2
    print("flag1: ", flag1)
    print("flag2: ", flag2)
    
    return 'flag is returned!'
if __name__ == '__main__':
    app.run()