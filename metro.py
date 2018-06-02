#!/usr/bin/env python3
#
# Generates a gif image comparing Montreal metro map to its real geography.
# Based on Reddit post "Berlin Subway Map compared to it's real geography"
# https://www.reddit.com/r/dataisbeautiful/comments/6baefh/berlin_subway_map_compared_to_its_real_geography/
#
# Project at https://github.com/will8211/montreal
#
# Shared at https://www.reddit.com/r/dataisbeautiful/comments/6c8ukp/montreal_metro_map_distances_vs_geographic/
# and http://imgur.com/a/TuRT8
#
# Depends on pycairo and imageio modules
# Also depends on gifsicle
# Font ('Falling Sky') available at http://www.fontspace.com/kineticplasma-fonts/falling-sky
#
# ~WM

import glob
import os
import subprocess as sp

import cairo
import imageio as io

FRAME_COUNT = 50
FRAME_DURATION = 0.02

MOD_START_X = -38
MOD_START_Y =  71 -35
MOD_END_X =     0
MOD_END_Y =     0 -35

# Station coordinates (start_x, start_y, node_type, end_x, end_y)
# Node types: 0 -> Regular station (small dot)
#             1 -> Transfer station (big dot)
#             2 -> Bend in the tracks, no station
#            -1 -> Bend only in geographical map

yellow = ((290, 293, 2, 252, 364),
          (308, 293, 2, 260, 389),
          (320, 310, 2, 277, 401),
          (335, 310, 0, 297, 404),
          (343, 310, 2, 330, 395),
          (367, 297, 1, 338, 385))

orange = (( 73, 262, 1,  35, 224),
          ( 83, 275, 0,  41, 248),
          ( 92, 288, 0,  49, 285),
          (101, 300, 0,  56, 309),
          (110, 313, 0,  80, 323),
          (119, 325, 0,  86, 337),
          (129, 338, 1,  86, 357),
          (142, 356, 0,  88, 383),
          (156, 374, 0, 108, 418),
          (169, 391, 0, 144, 430),
          (181, 407, 2, 154, 427),
          (192, 400, 1, 163, 424),
          (208, 388, 0, 181, 412),
          (226, 375, 0, 199, 404),
          (244, 362, 0, 213, 400),
          (261, 349, 0, 226, 396),
          (279, 335, 0, 239, 389),
          (296, 322, 0, 252, 383),
          (306, 315, 2, 258, 377),
          (290, 293, 1, 252, 364), 
          (273, 270, 0, 244, 346),
          (262, 256, 0, 232, 317),
          (251, 242, 0, 226, 301),
          (240, 228, 0, 215, 280),
          (230, 214, 0, 207, 262),
          (219, 199, 1, 197, 241), 
          (206, 183.5, 0, 180, 216),
          (195.5, 168.5, 0, 165, 194), 
          (185, 154.5, 0, 143, 163), 
          (173.5, 139.5, 0, 130, 142), 
          (148, 107, 0, 113, 110),
          (141,  98, 2, 101, 97),
          (103,  98, 0,  65,  76),
          ( 62,  98, 1,  39,  66))

green =  ((133, 473, 1, 61, 488),
          (140, 467, -1, 75, 485),
          (147, 462, 0, 87, 487),
          (155, 457, -1, 113, 492),
          (163, 452, 0, 118, 487),
          (165, 450, 2, 126, 483),
          (176, 462, 2, 126, 483),
          (179, 458.5, 0, 138, 491),
          (187, 453, -1, 147, 497),
          (195, 448, 0, 154, 490),
          (207, 438.5, 0, 170, 469),
          (216, 432, 2, 178, 458),
          (205, 418, 0, 176, 447),
          (192, 400, 1, 163, 424),
          (182, 387,-1, 153, 420),
          (176, 378, 2, 152, 407),
          (188, 369, 0, 163, 399),
          (206, 356, 0, 185, 393),
          (224, 343, 0, 204, 384),
          (241, 330, 0, 215, 380),
          (259, 316, 0, 227, 374),
          (276, 303, 0, 240, 369),
          (290, 293, 1, 252, 364),
          (309, 278, 0, 265, 358),
          (322, 268, 0, 281, 351),
          (327, 264, 2, 302, 340),
          (319, 253, 0, 299, 330),
          (314, 247, 2, 295, 317),
          (325, 239, 0, 310, 305),
          (337.5, 230, 0, 321, 297),
          (350, 221, 0, 334, 277),
          (362, 211, 0, 352, 266),
          (369, 206, 2, 365, 253),
          (360, 195, 0, 366, 244),
          (354, 187, 2, 367, 235),
          (364.5, 179.5, 0, 380, 226),
          (377, 170, 0, 396, 215),
          (389, 161, 0, 413, 204),
          (402, 151, 1, 432, 190))

