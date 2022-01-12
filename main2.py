# -*- coding: utf-8 -*-
# Advanced zoom example. Like in Google Maps.
# It zooms only a tile, but not the whole image. So the zoomed tile occupies
# constant memory and not crams it with a huge resized image for the large zooms.
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class AutoScrollbar(ttk.Scrollbar):
    ''' A scrollbar that hides itself if it's not needed.
        Works only if you use the grid geometry manager '''
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')

class Zoom_Advanced(ttk.Frame):
    ''' Advanced zoom of the image '''
    def __init__(self, mainframe, path, test):
        ''' Initialize the main Frame '''
        ttk.Frame.__init__(self, master=mainframe)
        self.master.title('Zoom with mouse wheel')
        print(test)
        # Vertical and horizontal scrollbars for canvas
        vbar = AutoScrollbar(self.master, orient='vertical')
        hbar = AutoScrollbar(self.master, orient='horizontal')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='we')
        # Create canvas and put image on it
        self.canvas = tk.Canvas(self.master, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.canvas.update()  # wait till canvas is created
        vbar.configure(command=self.scroll_y)  # bind scrollbars to the canvas
        hbar.configure(command=self.scroll_x)
        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind('<ButtonPress-1>', self.move_from)
        self.canvas.bind('<B1-Motion>',     self.move_to)
        self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>',   self.wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>',   self.wheel)  # only with Linux, wheel scroll up
        self.image = Image.open(path)  # open image
        self.width, self.height = self.image.size

        #for later...to make it fit more stuff
        #self.width, self.height = (1000000, 10000000)


        self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)
        # Plot some optional random rectangles for the test purposes
        minsize, maxsize, number = 5, 20, 10
        for n in range(number):
            x0 = random.randint(0, self.width - maxsize)
            y0 = random.randint(0, self.height - maxsize)
            x1 = x0 + random.randint(minsize, maxsize)
            y1 = y0 + random.randint(minsize, maxsize)
            color = ('red', 'orange', 'yellow', 'green', 'blue')[random.randint(0, 4)]
            # self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, activefill='black')
        self.canvas.create_rectangle(-50, 0, 50, 100, fill = "blue")
        w = self.calculate_w(4, 1, 100, 10)
        print("w is:", w)

        w_left = self.calculate_w_left_coord(-50, 50, 100, w, 150)

        print("wleft is:", w_left)

        w_right = self.calculate_w_right_coord(-50, 50, 100, w, 150)

        print("wright is:", w_right)

        self.draw_rectangles_given_w_and_index(0, 100, w_left[0], w_left[1], 10)
        self.draw_rectangles_given_w_and_index(1, 100, w_left[0], w_left[1], 10)
        self.draw_rectangles_given_w_and_index(2, 100, w_left[0], w_left[1], 10)
        self.draw_rectangles_given_w_and_index(3, 100, w_left[0], w_left[1], 10)
        # self.canvas.create_rectangle(170, 230, 270, 330, fill="blue")
        # self.canvas.create_rectangle(1700000, 1700000, 1700100, 1700100, fill="blue")

        self.canvas.create_line(150, 200, 220, 230)
        self.show_image()

    def scroll_y(self, *args, **kwargs):
        ''' Scroll canvas vertically and redraw the image '''
        self.canvas.yview(*args, **kwargs)  # scroll vertically
        self.show_image()  # redraw the image

    def scroll_x(self, *args, **kwargs):
        ''' Scroll canvas horizontally and redraw the image '''
        self.canvas.xview(*args, **kwargs)  # scroll horizontally
        self.show_image()  # redraw the image

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image

    def wheel(self, event):
        ''' Zoom with mouse wheel '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)  # get image area
        # if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
        # else: return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30: return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale        /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale        *= self.delta
        self.canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
        self.show_image()

    def show_image(self, event=None):
        ''' Show image on the Canvas '''
        bbox1 = self.canvas.bbox(self.container)  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
                 self.canvas.canvasy(0),
                 self.canvas.canvasx(self.canvas.winfo_width()),
                 self.canvas.canvasy(self.canvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.canvas.configure(scrollregion=bbox)  # set scroll region
        x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            x = min(int(x2 / self.imscale), self.width)   # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not
            image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                               anchor='nw', image=imagetk)
            self.canvas.lower(imageid)  # set image into background
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

    def draw_rectangles_given_w_and_index(self, index, l, wlx1, wly1, s):

        x1 = wlx1 + index * (l + s)
        y1 = wly1 - l / 2

        x2 = x1 + l
        y2 = y1 + l

        self.canvas.create_rectangle(x1, y1, x2, y2, fill = "blue")

    #b is maximum possible children
    #s is space between rectangles
    #d is depth of current layer
    #l is length of square
    def calculate_w(self, b, d, l, s):

        return ((b**d)*l) + ((b**d)-1)*s


    #x1: is parent rectangles left hand x coord
    #x2: is parent rectangles right hand x coord
    #y2: is parent rectangles right hand y coord
    #w: is width of the nodes at this layer
    #  calculated by ((b**d)*l)+((b**d)-1)*s
    #r is the distance between y2 and the
    # horizontal line that goes through
    # the center of rectangles at this layer
    def calculate_w_left_coord(self, x1, x2, y2, w, r):

        x_w_left = ((x1+x2)/2) - w/2
        y_w_left = y2 + r

        return x_w_left, y_w_left

    def calculate_w_right_coord(self, x1, x2, y2, w, r):

        x_w_right = ((x1+x2)/2) + w/2
        y_w_right = y2 + r

        return x_w_right, y_w_right






path = 'gray.PNG'  # place path to your image here
root = tk.Tk()
app = Zoom_Advanced(root, path=path, test = "hello")





root.mainloop()


