from tkinter import Canvas
import settings


class DrawSurface(Canvas):
    def __init__(self, master, color_string, brush_float, is_erasing):
        super().__init__(master=master, background=settings.CANVS_BG, bd=0, highlightthickness=0, relief='ridge')
        self.pack(expand=True, fill='both')

        self.color_string = color_string
        self.brush_float = brush_float
        self.is_erasing = is_erasing
        self.is_drawing = False

        self.previous_x = self.previous_y = None

        self.bind('<Motion>', self.draw)
        self.bind('<Button>', self.activate_draw)
        self.bind('<ButtonRelease>', self.deactivate_draw)

    def draw(self, event):
        if self.is_drawing:
            if self.previous_y and self.previous_x:
                self.create_brush_line((self.previous_x, self.previous_y), (event.x, event.y))
            self.previous_y = event.y
            self.previous_x = event.x

    def create_brush_line(self, start, end):
        brush_size = self.brush_float.get() * 5 * (self.brush_float.get() + 1) ** 4
        self.create_line(start, end, fill=f'#{self.color_string.get()}' if not self.is_erasing.get() else '#FFF', width=brush_size, capstyle='round')

    def activate_draw(self, event):
        self.is_drawing = True
        self.create_brush_line((event.x, event.y), (event.x, event.y))
        self.previous_y = event.y
        self.previous_x = event.x

    def deactivate_draw(self, event):
        self.is_drawing = False
        self.previous_x = self.previous_y = None