blue =   ((129, 338, 1,  86, 357),
          (151, 320, 0, 109, 338),
          (172, 303, 0, 132, 328),
          (193, 287, 0, 151, 317),
          (209, 275, 2, 165, 305),
          (201, 265, 0, 166, 290),
          (183, 242, 0, 155, 270),
          (175, 233, 2, 156, 261),
          (186, 224, 0, 165, 252),
          (202, 212, 0, 181, 244),
          (219, 199, 1, 197, 241),
          (236, 186, 0, 222, 229),
          (251, 175, 0, 242, 220),
          (264, 165, 1, 257, 207))

metro_lines = ((yellow, 1.000, 0.831, 0.000),
              (orange, 0.929, 0.498, 0.000),
              (green, 0.000, 0.561, 0.212),
              (blue, 0.000, 0.486, 0.757))

frames_list = []
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 460, 540)
ctx = cairo.Context(surface)

#############
# Functions #
#############

def smoothstep(a, b, value):
    '''
    Based on javascript code found at <https://github.com/gre/smoothstep>
    Takes a start time (a), and end time (b), and the current time (value),
    and return what proportion (between 0 and 1.0) of the distance it should
    currently be at, using a smooth s-curve for displacement. Used by the 
    transform() function.
    
    NOT USED: Swtiched to smootherstep()
    '''
    x = max(0, min(1, (value - a) / (b - a)))
    return x**2 * (3 - 2*x)

def smootherstep(a, b, value):
    '''
    A smoother version of smoothstep()
    https://en.wikipedia.org/wiki/Smoothstep#Variations
    '''
    x = max(0, min(1, (value - a) / (b - a)))
    return x**3 * (x * (x*6 - 15) + 10)

def transform(start, end, current_frame):
    '''
    Takes the starting and ending states of a value (an x or y coordinate or
    a size) and determines what that value should be at the current frame.
    '''
    #multiplier = current_frame / (FRAME_COUNT - 1) # Flat velocity
    multiplier = smootherstep(0, FRAME_COUNT, current_frame)
    return start + multiplier * (end - start)


###################################
# Draw metro lines for each frame #
###################################

for frame in range(FRAME_COUNT):

    # Background

    ctx.set_source_rgb(1.000, 1.000, 1.000) # white
    ctx.rectangle(0, 0, 460, 540)
    ctx.fill()

    # Text

    ctx.select_font_face('Falling Sky', 
                         cairo.FONT_SLANT_NORMAL, 
                         cairo.FONT_WEIGHT_BOLD)

    ctx.set_font_size(38)
    ctx.move_to(250, 90)
    ctx.set_source_rgb(0.000, 0.000, 0.000) # black
    ctx.show_text('Montreal')

    for metro_line, r, g, b in metro_lines:

        # Draw tracks

        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgb(r, g, b)
        
        line_width = transform(13, 4, frame)
        ctx.set_line_width(line_width)

        for i, coord in enumerate(metro_line):

            x = transform(coord[0] + MOD_START_X, coord[3] + MOD_END_X, frame) 
            y = transform(coord[1] + MOD_START_Y, coord[4] + MOD_END_Y, frame)
            
            if i == 0:
                ctx.move_to(x, y)
            
            # for frame 0, skip actual stations, following only track bends
            # this makes the lines straighter
            if frame > 0 or coord[2] > 0: 
                ctx.line_to(x, y)

        ctx.stroke()

        # Draw stations

        ctx.set_source_rgb(1.000, 1.000, 1.000)
        
        for coord in metro_line:

            x = transform(coord[0] + MOD_START_X, coord[3] + MOD_END_X, frame) 
            y = transform(coord[1] + MOD_START_Y, coord[4] + MOD_END_Y, frame)

            ctx.move_to(x, y)

            big_dot = transform(11, 3, frame)
            small_dot = transform(6, 3, frame)
        
            if coord[2] == 0:
                ctx.set_line_width(small_dot)
                ctx.line_to(x, y)

            elif coord[2] == 1:
                ctx.set_line_width(big_dot)
                ctx.line_to(x, y)

            ctx.stroke() 

    # Write frame to file

    frame_name = 'frame_%d.png' % frame
    surface.write_to_png(frame_name)
    frames_list.append(frame_name)


################
# Generate gif #
################

images = []
for filename in frames_list:
    images.append(io.imread(filename))

io.imwrite('part_1.gif', images[0], duration = 5.00)
io.mimwrite('part_2.gif', images, duration = FRAME_DURATION)
io.imwrite('part_3.gif', images[-1], duration = 5.00)

# To transition back to the start
io.mimwrite('part_4.gif', reversed(images), duration = FRAME_DURATION)

for f in glob.glob('frame_*.png'):
    os.remove(f)

result = sp.run(['gifsicle', '--colors', '256', 
                 'part_1.gif', 'part_2.gif', 'part_3.gif', 'part_4.gif'],
                 stdout=sp.PIPE)

with open('Montreal.gif', 'wb') as f:
    f.write(result.stdout)

for f in glob.glob('part_*.gif'):
    os.remove(f)

sp.call(['xdg-open', 'Montreal.gif'])
