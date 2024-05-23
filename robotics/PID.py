#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist, Pose
from nav_msgs.msg import Odometry
from math import atan2, sqrt

# PID controller parameters
kp_linear = 0.5  # Proportional gain for linear velocity
ki_linear = 0.1  # Integral gain for linear velocity
kd_linear = 0.2  # Derivative gain for linear velocity

kp_angular = 1.0  # Proportional gain for angular velocity
ki_angular = 0.0  # Integral gain for angular velocity
kd_angular = 0.2  # Derivative gain for angular velocity

# Goal position (x, y)
goal_x = 2.0
goal_y = 2.0

# Current robot pose
current_x = 0.0
current_y = 0.0
current_theta = 0.0

# PID controller variables
linear_error_integral = 0.0
linear_error_derivative = 0.0
angular_error_integral = 0.0
angular_error_derivative = 0.0
previous_linear_error = 0.0
previous_angular_error = 0.0

# Callback function to update the current robot pose
def odom_callback(msg):
    global current_x, current_y, current_theta
    current_x = msg.pose.pose.position.x
    current_y = msg.pose.pose.position.y
    current_theta = atan2(2 * (msg.pose.pose.orientation.w * msg.pose.pose.orientation.z + msg.pose.pose.orientation.x * msg.pose.pose.orientation.y), 1 - 2 * (msg.pose.pose.orientation.y ** 2 + msg.pose.pose.orientation.z ** 2))

# Calculate linear and angular errors
def calculate_errors():
    global linear_error_integral, linear_error_derivative, angular_error_integral, angular_error_derivative, previous_linear_error, previous_angular_error

    # Calculate linear error
    linear_error = sqrt((goal_x - current_x) ** 2 + (goal_y - current_y) ** 2)

    # Calculate angular error
    desired_theta = atan2(goal_y - current_y, goal_x - current_x)
    angular_error = desired_theta - current_theta

    # Update integral and derivative terms for linear error
    linear_error_integral += linear_error
    linear_error_derivative = linear_error - previous_linear_error

    # Update integral and derivative terms for angular error
    angular_error_integral += angular_error
    angular_error_derivative = angular_error - previous_angular_error

    # Store current errors for next iteration
    previous_linear_error = linear_error
    previous_angular_error = angular_error

    return linear_error, angular_error

# PID controller output
def pid_controller():
    linear_error, angular_error = calculate_errors()

    # Calculate linear velocity
    linear_vel = kp_linear * linear_error + ki_linear * linear_error_integral + kd_linear * linear_error_derivative

    # Calculate angular velocity
    angular_vel = kp_angular * angular_error + ki_angular * angular_error_integral + kd_angular * angular_error_derivative

    return linear_vel, angular_vel

# Main function
def main():
    rospy.init_node('turtlebot_pid_controller')

    # Subscribe to odometry topic
    rospy.Subscriber('/odom', Odometry, odom_callback)

    # Publish velocity commands
    velocity_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

    rate = rospy.Rate(10)  # 10 Hz

    while not rospy.is_shutdown():
        linear_vel, angular_vel = pid_controller()

        # Create a Twist message and publish
        twist_msg = Twist()
        twist_msg.linear.x = linear_vel
        twist_msg.angular.z = angular_vel
        velocity_publisher.publish(twist_msg)

        # Check if the goal is reached
        if sqrt((goal_x - current_x) ** 2 + (goal_y - current_y) ** 2) < 0.1:
            rospy.loginfo("Goal reached!")
            break

        rate.sleep()

    # Stop the robot
    twist_msg = Twist()
    velocity_publisher.publish(twist_msg)

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass