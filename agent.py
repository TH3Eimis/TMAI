import random
from fitness import Fitness
import json

DEFAULT_GENES = {
    'max_speed': 1.0,
    'acceleration': 0.6,
    'steer': {
        'vsmall': 0.05,
        'small': 0.15,
        'medium': 0.25,
        'large': 0.5,},
    'crash_threshold': 5.0,
    'fitness_weights': {
        'distance': 1.0,
        'time': 1.0,
        'crashes': 1.0,
        'rewards': 1.0},
    'mutation_rate': 0.1,
    'crossover_rate': 0.7,
}

RANDOM_GENES = {
    'max_speed': random.uniform(0.3, 0.9),
    'acceleration': random.uniform(0.4, 1.0),
    'steer': {
        'vsmall': random.uniform(0.2, 0.25),
        'small': random.uniform(0.3, 0.4),
        'medium': random.uniform(0.4, 0.5),
        'large': random.uniform(0.5,0.6),},
    'crash_threshold': 10.0,
    'fitness_weights': {
        'distance': 1.0,
        'time': 1.0,
        'crashes': 1.0,
        'rewards': 1.0},
    'mutation_rate': random.uniform(0.2, 0.7),
    'crossover_rate': random.uniform(0.2, 0.7),
}

CUSTOM_GENES = {}

TM_SPEEDS = {
    'slow': 25,
    'medium': 60,
    'fast': 100,
    'Vfast': 200,
}

STEER_RIGHT = 65536
STEER_LEFT = -65536

