import sympy as sym
from sympy import cos,sin,pi
theta=sym.Symbol("theta")
theta1=sym.Symbol("theta1")
theta2=sym.Symbol("theta2")
x=sym.Symbol("x")
y=sym.Symbol("y")
z=sym.Symbol("z")
d=sym.Symbol("d")
d1=sym.Symbol("d1")
d2=sym.Symbol("d2")
a=sym.Symbol("a")
a1=sym.Symbol("a1")
a2=sym.Symbol("a2")
alpha=sym.Symbol("alpha")
q3=sym.Symbol("q3")
x_rot=sym.Matrix([
    [1,0,0,0],
    [0,cos(alpha),-sin(alpha),0],
    [0,sin(alpha),cos(alpha),0],
    [0,0,0,1]
])
z_rot=sym.Matrix([
    
    [cos(theta),-sin(theta),0,0],
    [sin(theta),cos(theta),0,0],
    [0,0,1,0],
    [0,0,0,1]
])

z_trans=sym.Matrix([
    [1,0,0,0],
    [0,1,0,0],
    [0,0,1,d],
    [0,0,0,1]
])

x_trans=sym.Matrix([
    [1,0,0,a],
    [0,1,0,0],
    [0,0,1,0],
    [0,0,0,1]
])

#Q1
#dh1
#a1=0
#alf1=90
#d1=d1
#the1=10
#dh2
#a2=0
#alf2=-90
#d2=d2
#the2=-30
#dh3
#a3=0
#alf3=0
#d3=0.5+d
#the4=0

ans=z_rot*z_trans*x_trans*x_rot

T0_1 = ans.subs(a, 0).subs(alpha, pi/2).subs(d,d1).subs(theta, 0 + 10*pi/180)
T1_2 = ans.subs(a, 0).subs(alpha, -pi/2).subs(d,d2).subs(theta, -30*pi/180)
T2_3 = ans.subs(a, 0).subs(alpha, 0).subs(d,0.5).subs(theta, 0)
#sym.pprint(sym.N(T0_1))
#sym.pprint(sym.N(T0_1*T1_2*T2_3))

#Q2
jw=sym.Matrix([
    [0,0,0],
    [0,0,0],
    [1,1,0]

])

id=sym.Matrix([
    [0],
    [0],
    [1],
    
])
jv=sym.Matrix([
    [a1 *cos(theta1) + a2*cos(theta1 +theta2)],
    [a1*sin(theta1) +a2*sin(theta1 +theta2)],
    [q3 +5]
])
jv2Minus=sym.Matrix([
    [a1*cos(theta1)],
    [a1*sin(theta1)],
    [d1]
])
jv1=id.cross(jv)
sym.pprint(jv1)
jv2=id.cross(jv1-jv2Minus)
sym.pprint(jv2)