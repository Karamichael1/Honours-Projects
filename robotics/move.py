#!/usr/bin/env python

import sys
import rospy
import numpy as np
import math
from std_msgs.msg import Empty
from geometry_msgs.msg import Twist
from gazebo_msgs.srv import GetModelState
from tf.transformations import euler_from_quaternion

def move_to_goal(U, R):
    rospy.loginfo("Moving to goal...")
    cmd_vel_pub = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=10)
    twist = Twist()
    twist.linear.x = U[0]
    twist.angular.z = R[0]
    cmd_vel_pub.publish(twist)

def static_rotate(R):
    rospy.loginfo("Rotating...")
    cmd_vel_pub = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=10)
    twist = Twist()
    twist.angular.z = R[0]
    cmd_vel_pub.publish(twist)

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

def get_orientation():
    rospy.wait_for_service('/gazebo/get_model_state')
    try:
        get_model_state = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
        model_state = get_model_state('mobile_base', 'world')
        orientation = model_state.pose.orientation
        orientation_np = np.array([orientation.x, orientation.y, orientation.z, orientation.w])
        roll, pitch, yaw = euler_from_quaternion(orientation_np)
        return [yaw]
    except rospy.ServiceException as e:
        print("Service call failed:", e)

def calculate_yaw(goal, current_pos):
    return np.arctan2(goal[1] - current_pos[1], goal[0] - current_pos[0])

def face_goal(goal_ori, Kp_ori):
    while True:
        current_ori = get_orientation()
        error_ori = goal_ori - current_ori

        if (np.linalg.norm(error_ori) > np.pi):
            error_ori =  (error_ori - 2*np.pi*math.copysign(1, error_ori))
        rospy.loginfo(error_ori)
        # Control inputs for orientation
        R = Kp_ori * error_ori

        static_rotate(R)

        if (np.linalg.norm(error_ori) < 0.03):
            break

def move_to_prop(goal):
    try:
        rospy.init_node('turtle_controller', anonymous=True)

        # position control constants
        Kp = 0.5
        Kp_ori = 0.5

        while True:
            current_pos = get_coordinates()
            error = np.absolute(goal - current_pos)
            goal_ori = calculate_yaw(goal, current_pos)

            current_ori = get_orientation()
            error_ori = goal_ori - current_ori
            if (np.linalg.norm(error_ori) > np.pi):
                error_ori =  (error_ori - 2*np.pi*math.copysign(1, error_ori))

            if (np.linalg.norm(error_ori) > 0.1):
                face_goal(goal_ori, Kp_ori)

            current_pos = get_coordinates()
            error = np.absolute(goal - current_pos)
            goal_ori = calculate_yaw(goal, current_pos)

            current_ori = get_orientation()
            error_ori = goal_ori - current_ori
            if (np.linalg.norm(error_ori) > np.pi):
                error_ori =  (error_ori - 2*np.pi*math.copysign(1, error_ori))

            if (np.linalg.norm(error) < 1):
                U = Kp * np.array([math.copysign(1, error[0])*math.sqrt(np.abs(error[0]))])
            else:
                U = Kp * error 
            
            # Control inputs for orientation
            R = Kp_ori * error_ori

            move_to_goal(U, R)

            if (np.linalg.norm(error) < 0.05):
                break

        rospy.loginfo("Script completed.")

    except rospy.ROSInterruptException:
        pass
