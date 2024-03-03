#!/usr/bin/python
#2427724
import rospy
from std_msgs.msg import Empty
from geometry_msgs.msg import Twist

class DroneController:
    def __init__(self):
        rospy.init_node('drone_controller', anonymous=True)
        self.takeoff_pub = rospy.Publisher('/ardrone/takeoff', Empty, queue_size=1)
        self.land_pub = rospy.Publisher('/ardrone/land', Empty, queue_size=1)
        self.cmd_vel_pub=rospy.Publisher('/cmd_vel',Twist,queue_size=1)
        rospy.sleep(1)  

    def takeoff(self):
        rospy.loginfo("Taking off...")
        self.takeoff_pub.publish(Empty())

    def land(self):
        rospy.loginfo("Landing...")
        self.land_pub.publish(Empty())
    def move(self,linear_x=0.0, linear_y=0.0, linear_z=0.0, angular_z=0.0):
        rospy.loginfo("Moving: linear_x={}, linear_y={}, linear_z={}, angular_z={}".format(linear_x, linear_y, linear_z, angular_z))
        twist_msg = Twist()
        twist_msg.linear.x = linear_x
        twist_msg.linear.y = linear_y
        twist_msg.linear.z = linear_z
        twist_msg.angular.z = angular_z
        self.cmd_vel_pub.publish(twist_msg)  

if __name__ == '__main__':
    try:
        controller = DroneController()
        rospy.sleep(1)  
        controller.takeoff()
        rospy.sleep(5) 
        controller.move(linear_x=0.5)
        rospy.sleep(3) 
        controller.move()
        rospy.sleep(2)
        controller.land()
    except rospy.ROSInterruptException:
        pass