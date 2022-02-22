from cProfile import label
import math
import matlab
import matlab.engine
import calculate_new
import matplotlib.pyplot as plt

import numpy as np
import requests

anchor1 = [3,0] # anchor 위치 선언
anchor2 = [0,3]

def position_anchor1():    # anchor 1개로 위치 plot 하는 함수       ################################ test 용도
    snapshots = calculate_new.csv_to_ant()   #ant 파일로 분류하여 snapshots 수 반환 받음
    distance = calculate_new.csv_to_distance()  #rssi 값으로 부터 거리 추정
    print("snapshots:", snapshots)
    snapshots = matlab.double([snapshots])

    eng = matlab.engine.start_matlab()
    angle_raw = eng.Music_function(snapshots, nargout=1)

    print("angle:", angle_raw)    

    eng.quit()

    angle = 90 - angle_raw # y축 기준으로 plot하기 위해서
    angle_radian = math.radians(angle)
    origin = [0,0]
    target = [distance*math.cos(angle_radian), distance*math.sin(angle_radian)]
    print("target posistion:", target)
    #plt.plot([origin[0], target[0]], [origin[1], target[1]], color='yellow') # 거리 plot
    plt.scatter(target[0], target[1], c='r', s=50, label='target')  # target 
    plt.scatter(origin[0], origin[1], c='b', s=50, label='anchor')  # anchor
    plt.grid(True)
    plt.xlim([-5, 5])   
    plt.ylim([-1, 5])
    plt.xlabel('x(meter)')
    plt.ylabel('y(meter)')
    plt.title("Positioning")
    plt.text(2.8, -0.3, f"angle: {round(angle_raw, 2)}")
    plt.text(2.8, -0.6, f"distance: {round(distance, 2)}")
    plt.legend()
    plt.show()
    
def position_anchor2(): # anchor 2개로 위치 plot 하는 함수      ################################ test 용도
    angle1 = -20
    angle2 = -30
    angle1_radian = math.radians(angle1)
    angle2_radian = math.radians(angle2)
    x = np.arange(-2, 6, 0.1)
    y1 = math.tan(math.pi/2 - angle1_radian)*(x - 3)
    y2 = -math.tan(angle2_radian)*x + 3

    A = np.array([[-math.tan(angle2_radian), -1], [math.tan(math.pi/2 - angle1_radian), -1]])
    B = np.array([-3, 3*math.tan(math.pi/2 - angle1_radian)])
    C = np.linalg.solve(A, B)
    plt.scatter(C[0], C[1], c='r', s=50, label='target')    # 교점 
    plt.plot(x, y1)
    plt.plot(x, y2)
    plt.scatter(anchor1[0], anchor1[1], c='b', s=50, label='anchor')  # anchor1
    plt.scatter(anchor2[0], anchor2[1], c='b', s=50, label='anchor')  # anchor2

    plt.grid(True)
    plt.xlim([-2, 6])   
    plt.ylim([-2, 6])
    plt.xlabel('x(meter)')
    plt.ylabel('y(meter)')
    plt.title("Positioning")
    plt.legend()
    plt.show()

def estimate_angle():    # anchor 1개로 각도 추정
    snapshots = calculate_new.csv_to_ant()   #ant 파일로 분류하여 snapshots 수 반환 받음
    print("snapshots:", snapshots)
    snapshots = matlab.double([snapshots])

    eng = matlab.engine.start_matlab()
    angle = eng.Music_function(snapshots, nargout=1)

    print("angle:", angle)    

    eng.quit()

    return angle
    
def send_angle(angle1): # server에 추정한 각도 전달

    requests.get(f'http://127.0.0.1:5000/?angle1={angle1}')

def position_server(angle1, angle2):    #angle1, angle2 입력 받으면 위치 plot (server에서 2개 다 받으면 실행됨)

    angle1_radian = math.radians(angle1)
    angle2_radian = math.radians(angle2)
    x = np.arange(-2, 6, 0.1)
    y1 = math.tan(math.pi/2 - angle1_radian)*(x - 3)
    y2 = -math.tan(angle2_radian)*x + 3

    A = np.array([[-math.tan(angle2_radian), -1], [math.tan(math.pi/2 - angle1_radian), -1]])
    B = np.array([-3, 3*math.tan(math.pi/2 - angle1_radian)])
    C = np.linalg.solve(A, B)
    plt.scatter(C[0], C[1], c='r', s=50, label='target')    # 교점 
    plt.plot(x, y1)
    plt.plot(x, y2)
    plt.scatter(anchor1[0], anchor1[1], c='b', s=50, label='anchor')  # anchor1
    plt.scatter(anchor2[0], anchor2[1], c='b', s=50, label='anchor')  # anchor2

    plt.grid(True)
    plt.xlim([-2, 6])   
    plt.ylim([-2, 6])
    plt.xlabel('x(meter)')
    plt.ylabel('y(meter)')
    plt.title("Positioning")
    plt.legend()
    plt.show()

if __name__== '__main__':
    angle1 = estimate_angle()
    send_angle(angle1)