import customtkinter as ctk
import draw_surface
import tool_panel
import utils


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry('800x600')
        self.title('')
        self.iconbitmap('./src/empty.ico')
        ctk.set_appearance_mode('light')

        self.color_string = ctk.StringVar(value='000')
        self.brush_float = ctk.DoubleVar(value=0.2)
        self.is_erasing = ctk.BooleanVar(value=False)

        self.draw_surface = draw_surface.DrawSurface(self, self.color_string, self.brush_float, self.is_erasing)

        tool_panel.ToolPanel(self, self.brush_float, self.color_string, self.is_erasing, self.clear_canvas)

        self.bind('<MouseWheel>', self.adjust_brush_size)

        self.mainloop()

    def adjust_brush_size(self, event):
        direction = utils.sign(event.delta)
        brush_size = self.brush_float.get()
        new_brush_size = round(brush_size + 0.05 * direction, 2)
        if new_brush_size != brush_size:
            self.brush_float.set(max(0.2, min(1, new_brush_size)))

    def clear_canvas(self):
        self.draw_surface.delete('all')
        self.is_erasing.set(False)


if __name__ == '__main__':
    App()
