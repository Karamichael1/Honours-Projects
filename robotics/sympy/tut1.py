import sympy as sym
from sympy import cos,sin,pi
theta=sym.Symbol("theta")
x=sym.Symbol("x")
y=sym.Symbol("y")
z=sym.Symbol("z")


#Q1 matrix
m=sym.Matrix(
    [
        [cos(theta),-sin(theta),x],
        [sin(theta),+cos(theta),y],
            [0,0,1]
    ]
)
#Q1.1
p=sym.Matrix([
    [3],
    [2],
    [1]
])

#ans=m.subs(theta, 30* pi/180).subs(x,0).subs(y,0)
#sym.pprint(sym.N(ans*p))

#Q1.2
ans2=m.subs(theta,45*pi/180).subs(x,2).subs(y,9)
#sym.pprint(sym.N(ans2*p))

#Q1.3
val=sym.Matrix([
    [3],
    [3],
    [1]
])


T1_2=m.subs(theta,-30*pi/180).subs(x,2).subs(y,9)
T0_1=m.subs(theta,90*pi/180).subs(x,3).subs(y,4)

#sym.pprint(sym.N(T0_1*T1_2*val))

#Q2 setup

x_axis=sym.Matrix([
    [1,0,0,x],
    [0,cos(theta),-sin(theta),y],
    [0,sin(theta),cos(theta),z],
    [0,0,0,1]
])
y_axis=sym.Matrix([
    [cos(theta),0,sin(theta),x],
    [0,1,0,y],
    [-sin(theta),0,cos(theta),z] ,
    [0,0,0,1]
])
z_axis=sym.Matrix([
    [cos(theta),-sin(theta),0,x],
    [sin(theta),cos(theta),0,y],
    [0,0,1,z],
    [0,0,0,1]
])

#Q2.1
fi=z_axis.subs(theta,"f").subs(x,0).subs(y,0).subs(z,"l1")
sym.pprint(sym.N(fi))

#Q2.2
values=sym.Matrix([
    [3],
    [2],
    [3],
    [1]
])
#fi=z_axis.subs(theta,30*pi/180).subs(x,0).subs(y,0).subs(z,5)
#sym.pprint(sym.N(fi*values))

#Q2.3
axis=x_axis.subs(theta,"D").subs(x,0).subs(y,"l2").subs(z,0)
#sym.pprint(fi*axis)

#Q2.4

place=sym.Matrix([
    [2],
    [2],
    [2],
    [1]
])
#sym.pprint(fi*axis*place)