class Agent:
    def __init__(self, id, genes=None):
        self.agent_id = id
        match genes:
            case "CUSTOM_GENES":
                self.genes = CUSTOM_GENES
            case "RANDOM_GENES":
                self.genes = RANDOM_GENES
            case None:
                self.genes = RANDOM_GENES
            case _:
                print("Invalid genes using DEFAULT_GENES")
                self.genes = RANDOM_GENES
        self.fitness = Fitness(self)
        self.distance = [] # distance from sides of the road (left 0, right 1)
        self.crash_mode = 0
        self.crash_steps = 0
        self.steer_mode = 0
        self.steer_steps = 0
        self.save_steer = 0.0


    def decisionMaking(self,state,prev_speed,crash,slope):
        steer = 0
        accel = 0
        brake = 0
        # Make decisions based on the state of the agent
        player_info = state.player_info
        scene_mobil = state.scene_mobil
        # print(f"slope is::::{slope}")
        if crash or self.crash_mode:
            self.crash_mode = 1
            brake = 1
            accel = 0
            self.crash_steps += 1
            if self.crash_steps > 99:
                self.crash_mode = 0
                self.crash_steps = 0
            return steer, accel, brake
        
        if self.steer_mode:
            self.steer_steps += 1
            steer = self.save_steer
            print(f"steer: {steer}")
            if state.display_speed < self.genes['max_speed'] * TM_SPEEDS['medium']:
                accel = 1
            if self.steer_steps > 49:
                self.steer_mode = 0
                self.steer_steps = 0
                self.save_steer = 0.0
            return steer, accel, brake

        if state.display_speed < self.genes['max_speed'] * TM_SPEEDS['fast']:
            if random.random() < self.genes['acceleration']:
                accel = 1

        print(f"slope is:{slope:3f}")
        match slope:
            case slope if slope > 0: # slope on right steer left
                match slope:
                    case slope if 0.25 < slope < 0.35:
                        # Vsmall steer left
                        steer = STEER_LEFT * self.genes['steer']['vsmall']
                        print(f"Vsmall steer left: {steer}")
                        self.save_steer = steer
                        self.steer_mode = 1
                    case slope if 0.35 < slope < 0.45:
                        # small steer left
                        steer = STEER_LEFT * self.genes['steer']['small']
                        print(f"small steer left: {steer}")
                        self.save_steer = steer
                        self.steer_mode = 1
                    case slope if 0.45 < slope < 0.6:
                        # medium steer left
                        steer = STEER_LEFT * self.genes['steer']['medium']
                        print(f"medium steer left: {steer}")
                        self.save_steer = steer
                        self.steer_mode = 1
                    case slope if 0.6 < slope < 0.9:
                        # large steer left
                        steer = STEER_LEFT * self.genes['steer']['large']
                        print(f"large steer left: {steer}")
                        self.save_steer = steer
                        self.steer_mode = 1

            case slope if slope < 0: # slope on left steer right
                match slope:
                    case slope if -0.3 > slope > -0.35:
                        # Vsmall steer right
                        steer = STEER_RIGHT * self.genes['steer']['vsmall']
                        print(f"Vsmall steer right: {steer}")
                        self.save_steer = steer
                        self.steer_mode = 1
                    case slope if -0.35 > slope > -0.45:
                        # small steer right
                        steer = STEER_RIGHT * self.genes['steer']['small']
                        print(f"small steer right: {steer}")
                        self.save_steer = steer
                        self.steer_mode = 1
                    case slope if -0.45 > slope > -0.6:
                        # medium steer right
                        steer = STEER_RIGHT * self.genes['steer']['medium']
                        print(f"medium steer right: {steer}")
                        self.save_steer = steer
                        self.steer_mode = 1
                    case slope if -0.6 > slope > -0.9:
                        # large steer right
                        steer = STEER_RIGHT * self.genes['steer']['large']
                        print(f"large steer right: {steer}")
                        self.save_steer = steer
                        self.steer_mode = 1
        # match slope:
        #     case slope if 0.35 < slope < 0.8 : # slope on right steer left
        #         left = 1
        #         right = 0
        #     case slope if -0.35 > slope > -0.8: # slope on left steer right
        #         left = 0
        #         right = 1
        return steer, accel, brake

    def run_process(self, state, prev_speed, challange=None, slope=0):
        crash = False
        steer = 0
        accel = 0
        brake = 0
        race_time = state.player_info.race_time
        if self.fitness.medal_times != {} and challange is not None:
            self.getMapData(challange)

        if self.crashDetection(state, prev_speed):
            crash = True
            self.fitness.crashes += 1

        if race_time >= 0 and state.player_info.finish_not_passed == True:
            steer,accel,brake = self.decisionMaking(state,prev_speed,crash,slope)
        # print(f"Steer: {steer}, Accel: {accel}, Brake: {brake}")
        return steer, accel, brake

    def crashDetection(self,state,prev_speed):
            current_speed = state.display_speed
            speed_dif = current_speed - prev_speed
            is_braking = state.scene_mobil.input_brake
            if current_speed != prev_speed and abs(current_speed - prev_speed) > self.genes['crash_threshold'] and speed_dif < 0 and is_braking != 1:
                return True
            return False
    
    def GetMapData(self, map_path):
        map_directory = "C:/Users/Eimis/Documents/TrackMania/Tracks/Challenges/My Challenges/" + map_path + ".Challenge.Gbx"
        with open(map_directory, 'r', encoding='latin-1') as file:
            map_data = ''
            for line in file:
                map_data += line
                if '</header>' in line:
                    break
        bronze_index = map_data.find('bronze="')
        silver_index = map_data.find('silver="')
        gold_index = map_data.find('gold="')
        author_index = map_data.find('authortime="')

        if bronze_index != -1 and silver_index != -1 and gold_index != -1 and author_index != -1:
            bronze_time = int(map_data[bronze_index + len('bronze="'):map_data.find('"', bronze_index + len('bronze="'))])/1000
            silver_time = int(map_data[silver_index + len('silver="'):map_data.find('"', silver_index + len('silver="'))])/1000
            gold_time = int(map_data[gold_index + len('gold="'):map_data.find('"', gold_index + len('gold="'))])/1000
            author_time = int(map_data[author_index + len('authortime="'):map_data.find('"', author_index + len('authortime="'))])/1000

            map_data_dict = {
                "bronze": bronze_time,
                "silver": silver_time,
                "gold": gold_time,
                "author": author_time
            }
        
        return map_data_dict

        # print(f"Map data: {map_data_dict}")
        # print(f"Medal times: {self.fitness.medal_times}")
        
        # with open('map_data.json', 'w') as json_file:
        #             json.dump(map_data_dict, json_file)

    def save_agent(self):
        file_path = f"saved_agent_{self.agent_id}.json"
        agent_data = {
            'genes': self.genes,
            'fitness_values': {
            'distance': self.fitness.distance,
            'time_taken': self.fitness.time_taken,
            'crashes': self.fitness.crashes,
            'rewards': self.fitness.rewards,
            }
        }
        with open(file_path, 'w') as file:
            json.dump(agent_data, file)