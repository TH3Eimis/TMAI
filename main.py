# created using empty template from https://gist.github.com/Agade09/f5b57048895b0a3a64fb0b1ae09cbd7f

import argparse
import socket, struct, time, signal, numpy as np
from tminterface.structs import SimStateData, CheckpointData, RealTimeState
from tminterface.util import quat_to_ypw
from population import Population
from fitness import Fitness
from agent import Agent
from vision import screen_record
import threading
from queue import Queue
import cv2
import matplotlib.pyplot as plt

from CTMInterface import MessageType, TMInterface


ITER_COUNT = 3

def iface_register(iface):
    while True:
        try:
            iface.register(2)
            break
        except ConnectionRefusedError as e:
            print(e)

    return iface

def run_client(population):
    parser = argparse.ArgumentParser()
    parser.add_argument("--tmi_port", "-p", type=int, default=8477)
    args = parser.parse_args()
    iface = TMInterface(args.tmi_port)
    iface = iface_register(iface)

    ticks_per_second = 0
    now = time.time()

    data_queue = Queue()

    # Start screen recording thread
    try:
        sr_thread = threading.Thread(target=screen_record, args=(data_queue,), daemon=True)
        sr_thread.start()
    except:
        print("window not found")

    current_agent_index = -1  # Track which agent is currently active

    prev_speed = 0
    fitness_list = []

    _challange = None
    while current_agent_index < population.size:
        current_agent_index += 1
        if current_agent_index == population.size:
            break
        prev_speed = 0
        fs = 0
        evry100 = 0
        while True:
            
            slope = 0
            current_agent = population.individuals[current_agent_index]
            msgtype = (iface._read_int32())
            # =============================================
            #        READ INCOMING MESSAGES
            # =============================================

            if not data_queue.empty():
                    slope = data_queue.get()
                    # print(f"recieving slope: {slope}")
                    data_queue.queue.clear()

            if msgtype == int(MessageType.SC_RUN_STEP_SYNC):
                _time = iface._read_int32()
                # print("time: ", _time)

                if fs == 0:
                    fs = 1
                    iface.set_speed(1)
                    iface.give_up()

                # ============================
                # BEGIN ON RUN STEP
                # ============================
                _state = iface.get_simulation_state()
                _challange = iface.get_current_challenge()
                _current_speed = _state.display_speed

                iface.reset_camera()
                steer, accel, brake = current_agent.run_process(_state,prev_speed,_challange,slope)
                iface.set_input_state(steer, accel, brake)
                if current_agent.fitness.crashes >= 10:
                    print(f"Agent {current_agent.agent_id} crashed too many times")
                    map_data_dict = current_agent.GetMapData(_challange)
                    current_agent.fitness.medal_times = map_data_dict
                    current_agent.fitness.rewards.append('crash')
                    current_agent.fitness.value = 0
                    print(f"Agent {current_agent.agent_id} finished with fitness: {current_agent.fitness.value}")
                    fitness_list.append(current_agent.fitness.value)
                    iface.prevent_simulation_finish()
                    iface.give_up()
                    iface._respond_to_call(msgtype)
                    break
                # ============================
                # END ON RUN STEP
                # ============================
                if evry100 == 100: # Every sim sec save speed
                    evry100 = 0
                    current_agent.fitness.average_speed += _current_speed

                prev_speed = _current_speed
                evry100 += 1
                iface._respond_to_call(msgtype)
            elif msgtype == int(MessageType.SC_CHECKPOINT_COUNT_CHANGED_SYNC):
                current = iface._read_int32()
                target = iface._read_int32()
                # ============================
                # BEGIN ON CP COUNT
                # ============================
                # Get Sim Data
                _state = iface.get_simulation_state()
                _challange = iface.get_current_challenge()
                race_time = _state.player_info.current_time
                # Save fitness data
                current_agent.fitness.time_taken = race_time/1000
                print(f"stateDisplasysleepedis: {_state.display_speed}")
                current_agent.fitness.average_speed += (_state.display_speed)*(evry100/100)

                map_data_dict = current_agent.GetMapData(_challange)
                current_agent.fitness.medal_times = map_data_dict

                current_agent.fitness.rewards.append('finish')
                current_agent.fitness.evaluate()
                print(f"Agent {current_agent.agent_id} finished with fitness: {current_agent.fitness.value}")
                fitness_list.append(current_agent.fitness.value)
                
                with open("test.txt", "a") as file:
                    file.write("\n".join(str(x) for x in current_agent.fitness.medal_times.values()) + "\n")
                iface.prevent_simulation_finish()
                iface.give_up()
                iface._respond_to_call(msgtype)
                break
                # ============================
                # END ON CP COUNT
                # ============================
            elif msgtype == int(MessageType.SC_LAP_COUNT_CHANGED_SYNC):
                iface._read_int32()
                iface._respond_to_call(msgtype)
            elif msgtype == int(MessageType.SC_REQUESTED_FRAME_SYNC):
                iface._respond_to_call(msgtype)
            elif msgtype == int(MessageType.C_SHUTDOWN):
                iface.close()
            elif msgtype == int(MessageType.SC_ON_CONNECT_SYNC):
                print("Connected")
                iface._respond_to_call(msgtype)
            elif msgtype == int(MessageType.C_IS_IN_MENUS):
                iface._respond_to_call(int(MessageType.C_IS_IN_MENUS))
            else:
                print(f"Unknown message type: {msgtype}")
                iface._respond_to_call(msgtype)

    population.plotFitness(fitness_list)
    population.evolve()
    sr_thread = None
    return population



def main():
    population = None
    for i in range(ITER_COUNT):
        if i == 0:
            population = Population()
            population.createPop(Agent)

        population = run_client(population)
        continue
        


if __name__ == "__main__":
    main()