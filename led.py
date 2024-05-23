import tkinter as tk
from tkinter import colorchooser, simpledialog

class LEDControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LED Control UI")

        self.mode = tk.StringVar(value="Place")

        self.canvas = tk.Canvas(root, width=500, height=500, bg='white')
        self.canvas.pack()

        self.leds = []
        self.led_number = 1
        self.frames = [{}]  # List of frames, each frame is a dict {led_number: color}
        self.current_frame_index = 0

        self.canvas.bind("<Button-1>", self.canvas_click)

        self.mode_frame = tk.Frame(root)
        self.mode_frame.pack()

        self.place_mode_button = tk.Radiobutton(self.mode_frame, text="Place Mode", variable=self.mode, value="Place")
        self.place_mode_button.pack(side="left")
        self.edit_mode_button = tk.Radiobutton(self.mode_frame, text="Edit Mode", variable=self.mode, value="Edit")
        self.edit_mode_button.pack(side="left")

        self.frame_control_frame = tk.Frame(root)
        self.frame_control_frame.pack()

        self.add_frame_button = tk.Button(self.frame_control_frame, text="Add Frame", command=self.add_frame)
        self.add_frame_button.pack(side="left")
        self.prev_frame_button = tk.Button(self.frame_control_frame, text="Previous Frame", command=self.prev_frame)
        self.prev_frame_button.pack(side="left")
        self.next_frame_button = tk.Button(self.frame_control_frame, text="Next Frame", command=self.next_frame)
        self.next_frame_button.pack(side="left")

        self.generate_button = tk.Button(root, text="Generate Code", command=self.generate_code)
        self.generate_button.pack()

    def canvas_click(self, event):
        if self.mode.get() == "Place":
            self.place_led(event.x, event.y)
        elif self.mode.get() == "Edit":
            self.edit_led(event.x, event.y)

    def place_led(self, x, y):
        led_id = self.canvas.create_oval(x-5, y-5, x+5, y+5, fill='green')
        self.canvas.create_text(x, y-10, text=str(self.led_number), font=('Arial', 10), fill='black')
        self.leds.append({'number': self.led_number, 'x': x, 'y': y, 'id': led_id, 'color': 'green'})
        self.frames[0][self.led_number] = 'green'
        self.led_number += 1

    def edit_led(self, x, y):
        closest_item = self.canvas.find_closest(x, y)
        item_id = closest_item[0]
        for led in self.leds:
            if led['id'] == item_id:
                new_color = colorchooser.askcolor(title="Choose LED color")[1]
                if new_color:
                    self.canvas.itemconfig(led['id'], fill=new_color)
                    led['color'] = new_color
                    self.frames[self.current_frame_index][led['number']] = new_color
                break

    def add_frame(self):
        self.frames.append({})
        self.current_frame_index = len(self.frames) - 1
        self.update_canvas()

    def prev_frame(self):
        if self.current_frame_index > 0:
            self.current_frame_index -= 1
            self.update_canvas()

    def next_frame(self):
        if self.current_frame_index < len(self.frames) - 1:
            self.current_frame_index += 1
            self.update_canvas()

    def update_canvas(self):
        self.canvas.delete("all")
        for led in self.leds:
            color = self.frames[self.current_frame_index].get(led['number'], 'green')
            led_id = self.canvas.create_oval(led['x']-5, led['y']-5, led['x']+5, led['y']+5, fill=color)
            self.canvas.create_text(led['x'], led['y']-10, text=str(led['number']), font=('Arial', 10), fill='black')
            led['id'] = led_id

    def generate_code(self):
        code = """import time
import board
import neopixel

pixels = neopixel.NeoPixel(board.D18, {}, brightness=0.2)

frames = [\n""".format(len(self.leds))

        for frame in self.frames:
            frame_code = "    {"
            for led_number, color in frame.items():
                r, g, b = self.hex_to_rgb(color)
                frame_code += f"{led_number - 1}: ({r}, {g}, {b}), "
            frame_code = frame_code.rstrip(', ') + "},\n"
            code += frame_code

        code += """    ]

def show_frame(strip, frame):
    for led_number, color in frame.items():
        strip[led_number] = color
    strip.show()

while True:
    for frame in frames:
        show_frame(pixels, frame)
        time.sleep(1)  # Adjust the delay as needed
"""

        print(code)
        with open("led_show_code.py", "w") as f:
            f.write(code)

    def hex_to_rgb(self, hex):
        if hex.startswith('#') and len(hex) == 7:
            return tuple(int(hex[i:i+2], 16) for i in (1, 3, 5))
        else:
            return (0, 255, 0)

if __name__ == "__main__":
    root = tk.Tk()
    app = LEDControlApp(root)
    root.mainloop()
