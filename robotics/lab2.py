#!/usr/bin/python
#2427724
import rospy
from std_msgs.msg import Empty
from geometry_msgs.msg import Twist
from gazebo_msgs.srv import GetModelState
import tf.transformations as tf_trans

class DroneController:
    def __init__(self):
        rospy.init_node('drone_controller', anonymous=True)
        self.takeoff_pub = rospy.Publisher('/ardrone/takeoff', Empty, queue_size=1)
        self.land_pub = rospy.Publisher('/ardrone/land', Empty, queue_size=1)
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.get_model_state = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
        rospy.sleep(1)

    def takeoff(self):
        rospy.loginfo("Taking off...")
        self.takeoff_pub.publish(Empty())

    def land(self):
        rospy.loginfo("Landing...")
        self.land_pub.publish(Empty())

    def move(self, target_x=0.0, target_y=0.0, target_z=0.0, Kp=1.0, Ki=0.0, Kd=0.0):
        rospy.loginfo("Moving to: target_x={}, target_y={}, target_z={}".format(target_x, target_y, target_z))

        # PID control parameters
        prev_error_x = 0.0
        prev_error_y = 0.0
        prev_error_z = 0.0
        integral_x = 0.0
        integral_y = 0.0
        integral_z = 0.0

        rate = rospy.Rate(10)  # 10Hz
        while not rospy.is_shutdown():
            # Get current position and orientation
            current_state = self.get_model_state("drone", "")
            current_x = current_state.pose.position.x
            current_y = current_state.pose.position.y
            current_z = current_state.pose.position.z
            orientation = current_state.pose.orientation
            # Convert orientation to Euler angles
            (roll, pitch, yaw) = tf_trans.euler_from_quaternion([orientation.x, orientation.y, orientation.z, orientation.w])

            # Calculate errors
            error_x = target_x - current_x
            error_y = target_y - current_y
            error_z = target_z - current_z

            # Transform errors to body frame
            error_x_bf = error_x * tf_trans.cos(yaw) + error_y * tf_trans.sin(yaw)
            error_y_bf = -error_x * tf_trans.sin(yaw) + error_y * tf_trans.cos(yaw)

            # Calculate integral terms
            integral_x += error_x_bf
            integral_y += error_y_bf
            integral_z += error_z

            # Calculate derivative terms
            derivative_x = error_x_bf - prev_error_x
            derivative_y = error_y_bf - prev_error_y
            derivative_z = error_z - prev_error_z

            # PID control
            linear_x = Kp * error_x_bf + Ki * integral_x + Kd * derivative_x
            linear_y = Kp * error_y_bf + Ki * integral_y + Kd * derivative_y
            linear_z = Kp * error_z + Ki * integral_z + Kd * derivative_z

            # Publish control command
            twist_msg = Twist()
            twist_msg.linear.x = linear_x
            twist_msg.linear.y = linear_y
            twist_msg.linear.z = linear_z
            self.cmd_vel_pub.publish(twist_msg)

            # Update previous errors for next iteration
            prev_error_x = error_x_bf
            prev_error_y = error_y_bf
            prev_error_z = error_z

            # Check if close enough to target, then stop
            if abs(error_x) < 0.1 and abs(error_y) < 0.1 and abs(error_z) < 0.1:
                rospy.loginfo("Reached target position")
                break

            rate.sleep()


if __name__ == '__main__':
    try:
        controller = DroneController()
        rospy.sleep(1)
        controller.takeoff()
        rospy.sleep(5)
        # Supply coordinates for the drone to fly to
        target_x = 1.0
        target_y = 2.0
        target_z = 3.0
        # Apply PID control
        controller.move(target_x, target_y, target_z)
        rospy.sleep(2)
        controller.land()
    except rospy.ROSInterruptException:
        pass
