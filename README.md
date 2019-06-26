# Laser-Tracking-System
Laser tracking system based on motion detection 
https://youtu.be/veeBLcLZFfc

###### image will be edited soon..

## Introduction

In part of autonomous robotics course in university we had to arrange final project with connection to autonomous machine.
We thought about doing laser tracking on specific faces in order to build some "killing machine" that identify target (our vision was terrorists/wanted people) and shoot towards it accurately bullet.
Of course we couldn't build such a machine (real shooting) so we do it with laser beam, our targets would be motion detected so every movement captured in camera will get the laser beam.

 
## Equipment

With a relatively small budget we achieved a good product.

###### Raspberry pie 3B
 





 
###### Camera
 


###### Laser 

###### Servos
 

###### Laser mounted on the 2-axis servos
 


## Connections to raspberry pie

The pie comes with only 2 – 5V ports and 2 – 3v3 ports.
 

We can see that only 2 and 4 ports are available for 5V input
But we have 3 devices using the 5V:
1)	Laser, 
2)	Horizontal servo
3)	Vertical servo

So we had to plug in 2 wires of the 5V into 1 pin and the one remaining to the second 5V pin:
 

(At first, we tried to plug our laser to a 3v3 pin but the beam strength was very weak. The same case happened with the servo when plugged to the 3v3 pin)















Our pie final connections would seem like this:
 

 
Model Architecture

First we need to locate the camera in the closest place from the laser
which will give us the best precision.

With our cheap budget we manage to improvise the following structure:
 
 

