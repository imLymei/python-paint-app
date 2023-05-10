import customtkinter as ctk
from PIL import Image
from tkinter import Canvas
import settings


class ToolPanel(ctk.CTkToplevel):
    def __init__(self, parent, brush_float, color_string, is_erasing, clear_canvas):
        super().__init__()

        self.parent = parent
        self.brush_float = brush_float
        self.is_erasing = is_erasing

        self.geometry('200x300')
        self.title('')
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.protocol('WM_DELETE_WINDOW', self.close_app)

        self.columnconfigure((0, 1, 2), weight=1, uniform='a')
        self.rowconfigure(0, weight=2, uniform='a')
        self.rowconfigure(1, weight=3, uniform='a')
        self.rowconfigure((2, 3), weight=1, uniform='a')

        BrushSizeSlider(self, brush_float)
        self.color_slide_panel = ColorSlidePanel(self, color_string)
        self.brush_preview = BrushPreview(self, color_string, self.brush_float, self.is_erasing)
        ColorPanel(self, color_string)

        self.brush_button = BrushButton(self, 0, self.is_erasing)
        self.eraser_button = EraseButton(self, 1, self.is_erasing)
        CleanButton(self, 2, clear_canvas)

        self.is_erasing.trace('w', self.toggle_button_selected)
        color_string.trace('w', self.color_slide_panel.change_all_colors)

    def close_app(self):
        self.parent.quit()
        self.quit()

    def toggle_button_selected(self, *args):
        if self.is_erasing.get():
            self.eraser_button.configure(fg_color=settings.BUTTON_ACTIVE_COLOR)
            self.brush_button.configure(fg_color=settings.BUTTON_COLOR)
        else:
            self.brush_button.configure(fg_color=settings.BUTTON_ACTIVE_COLOR)
            self.eraser_button.configure(fg_color=settings.BUTTON_COLOR)


class ColorPanel(ctk.CTkFrame):
    def __init__(self, master, color_string):
        super().__init__(master=master, fg_color='transparent')

        self.color_string = color_string

        self.rowconfigure(list(range(settings.COLOR_ROWS)), weight=1, uniform='b')
        self.columnconfigure(list(range(settings.COLOR_COLS)), weight=1, uniform='b')

        for row_index, row in enumerate(settings.COLORS):
            for column_index, data in enumerate(row):
                ColorFieldButton(self, row_index, column_index, data, self.change_color)

        self.grid(row=1, column=0, columnspan=3, pady=5, padx=5)

    def change_color(self, value):
        self.color_string.set(value)


class ColorSlidePanel(ctk.CTkFrame):
    def __init__(self, master, color_string):
        super().__init__(master=master)

        self.color_string = color_string
        self.r_int = ctk.IntVar(value=self.color_string.get()[0])
        self.g_int = ctk.IntVar(value=self.color_string.get()[1])
        self.b_int = ctk.IntVar(value=self.color_string.get()[2])

        self.is_erasing = master.is_erasing

        self.rowconfigure((0, 1, 2), weight=1, uniform='c')
        self.columnconfigure(0, weight=1, uniform='c')

        self.red_slider = ColorSliders(self, 0, 0, self.r_int, settings.SLIDER_RED, self.set_single_color, 'r')
        self.green_slider = ColorSliders(self, 1, 0, self.g_int, settings.SLIDER_GREEN, self.set_single_color, 'g')
        self.blue_slider = ColorSliders(self, 2, 0, self.b_int, settings.SLIDER_BLUE, self.set_single_color, 'b')

        self.grid(row=0, column=0, sticky='nswe', padx=5, pady=5)

    def change_all_colors(self, *args):
        color = self.color_string.get()
        color_range = settings.COLOR_RANGE

        self.r_int.set(color_range.index(color[0]))
        self.g_int.set(color_range.index(color[1]))
        self.b_int.set(color_range.index(color[2]))

        self.is_erasing.set(False)

    def set_single_color(self, color, value):
        match color:
            case 'r':
                self.r_int.set(value)
            case 'g':
                self.g_int.set(value)
            case 'b':
                self.b_int.set(value)
        self.color_string.set(
            f'{settings.COLOR_RANGE[self.r_int.get()]}{settings.COLOR_RANGE[self.g_int.get()]}{settings.COLOR_RANGE[self.b_int.get()]}')


class ColorSliders(ctk.CTkSlider):
    def __init__(self, master, row, column, variable, color, function, function_color):
        super().__init__(master, from_=0, to=15, number_of_steps=16, variable=variable,
                         command=lambda value: function(function_color, value), button_color=color,
                         button_hover_color=color)

        self.grid(row=row, column=column, padx=2, pady=0.5)


class ColorFieldButton(ctk.CTkButton):
    def __init__(self, master, row, column, data, change_color):
        super().__init__(master=master, text='', fg_color=f'#{data}', hover_color=f'#{data}', corner_radius=0,
                         command=lambda: change_color(data))
        self.grid(row=row, column=column, padx=0.5, pady=0.5)


class BrushSizeSlider(ctk.CTkFrame):
    def __init__(self, master, brush_float):
        super().__init__(master=master)

        ctk.CTkSlider(self, variable=brush_float, from_=0.2).pack(expand=True, fill='x', padx=5)

        self.grid(row=2, column=0, columnspan=3, sticky='nswe', pady=5, padx=5)


class BrushPreview(Canvas):
    def __init__(self, master, color_string, brush_float, is_erasing):
        super().__init__(master=master, background=settings.BRUSH_PREVIEW_BG, bd=0, highlightthickness=0,
                         relief='ridge')

        self.color_string = color_string
        self.brush_float = brush_float
        self.is_erasing = is_erasing

        self.color_string.trace('w', self.update_preview)
        self.brush_float.trace('w', self.update_preview)
        self.is_erasing.trace('w', self.update_preview)

        self.x = self.y = self.max_length = 0

        self.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky='nswe')

        self.bind('<Configure>', self.setup)

    def update_preview(self, *args):
        self.delete('all')
        current_radius = self.max_length * self.brush_float.get()
        color = f'#{self.color_string.get()}' if not self.is_erasing.get() else '#FFF'
        border_color = f'#{self.color_string.get()}' if not self.is_erasing.get() else '#000'
        self.create_oval(self.x - current_radius, self.y - current_radius,
                         self.x + current_radius, self.y + current_radius,
                         fill=color, outline=border_color)

    def setup(self, event):
        self.x = event.width/2
        self.y = event.height/2
        self.max_length = self.x * 0.6
        self.update_preview()


class Button(ctk.CTkButton):
    def __init__(self, master, image_path, col, function, color=settings.BUTTON_COLOR):
        image = ctk.CTkImage(light_image=Image.open(image_path), dark_image=Image.open(image_path))
        super().__init__(master=master, text='', image=image, fg_color=color,
                         hover_color=settings.BUTTON_HOVER_COLOR, command=function)
        self.grid(row=3, column=col, sticky='nswe', padx=5, pady=5)


class BrushButton(Button):
    def __init__(self, master, col, is_erasing):
        super().__init__(master=master, image_path='./src/brush.png', col=col, function=lambda: is_erasing.set(False),
                         color=settings.BUTTON_ACTIVE_COLOR)


class EraseButton(Button):
    def __init__(self, master, col, is_erasing):
        super().__init__(master=master, image_path='./src/eraser.png', col=col, function=lambda: is_erasing.set(True))


class CleanButton(Button):
    def __init__(self, master, col, function):
        super().__init__(master=master, image_path='./src/clear.png', col=col, function=function)
