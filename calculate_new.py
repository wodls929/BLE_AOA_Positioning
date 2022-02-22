from tracemalloc import Snapshot
import matplotlib.pyplot as plt
import pandas as pd
import math
import numpy as np

wavelength = 0.125 # meter
distance = 0.035    # meter

def cal_phase(q, i):
    return math.atan2(q, i)

def average(angle):
    return sum(angle) / len(angle) 

def calculate_angle(sample_q_arr, sample_i_arr):      #i,q 받아서 각도 계산

    # i_sample = i.values.tolist()[8:45]
    # q_sample = q.values.tolist()[8:45]

    # i_sample = i.values.tolist()[0:45]
    # q_sample = q.values.tolist()[0:45]

    phase_radian = []
    phase_degree = []
    for i in range(len(sample_q_arr)):
        temp = cal_phase(sample_q_arr[i], sample_i_arr[i])
        if temp > math.pi:
            phase_radian.append(temp - 2*math.pi)
        elif temp < -math.pi:
            phase_radian.append(temp + 2*math.pi)
        else:
            phase_radian.append(temp)
            phase_degree.append(temp/ (math.pi) * 180)
    # print("phase(degree):", phase_degree)

    angle = []
    for i in range(len(phase_radian)//2):
        phase_diff = phase_radian[i*2] - phase_radian[i*2+1]
        if phase_diff > math.pi:
            phase_diff = phase_diff - 2*math.pi
        elif phase_diff < -math.pi:
            phase_diff = phase_diff + 2*math.pi
        else:
            pass
        # print("phase diff(degree):",  phase_diff/math.pi*180)
        d = phase_diff * wavelength     #----------> 나중에 채널별로 파장 다르게 해줘야 정확할 듯
        e = 2*math.pi*distance
        f = d/e
        if f > 1:
            asin=math.asin(1)
            print("각도 범위 넘음!! phase_diff:", phase_diff)
        elif f < -1:
            asin=math.asin(-1)
            print("각도 범위 넘음!! phase_diff:", phase_diff)
        else:
            asin = math.asin(f)     # ----------------> 이거 범위 문제
        
        angle.append(math.degrees(asin))
    
    angle_average = average(angle)

    print("average angle:", angle_average)
    # print(len(angle))
# 음수 각도 의미 ---> phase_radian[i*2]의 안테나와 물체간의 거리보다 phase_radian[i*2+1]의 안테나와 물체간 거리가 더 크다. 

def calculate_angle_csv():      #csv에서 i,q 가져와서 각도 계산하는 함수
    df = pd.read_csv('./rtls_connected_now_log/4MHz_2us_false_0.csv')

    for num in range(90):

        i = df['i']
        q = df['q']

        # i_sample = i.values.tolist()[num*180+32:num*180+180]   # 4MHz_2us_filtered
        # q_sample = q.values.tolist()[num*180+32:num*180+180]   

        # i_sample = i.values.tolist()[num*90+16:num*90+90]   # 2MHz_2us_filtered
        # q_sample = q.values.tolist()[num*90+16:num*90+90]   

        # i_sample = i.values.tolist()[num*45+8:num*45+45]  # 1MHz_2us_filtered
        # q_sample = q.values.tolist()[num*45+8:num*45+45]

        # i_sample = i.values.tolist()[num*82+8:num*82+82]  # 1MHz_1us_filtered
        # q_sample = q.values.tolist()[num*82+8:num*82+82]

        i_sample = i.values.tolist()[num*624+32:num*624+624]   # 4MHz_2us_no
        q_sample = q.values.tolist()[num*624+32:num*624+624]  

        # i_sample = i.values.tolist()[8:45]
        # q_sample = q.values.tolist()[8:45]

        # i_sample = i.values.tolist()[0:45]
        # q_sample = q.values.tolist()[0:45]

        phase_radian = []
        phase_degree = []            


        # for i in range(len(q_sample)):
        #     temp = cal_phase(q_sample[i], i_sample[i])
        #     if temp > math.pi:
        #         phase_radian.append(temp - 2*math.pi)
        #     elif temp < -math.pi:
        #         phase_radian.append(temp + 2*math.pi)
        #     else:
        #         phase_radian.append(temp)
        #         phase_degree.append(temp/ (math.pi) * 180)
        # # print("phase(degree):", phase_degree)

        for i in range(len(q_sample)):      # 새로 추가한 것
            # if i_sample[i] > 0:
            #     temp = math.atan2(q_sample[i], i_sample[i])
            # elif i_sample[i] <= 0 and q_sample[i] > 0:
            #     temp = math.pi + math.atan2(q_sample[i], i_sample[i])
            # elif i_sample[i] <= 0 and q_sample[i] <= 0:
            #     temp = -math.pi + math.atan2(q_sample[i], i_sample[i])
            temp = math.atan2(q_sample[i], i_sample[i]) # atan2가 -180~180 사이 값 반환
            phase_radian.append(temp)
            phase_degree.append(temp/ (math.pi) * 180)
        print("phase_degree", phase_degree)
        angle = []
        
        # for i in range(len(phase)-1):
        for i in range(len(phase_radian)//2):
            phase_diff = phase_radian[i*2] - phase_radian[i*2+1]
            if phase_diff > math.pi:
                phase_diff = phase_diff - 2*math.pi
            elif phase_diff < -math.pi:
                phase_diff = phase_diff + 2*math.pi
            else:
                pass
            print("phase diff(degree):",  phase_diff/math.pi*180)
            d = phase_diff * wavelength     #----------> 나중에 채널별로 파장 다르게 해줘야 정확할 듯
            e = 2*math.pi*distance
            f = d/e
            if f > 1:
                asin=math.asin(1)
                print("각도 범위 넘음!! phase_diff:", phase_diff)
            elif f < -1:
                asin=math.asin(-1)
                print("각도 범위 넘음!! phase_diff:", phase_diff)
            else:
                asin = math.asin(f)     # ----------------> 이거 범위 문제
            angle.append(math.degrees(asin))
        print(num)
        print("angle:", angle)
        # print(len(angle))
# 음수 각도 의미 ---> phase_radian[i*2]의 안테나와 물체간의 거리보다 phase_radian[i*2+1]의 안테나와 물체간 거리가 더 크다.

def csv_to_ant_no_filtering_4MHz_2us():
    df = pd.read_csv('4MHz_2us_012.csv')
    ant_0 = []
    ant_1 = []
    ant_2 = []

    i = df['i']
    q = df['q']
    i_sample_list = i.values.tolist()
    q_sample_list = q.values.tolist()
    # i_sample = i.values.tolist()[num*180+32:num*180+180]   # 4MHz_2us_filtered
    # q_sample = q.values.tolist()[num*180+32:num*180+180]   

    # i_sample = i.values.tolist()[num*90+16:num*90+90]   # 2MHz_2us_filtered
    # q_sample = q.values.tolist()[num*90+16:num*90+90]   

    # i_sample = i.values.tolist()[num*45+8:num*45+45]  # 1MHz_2us_filtered
    # q_sample = q.values.tolist()[num*45+8:num*45+45]

    # i_sample = i.values.tolist()[num*82+8:num*82+82]  # 1MHz_1us_
    print('0::::', int(len(i_sample_list)/624))             # 패킷 68개
    for num in range(int(len(i_sample_list)/624)):
        i_packet = i_sample_list[num*624+32:num*624+624]   # 4MHz_2us_no
        q_packet = q_sample_list[num*624+32:num*624+624]  
        print('1::::', int(len(i_packet)/16))           # 37번의 안테나 스위칭
        for i in range(int(len(i_packet)/16) - 1):      # 36번으로 맞춰야 ant1,2,3 배열 길이 맞음
            ant = i % 3 # antenna 번호
            print(ant)
            i_filtered = i_packet[i*16+8:i*16+16]
            q_filtered = q_packet[i*16+8:i*16+16]
            for j in range(8): 
                iq = complex(i_filtered[j], q_filtered[j])
                iq = str(iq)
                iq = iq.strip("("")") 
                if ant == 0:
                    ant_0.append(iq)
                if ant == 1:
                    ant_1.append(iq)
                if ant == 2:
                    ant_2.append(iq)
    print(len(ant_0))
    print(len(ant_1))
    print(len(ant_2)) 
    print(ant_0[5])      
    df = pd.DataFrame((zip(ant_0, ant_1, ant_2)), columns = ['ant_0', 'ant_1', 'ant_2'])
    df.to_csv('./MUSIC-Algorithm-master/ant.csv', index=False)

def csv_to_ant():    #csv 파일로 부터 ant 파일 생성(신호 안테나 별로 따로 나누어 놓은 파일)     # filtering_1MHz_2us
    df = pd.read_csv('iq_data.csv')
    ant_0 = []
    ant_1 = []
    ant_2 = []

    i = df['i']
    q = df['q']
    i_sample_list = i.values.tolist()
    q_sample_list = q.values.tolist()

    print('0::::', int(len(i_sample_list)/45))             
    for num in range(int(len(i_sample_list)/45)):
        i_packet = i_sample_list[num*45+8:num*45+45]   
        q_packet = q_sample_list[num*45+8:num*45+45]  
        for i in range(int(len(i_packet)) - 1):      # 36번으로 맞춰야 ant1,2,3 배열 길이 맞음
            ant = i % 3 # antenna 번호
            print(ant)
            iq = complex(i_packet[i], q_packet[i])
            iq = str(iq)
            iq = iq.strip("("")") 
            if ant == 0:
                ant_0.append(iq)
            if ant == 1:
                ant_1.append(iq)
            if ant == 2:
                ant_2.append(iq)
    snapshots = len(ant_0)
    print(len(ant_0))
    print(len(ant_1))
    print(len(ant_2))    
    df = pd.DataFrame((zip(ant_0, ant_1, ant_2)), columns = ['ant_0', 'ant_1', 'ant_2'])
    df.to_csv('ant.csv', index=False)
    #df.to_csv('C:/Users/JAEIN/code/MUSIC-Algorithm-master/ant.csv', index=False)

    return snapshots

def csv_to_distance():
    df = pd.read_csv('iq_data.csv')
    rssi = df['rssi']

    rssi_list = rssi.values.tolist()
    rssi_avg = sum(rssi_list)/len(rssi_list)
    N = 4   # 2~4
    distance = 10**((-64.43 - rssi_avg)/(10*N))
    print("distance:", distance)

    return distance


# if __name__ == '__main__':
#     calculate_angle_csv()

if __name__ == '__main__':
    csv_to_ant()

