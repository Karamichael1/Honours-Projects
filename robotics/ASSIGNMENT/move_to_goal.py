#!/usr/bin/env python

import PRM
import move
import sys
import numpy as np
import rospy 
from gazebo_msgs.srv import GetModelState

def extract_goal_coords():
    if len(sys.argv) != 3:
        print("Usage: python script.py x y")
        return None
    try:
        x = float(sys.argv[1])
        y = float(sys.argv[2])
        return np.array([x, y])
    except ValueError:
        print("Coordinates must be numeric")
        return None

def get_coordinates():
    rospy.wait_for_service('/gazebo/get_model_state')
    try:
        get_model_state = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
        model_state = get_model_state('mobile_base', 'world')
        position = model_state.pose.position
        return np.array([position.x, position.y])
    except rospy.ServiceException as e:
        print("Service call failed:", e)


def real_to_map(coords):
    return np.array([round(635 + (25.5/0.5108) * coords[0]), round(635 + (21.5/-0.4459) * coords[1])])

def map_to_real(coords):
    return np.array([(coords[0] - 635)/(25.5/0.5108), (coords[1] - 635)/(21.5/-0.4459)])

def array_to_tuple(array):
    return tuple(array.tolist())

def tuple_to_array(tuple):
    return np.array(tuple, dtype=float)

if __name__ == '__main__':
    goal = extract_goal_coords()
    start = get_coordinates()

    path = PRM.find_path(start_point=array_to_tuple(real_to_map(start)), target_point=array_to_tuple(real_to_map(goal)),
                         map_path='Mapping.pgm', save_path='roadmap.pkl')
    
    # remove start from path
    # path = path[1:]

    if path is not None:
        print(path)
        print([map_to_real(tuple_to_array(point)) for point in path])

        for point in path:
            move.move_to_prop(map_to_real(tuple_to_array(point)))
        
        # for index, point in enumerate(path):
        #     if index == len(path) - 1:  # if goal point
        #         move.move_to_prop(map_to_real(tuple_to_array(point)))
        #     else:
        #         move.move_to(map_to_real(tuple_to_array(point)))
    else:
        print('No path found')
