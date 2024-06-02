from tkinter import *
import cv2
from PIL import ImageTk, Image
import mediapipe as mp
import random

####################################
# customize these functions
####################################

class PoseDetector():
    def __init__(self):
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(static_image_mode=False, min_detection_confidence=0.9, min_tracking_confidence=0.9)

    def findPts(self, img):
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(rgb)

        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])

        pts = []
        displm = [0, 19, 20, 31, 32]
        for lm in displm:
            if(lm < len(self.lmList)):
                pts.append([self.lmList[lm][1], self.lmList[lm][2]])

        return pts

def set_frame(data, initial=False):
    if(initial):
        data.cap = cv2.VideoCapture(0)

    _, data.img = data.cap.read()
    data.img = cv2.flip(data.img, 1)
    data.rgb = cv2.cvtColor(data.img, cv2.COLOR_BGR2RGB)
    data.imtk = ImageTk.PhotoImage(image=Image.fromarray(data.rgb))

def getLevel(w, h, numPts):
    pts = []
    for i in range(numPts):
        x = random.randrange(int(w*0.3), int(w*0.7))
        y = random.randrange(int(h*0.2), int(h*0.8))
        pts.append([x, y])

    connections = []
    for i in range(numPts):
        if(i == numPts - 1):
            connections.append([i, 0])
        else:
            connections.append([i, i + 1])

    return pts, connections

def drawLevel(data, canvas):
    for i in range(len(data.connections)):
        conn = data.connections[i]
        if data.colors[conn[0]] == "green" or data.colors[conn[1]] == "green":
            canvas.create_line(data.pts[conn[0]], data.pts[conn[1]], width = 5, fill = '#32a852')
        else:
            canvas.create_line(data.pts[conn[0]], data.pts[conn[1]], width = 5, fill = 'red')

    for i in range(len(data.pts)):
        conn = data.connections[i]
        if data.colors[i] == "green":
            canvas.create_oval(data.pts[conn[0]][0] - 25, data.pts[conn[0]][1] - 25, data.pts[conn[0]][0] + 25, data.pts[conn[0]][1] + 25, fill = '#9cffb5', width = 5, outline = '#32a852')
        if data.colors[i] == "red":
            canvas.create_oval(data.pts[conn[0]][0] - 25, data.pts[conn[0]][1] - 25, data.pts[conn[0]][0] + 25, data.pts[conn[0]][1] + 25, fill = '#ff9c9c', width = 5, outline = 'red')

def round_rectangle(canvas, x1, y1, x2, y2, color, outl, r=25):
    points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
    return canvas.create_polygon(points, fill = color, outline = outl, width = 15, smooth=True)

def init(data):
    # load data.xyz as appropriate
    data.w = 1280
    data.h = 720

    set_frame(data, initial=True)
    data.pose = PoseDetector()
    data.lm = data.pose.findPts(data.rgb)
    data.firstTime = True
    data.start = False
    data.startBox = [800, data.h/2 - 160, 1250, data.h/2 + 160]
    data.skipBox = [1050, 150, 1250, 200]
    data.boxCol = "blue"
    data.skip = False
    data.pts, data.connections = getLevel(data.w, data.h, random.randrange(2, 5))
    data.colors = ["red" for i in range(len(data.pts))]
    #timer is 30, it just gets cut back immediately
    data.timer = 30
    data.secondCount = 1
    data.score = 0
    data.hover = False
    
def mousePressed(event, data):
    # use event.x and event.y
    pass

def keyPressed(event, data):
    # use event.char and event.keysym
    pass

def timerFired(data):
    set_frame(data, initial=False)
    data.lm = data.pose.findPts(data.rgb)

    if data.start:
        if data.timer <= 0:
            data.start = False
            data.boxCol = "blue"
            data.firstTime = False
            data.timer = 30
            data.hover = True
        elif data.secondCount >= 8:
            data.secondCount = 1
            data.timer -= 1
        else:
            data.secondCount += 1
    # if(len(data.lm) >= 1 and data.startBox[0] < data.lm[1][0] < data.startBox[2] and data.startBox[1] < data.lm[1][1] < data.startBox[3]):
    #     #if skip
    #     if(data.start and not data.skip):
    #         data.pts, data.connections = getLevel(data.w, data.h, random.randrange(2, 5))
    #         data.colors = ["red" for i in range(len(data.pts))]
    #         data.skip = True
    #     #start game
    #     else:
    #         data.start = True
    #         data.skip = True
    # else:
    #     if(data.start):
    #         data.skip = False
    if(len(data.lm) >= 1 and data.startBox[0] < data.lm[1][0] < data.startBox[2] and data.startBox[1] < data.lm[1][1] < data.startBox[3]):
        #start
        if not data.hover:
            if not data.start:
                data.score = 0
                data.start = True
    #skipBox
    elif(len(data.lm) >= 1 and data.skipBox[0] < data.lm[1][0] < data.skipBox[2] and data.skipBox[1] < data.lm[1][1] < data.skipBox[3]):
        data.hover = False
        #if skip
        data.boxCol = "green"
        if(data.start and not data.skip):
            data.pts, data.connections = getLevel(data.w, data.h, random.randrange(2, 5))
            data.colors = ["red" for i in range(len(data.pts))]

            data.skip = True
    else:
        data.hover = False
        data.boxCol = "blue"
        if(data.start):

            data.skip = False

    for i in range(len(data.pts)):
        pt = data.pts[i]
        for lm in data.lm:
            if(pt[0] - 25 < lm[0] < pt[0] + 25 and pt[1] - 25 < lm[1] < pt[1] + 25):
                data.colors[i] = "green"
                break
            else:
                data.colors[i] = "red"

    won = True
    filled = [False for i in range(len(data.pts))]
    for i in range(len(data.pts)):
        pt = data.pts[i]
        for lm in data.lm:
            if(pt[0] - 25 < lm[0] < pt[0] + 25 and pt[1] - 25 < lm[1] < pt[1] + 25):
                filled[i] = True

    for i in range(len(filled)):
        if(not filled[i]):
            won = False

    if(won):
        # sets the new points
        data.score += len(data.pts)
        data.pts, data.connections = getLevel(data.w, data.h, random.randrange(2, 5))
        data.colors = ["red" for i in range(len(data.pts))]


