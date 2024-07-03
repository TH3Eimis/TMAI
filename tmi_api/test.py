import socket, struct, time, signal, random, numpy as np
from tminterface.structs import SimStateData, CheckpointData, RealTimeState
from tminterface.util import quat_to_ypw

HOST = "127.0.0.1"
PORT = 8477

SC_RUN_STEP_SYNC = 0
C_SET_SPEED = 1
C_REWIND_TO_STATE = 2
C_SET_INPUT_STATE = 3
C_SHUTDOWN = 4

sock = None

sorted_data = []

def signal_handler(sig, frame):
    global sock

    print('Shutting down...')
    sock.sendall(struct.pack('i', C_SHUTDOWN))
    sock.close()


def rewind_to_state(sock, state):
    sock.sendall(struct.pack('i', C_REWIND_TO_STATE))
    sock.sendall(struct.pack('i', len(state.data)))
    sock.sendall(state.data)

def set_input_state(sock, up=-1, down=-1, steer=0x7FFFFFFF):
    sock.sendall(struct.pack('i', C_SET_INPUT_STATE))
    sock.sendall(struct.pack('b', up))
    sock.sendall(struct.pack('b', down))
    sock.sendall(struct.pack('i', steer))

def respond(sock, type):
    sock.sendall(struct.pack('i', type))

def main():
    global sock

    first_state = 0

    ticks_per_second = 0
    now = time.time()

    current_speed = 0
    prev_speed = 0

    loopThresh = 0

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    signal.signal(signal.SIGINT, signal_handler)

    sock.connect((HOST, PORT))
    print('Connected')
    while True:
        message_type = struct.unpack('i', sock.recv(4))[0]
        if message_type == SC_RUN_STEP_SYNC:
            state_length = struct.unpack('i', sock.recv(4))[0]
            state = SimStateData(sock.recv(state_length))
            real_time_state = RealTimeState(state.data)
            state.cp_data.resize(CheckpointData.cp_states_field, state.cp_data.cp_states_length)
            state.cp_data.resize(CheckpointData.cp_times_field, state.cp_data.cp_times_length)

            current_speed = state.display_speed
            speed_dif = current_speed - prev_speed
            is_braking = state.scene_mobil.input_brake
            

            if loopThresh >= 10:
                loopThresh = 0
                prev_speed = current_speed
                # print(f'Current speed: {current_speed}')
                # print(f'is breaking: {is_braking}')
            
            race_time = state.player_info.race_time
            if race_time == 0: # when race starts do below
                first_state = state
                set_input_state(sock, up=True)

            # if race_time == 3000:
            #     set_input_state(sock, steer=-65536)

            if race_time > 0 and race_time % 10000 == 0 and first_state:
                rewind_to_state(sock, first_state)
                set_input_state(sock, up=True, steer=0x7FFFFFFF)

            respond(sock, SC_RUN_STEP_SYNC) # ---------- END OF CURRENT STEP ------------

            if time.time() - now > 1:
                #print(f'Effective speed: {ticks_per_second / 100}x')
                #print(f'Ticks per second: {ticks_per_second}')
                now = time.time()
                ticks_per_second = 0
            #print(f'race time: {state.player_info.race_time}')
            ticks_per_second += 1
            loopThresh += 1



# class Agent:
#     def __init__(self):
#         self.genes = {}  # Dictionary to store unique properties of the agent
#         self.fitness = fitness()

#         # Define AI parameters here, for example:
#         self.speed = 1.0
#         self.steer = 0.0

#     def communicate_with_socket(self, sock, state):
#         # Communicate with the socket based on the current state and AI parameters
#         race_time = state.player_info.race_time
#         car_speed = state.dyna.vel_mph
#         car_turning_vel = state.dyna.angular_speed
#         car_turning_bool = state.dyna.is_turning
#         damper_absorber = state.simulation_wheels.damper_absorber

#         if race_time == 0:  # when race starts do below
#             set_input_state(sock, up=True)

#         if race_time == 3000:
#             set_input_state(sock, steer=-65536)

#         if race_time > 0 and race_time % 5000 == 0:
#             rewind_to_state(sock, state)
#             set_input_state(sock, up=True, steer=0x7FFFFFFF)

#     def evaluate(self):
#         # Evaluate the fitness of the agent based on certain criteria
#         # For example, distance covered, time taken, etc.
#         self.fitness.evaluate()  # Implement this method according to your fitness evaluation criteria

#     @staticmethod
#     def crossover(parent1, parent2):
#         # Perform crossover between two parents to create offspring
#         # You can define your own crossover logic here
#         offspring = Agent()

#         # Example: Take some parameters from parent1 and some from parent2
#         offspring.speed = (parent1.speed + parent2.speed) / 2
#         offspring.steer = (parent1.steer + parent2.steer) / 2

#         return offspring

#     def mutate(self):
#         # Mutate the agent's parameters
#         # You can define your own mutation logic here
#         # Example: Randomly adjust speed and steer within certain bounds
#         self.speed += random.uniform(-0.1, 0.1)
#         self.steer += random.uniform(-0.1, 0.1)

#         # Ensure parameters stay within valid range, if needed
#         self.speed = max(0.0, min(1.0, self.speed))
#         self.steer = max(-1.0, min(1.0, self.steer))


if __name__ == "__main__":
    main()