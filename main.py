import tkinter as tk
import threading
import imageio
import sys
from termcolor import colored
from PIL import Image, ImageTk
from time import time, sleep
import os
import tempfile
import ffmpy
import shutil
import gc

###############################################################################
# 状态参数
###############################################################################

class Global():
    def load(self, name):
        videoName = name
        fileExtension = os.path.splitext(videoName)[1].lower()
        if fileExtension != '.mp4' and fileExtension != '.mpeg':
            print(os.path.realpath(__file__))
            tempDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tempfiles')
            tempFile = os.path.join(tempDir, 'temp.mp4')
            if os.path.exists(tempDir): shutil.rmtree(tempDir)
            os.mkdir(tempDir)
            ff = ffmpy.FFmpeg(
                executable = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ffmpeg.exe'),
                inputs = { videoName : None },
                outputs = { tempFile : '-f mp4' }
            )
            ff.run()
            video = imageio.get_reader(tempFile)
        else:
            video = imageio.get_reader(videoName)
        
        meta = video.get_meta_data()
        print(meta)
        self.video = video
        self.name = name
        self.pause = False
        self.cur = 0
        self.fps = meta.get('fps')
        self.size = meta.get('source_size')
        self.duration = meta.get('duration')
        self.name = os.path.basename(videoName)
        self.step = 1
        self.speed = 1.0
        self.count = video.count_frames()
        self.zoom = 1.0
        if self.size[0] * self.size[1] > self.windowSize()[0] * self.windowSize()[1]:
            self.zoom = 2
        self.jumpRecord = ""
        self.frameTimeCost = 0
        self.prepared = 0
        
        curSize = (round(g.size[0] / g.zoom), round(g.size[1] / g.zoom))
        self.photoImages = [None for i in range(self.count)]
        
        # for i in range(self.count):
        #     self.photoImages.append(ImageTk.PhotoImage(g.frames(i).resize(curSize, Image.ANTIALIAS)))
        
        gc.collect(generation = 2)
        
        if self.count > 1000: print(colored('WARNING: video too large.', 'red'))
        
        print('Read')
        print(colored(g.name, 'green'))
        print('fps', colored(g.fps, 'yellow'))
        
    
    def frames(self, index):
        return Image.fromarray(self.video.get_data(index))
        
    
    def viewSize(self):
        return (self.view.winfo_width(), self.view.winfo_height())
    
    def windowSize(self):
        return (self.tk.winfo_width(), self.tk.winfo_height())
        
    def mousePos(self):
        return (g.tk.winfo_pointerx() - root.winfo_rootx(), g.tk.winfo_pointery() - root.winfo_rooty())
    
    def viewPos(self):
        return (self.view.winfo_x() + self.viewSize()[0] // 2, self.view.winfo_y() + self.viewSize()[1] // 2)
    
    def scaledSize(self):
        return (max(1, round(self.size[0] / self.zoom)), max(1, round(self.size[1] / self.zoom)))
    
g = Global()

###############################################################################

###############################################################################
# 运行
###############################################################################

def updateTitle():
    g.tk.title("[%03d / %03d] [%.0f%%] [step %d] [scale %.4f] %s | [time %.4f] | %s" % (
        g.cur + 1, g.count,
        g.prepared / g.count * 100,
        g.step,
        g.zoom,
        g.name,
        g.frameTimeCost,
        g.jumpRecord
    ))    

def correctSize():
    if g.scaledSize() != (g.photoImages[g.cur].width(), g.photoImages[g.cur].height()):
        g.photoImages[g.cur] = ImageTk.PhotoImage(g.frames(g.cur).resize(g.scaledSize(), Image.ANTIALIAS))
        gc.collect(generation = 1)

def prepare():
    if g.photoImages[g.cur] is None:
        g.photoImages[g.cur] = ImageTk.PhotoImage(g.frames(g.cur).resize(g.scaledSize(), Image.ANTIALIAS))
        g.prepared += 1

def setFrame():
    beginTime = time()
    prepare()
    correctSize()
    imageObject = g.photoImages[g.cur]                          # tkinter 图像组件.
    if g.viewSize() != (imageObject.width(), imageObject.height()):
        g.view.config(image = imageObject)                      # 设置组件数据信息.
    g.view.image = imageObject                                  # 贴图片.
    endTime = time()
    g.frameTimeCost = endTime - beginTime
    updateTitle()
    return g.frameTimeCost

def nextFrame():
    g.cur = g.cur + 1
    if g.cur == g.count: g.cur = 0
    setFrame()

def previousFrame():
    g.cur = g.cur - 1
    if g.cur < 0: g.cur = g.count - 1
    setFrame()

def addStep():
    g.step += 1
    updateTitle()

def decStep():
    g.step -= 1
    if g.step == 0: g.step = 1
    updateTitle()

def keyboardCallback(e):
    
    # print(e)
    
    if e.keysym.isdigit():
        g.jumpRecord += e.keysym
        updateTitle()
    
    if e.keysym == 'Return' and g.jumpRecord != "":
        jumpto = int(g.jumpRecord)
        jumpto = min(g.count - 1, max(0, jumpto))
        g.cur = jumpto
        g.pause = True
        g.jumpRecord = ""
        setFrame()
    
    if e.keysym == 'equal':
        addStep()
    
    if e.keysym == 'minus':
        decStep()
    
    if e.keysym == 'space':
        g.pause = not g.pause
    
    if e.keysym == 'Left' or e.keysym == 'a':
        g.pause = True
        for _ in range(g.step):
            previousFrame()
            
    if e.keysym == 'Right' or e.keysym == 'd' :
        g.pause = True
        for _ in range(g.step):
            nextFrame()
            
    if e.keysym == 'Up' or e.keysym == 'w':
        g.pause = True
        for _ in range(5 * g.step):
            previousFrame()
            
    if e.keysym == 'Down' or e.keysym == 's' :
        g.pause = True
        for _ in range(5 * g.step):
            nextFrame()
    
    if e.keysym == 'r':
        g.zoom = 1
        label.place(relx = 0.5, rely = 0.5, anchor = tk.CENTER)

def scrollCallback(e):
    scale = e.delta // 120
    rate = 0.9 ** scale
    g.zoom *= rate
    updateTitle()

def stream(label: tk.Canvas):
    g.load(sys.argv[1])
    
    while True:
        while g.pause : sleep(0.001)
        nextFrame()
        
        sleepTime = (1 / g.fps - g.frameTimeCost) / g.speed
        if sleepTime > 0: sleep(sleepTime)
        # else: print('Warning: fps not full. frame %d time %.4f' % (g.cur, g.frameTimeCost))

def clickCallback(e):
    g.fromPoint = g.viewPos()
    g.mouseFromPoint = g.mousePos()

def moveCallback(e):
    g.mouseToPoint = g.mousePos()
    dir = (g.mouseToPoint[0] - g.mouseFromPoint[0], g.mouseToPoint[1] - g.mouseFromPoint[1])
    targetPos = (g.fromPoint[0] + dir[0], g.fromPoint[1] + dir[1])
    g.view.place(relx = targetPos[0] / g.windowSize()[0], rely = targetPos[1] / g.windowSize()[1], anchor = tk.CENTER)

if __name__ == "__main__":
    root = tk.Tk()
    root.config(width = 1280, height = 800)
    
    label = tk.Label(root)
    label.place(relx = 0.5, rely = 0.5, anchor = tk.CENTER)
    
    thread = threading.Thread(target = stream, args = (label,))
    thread.daemon = 1
    thread.start()
    
    g.tk = root
    g.view = label
    
    root.bind('<Key>', keyboardCallback)
    root.bind("<MouseWheel>", scrollCallback)
    root.bind("<Button-1>", clickCallback)
    root.bind("<B1-Motion>", moveCallback)
    root.mainloop()