def redrawAll(canvas, data):
    # draw in canvas
    canvas.create_image(0, 0, anchor=NW, image=data.imtk)

    if(data.start):
        drawLevel(data, canvas)
        #score
        round_rectangle(canvas, 50, 25, 250, 175, "#ededed", "#e3e3e3")
        canvas.create_text(150, 100, text = data.score, font = "Avenir 100", fill="#3d6287")
        #timer
        round_rectangle(canvas, 1050, 25, 1250, 175, "#ededed", "#e3e3e3")
        canvas.create_text(1150, 100, text = data.timer, font = "Avenir 100", fill="#3d6287")

        if data.boxCol == "blue":
            round_rectangle(canvas, data.skipBox[0], data.skipBox[1], data.skipBox[2], data.skipBox[3], "#a1eded", '#8ad9db')
        else:
            round_rectangle(canvas, data.skipBox[0], data.skipBox[1], data.skipBox[2], data.skipBox[3], '#9cffb5', '#32a852')
        canvas.create_text((data.skipBox[0] + data.skipBox[2])/2, (data.skipBox[1] + data.skipBox[3])/2, text="Skip Level", font = "Avenir 35")

        for pt in data.lm:
            canvas.create_oval(pt[0] - 20, pt[1] - 20, pt[0] + 20, pt[1] + 20, fill = '#11a0ed', width = 0)
    else:
        #Light blue #338ee8 dark blue #3d6287 sky blue #a1eded
        #canvas.create_rectangle(0, 0, 1280, 720, fill = "#3d6287")
        #draw the button
        if data.boxCol == "blue":
            round_rectangle(canvas, data.startBox[0], data.startBox[1], data.startBox[2], data.startBox[3], "#a1eded", '#8ad9db')
        else:
            round_rectangle(canvas, data.startBox[0], data.startBox[1], data.startBox[2], data.startBox[3], '#9cffb5', '#32a852')
        #draw rh circle
        if(len(data.lm) > 1):
            canvas.create_oval(data.lm[1][0] - 20, data.lm[1][1] - 20, data.lm[1][0] + 20, data.lm[1][1] + 20, fill = '#11a0ed', width = 0)
        #round_rectangle(canvas, 50, 140, 500, 250, "#338ee8", "#2c82de")
        canvas.create_text(275, 200, text = "MotiLens", font = "Avenir 100", fill="#ffffff")
        round_rectangle(canvas, 50, 285, 500, data.startBox[3], "#ededed", "#e3e3e3")
        #how to play
        if data.firstTime:
            canvas.create_text(275, 320, text = "How to Play", font = "Avenir 30", fill="#3d6287")
            canvas.create_text(275, 350, text = "Use your head, hands, and feet", font = "Avenir 27", fill="#338ee8")
            canvas.create_text(275, 380, text = "to match the pattern shown. Get", font = "Avenir 27", fill="#338ee8")
            canvas.create_text(275, 410, text = "as many puzzles as you can in", font = "Avenir 27", fill="#338ee8")
            canvas.create_text(275, 440, text = "the time limit! If a puzzle is", font = "Avenir 27", fill="#338ee8")
            canvas.create_text(275, 470, text = "too hard, there is a skip button.", font = "Avenir 27", fill="#338ee8")
            canvas.create_text(275, 500, text = "1 dot puzzles are 1 point, 2 dot puzzles are 2 points, etc.", font = "Avenir 17", fill="#919191")
            canvas.create_text((data.startBox[0] + data.startBox[2])/2, (data.startBox[1] + data.startBox[3])/2, text="Start Game", font = "Avenir 80", fill="#345780")
        else:
            canvas.create_text(275, 360, text = "Final Score:", font = "Avenir 60", fill = "#3d6287")
            canvas.create_text(275, 440, text = data.score, font = "Avenir 80", fill = "#3d6287")
            canvas.create_text((data.startBox[0] + data.startBox[2])/2, (data.startBox[1] + data.startBox[3])/2, text="Try Again?", font = "Avenir 80", fill="#345780")
        canvas.create_rectangle(50, 260, 500, 265, fill="#3d6287", outline="#345780", width=10)

        canvas.create_text((data.startBox[0] + data.startBox[2])/2, (data.startBox[1] + data.startBox[3])/2 + 200, text="Hover your right hand over the button to begin", font = "Avenir 20", fill = "black")
####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 0 # milliseconds
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1280, 720)
