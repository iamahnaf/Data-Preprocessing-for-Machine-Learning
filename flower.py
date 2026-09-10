"""Animated sunflower that blooms on your screen — built with Python's turtle.

No external libraries needed. Run it, then click the window to close.
"""

import turtle

# --- screen setup -----------------------------------------------------------
screen = turtle.Screen()
screen.bgcolor("skyblue")
screen.title("Animated Sunflower 🌻")
screen.tracer(0)  # draw everything smoothly instead of frame-by-frame

t = turtle.Turtle()
t.speed(0)
t.hideturtle()


def petal(r, color):
    """Draw one petal as a filled rounded shape."""
    t.color(color)
    t.begin_fill()
    t.circle(r, 60)   # curve up
    t.left(120)
    t.circle(r, 60)   # curve back
    t.left(120)
    t.end_fill()


def leaf(size):
    """Draw a single leaf facing right."""
    t.color("forestgreen")
    t.begin_fill()
    t.circle(size, 90)
    t.left(180)
    t.circle(size, 90)
    t.end_fill()


def sun():
    t.penup()
    t.goto(-260, 190)
    t.pendown()
    t.color("gold")
    t.begin_fill()
    for _ in range(8):
        t.forward(14)
        t.backward(14)
        t.right(45)
        t.forward(14)
        t.backward(14)
        t.right(45)
    t.color("goldenrod")
    t.begin_fill()
    t.up()
    t.forward(20)
    t.down()
    t.circle(20, 360)
    t.end_fill()


def draw_cloud(x, y):
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.color("white")
    for _ in range(3):
        t.begin_fill()
        t.circle(16)
        t.end_fill()
        t.forward(22)
    t.end_fill()


def stem():
    """Draw the green stem growing upward."""
    t.color("seagreen")
    t.pensize(6)
    t.penup()
    t.goto(0, -220)
    t.setheading(90)
    t.pendown()
    t.forward(180)

    # a leaf on the way up
    t.setheading(45)
    leaf(22)

    # back to stem tip
    t.penup()
    t.goto(0, -40)
    t.setheading(90)
    t.pendown()


def bloom():
    """Draw the flower head that 'pops' open with all petals."""
    for i, color in enumerate(["#ff8c00", "#ffa500", "#ffb347"]):
        t.penup()
        t.goto(0, -40)
        t.pendown()
        t.setheading(90 + i * 60 + i * 15)
        for _ in range(6):
            petal(58, color)
            t.right(60)
        screen.update()
        turtle.time.sleep(0.15)


def face():
    """Draw the flower's happy center."""
    t.penup()
    t.goto(0, -58)
    t.pendown()
    t.color("#8b4513")
    t.begin_fill()
    t.circle(30)
    t.end_fill()

    t.color("#5c3317")
    t.pensize(4)
    # eyes
    t.penup()
    t.goto(-11, -40)
    t.dot(7, "#fff")
    t.goto(11, -40)
    t.dot(7, "#fff")
    t.goto(-12, -41)
    t.dot(4, "#000")
    t.goto(10, -41)
    t.dot(4, "#000")
    # smile
    t.penup()
    t.goto(-13, -58)
    t.pendown()
    t.setheading(-60)
    t.circle(14, 120)


def sparkles():
    """Add a few twinkles so it feels alive."""
    t.color("#fff")
    t.penup()
    for x, y in [(-120, 120), (90, 160), (150, 40), (-160, 10)]:
        t.goto(x, y)
        t.down()
        for _ in range(4):
            t.forward(7)
            t.backward(7)
            t.left(90)
        t.up()


sun()
draw_cloud(-150, 180)
draw_cloud(60, 220)
draw_cloud(170, 150)
stem()
bloom()
face()
sparkles()

t.color("dodgerblue")
t.penup()
t.goto(0, -290)
t.pendown()
t.write("Have a blooming day!  🌻",
        align="center", font=("Comic Sans MS", 18, "bold"))

screen.update()
screen.exitonclick()