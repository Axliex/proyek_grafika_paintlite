import tkinter as tk
from tkinter import simpledialog, colorchooser
from math import cos, sin, pi, sqrt, radians

# Transformation functions
def translate(points, tx, ty):
    return [(x + tx, y + ty) for x, y in points]

def scale(points, sx, sy, cx, cy):
    return [(cx + (x - cx) * sx, cy + (y - cy) * sy) for x, y in points]

def rotate_point(x, y, angle, cx, cy):
    angle_rad = radians(angle)
    x_new = cos(angle_rad) * (x - cx) - sin(angle_rad) * (y - cy) + cx
    y_new = sin(angle_rad) * (x - cx) + cos(angle_rad) * (y - cy) + cy
    return x_new, y_new

def rotate(points, angle, cx, cy):
    return [rotate_point(x, y, angle, cx, cy) for x, y in points]

# Main Application Class
class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Paint Application")
        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        self.canvas.pack()

        self.shapes = []  # List to store shapes and their points
        self.current_points = []  # Points for the current shape
        self.selected_shape_index = None  # Index of the selected shape
        self.draw_mode = "point"
        self.default_line_color = "black"
        self.default_fill_color = ""
        self.line_color = self.default_line_color
        self.fill_color = self.default_fill_color

        self.setup_menu()
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_right_click)  # Bind right-click for selection

    def setup_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        
        draw_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Draw", menu=draw_menu)
        draw_menu.add_command(label="Point", command=self.set_draw_mode_point)
        draw_menu.add_command(label="Line", command=self.set_draw_mode_line)
        draw_menu.add_command(label="Circle", command=self.set_draw_mode_circle)
        draw_menu.add_command(label="Ellipse", command=self.set_draw_mode_ellipse)
        
        shape_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Shape", menu=shape_menu)
        shape_menu.add_command(label="Rectangle", command=self.set_draw_mode_rectangle)
        shape_menu.add_command(label="Square", command=self.set_draw_mode_square)
        shape_menu.add_command(label="Triangle", command=self.set_draw_mode_triangle)
        
        transform_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Transform", menu=transform_menu)
        transform_menu.add_command(label="Translate", command=self.translate_shape)
        transform_menu.add_command(label="Scale", command=self.scale_shape)
        transform_menu.add_command(label="Rotate", command=self.rotate_shape)

        color_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Color", menu=color_menu)
        color_menu.add_command(label="Set Line Color", command=self.set_line_color)
        color_menu.add_command(label="Set Fill Color", command=self.set_fill_color)

        menu.add_command(label="Clear Canvas", command=self.clear_canvas)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.shapes = []
        self.selected_shape_index = None

    def on_click(self, event):
        if self.draw_mode == "point":
            self.draw_point(event.x, event.y)
        else:
            self.current_points.append((event.x, event.y))
            if self.is_shape_complete():
                self.add_shape()
                self.redraw()
                self.current_points = []

    def on_right_click(self, event):
        self.select_shape(event.x, event.y)

    def select_shape(self, x, y):
        for i, (shape, points, line_color, fill_color) in enumerate(self.shapes):
            if shape == "point" and self.is_point_near(points[0], (x, y)):
                self.selected_shape_index = i
                self.redraw()
                return
            elif shape == "line" and self.is_point_on_line(points[0], points[1], (x, y)):
                self.selected_shape_index = i
                self.redraw()
                return
            elif shape in {"rectangle", "square"} and self.is_point_in_rectangle(points[0], points[1], (x, y)):
                self.selected_shape_index = i
                self.redraw()
                return
            elif shape == "circle" and self.is_point_in_circle(points[0], points[1], (x, y)):
                self.selected_shape_index = i
                self.redraw()
                return
            elif shape == "ellipse" and self.is_point_in_ellipse(points[0], points[1], points[2], (x, y)):
                self.selected_shape_index = i
                self.redraw()
                return
            elif shape == "triangle" and self.is_point_in_triangle(points[0], points[1], (x, y)):
                self.selected_shape_index = i
                self.redraw()
                return
        self.selected_shape_index = None
        self.redraw()

    def is_point_near(self, p1, p2, threshold=5):
        return abs(p1[0] - p2[0]) < threshold and abs(p1[1] - p2[1]) < threshold

    def is_point_on_line(self, p1, p2, p, threshold=5):
        # Check if point p is on the line segment p1p2
        if min(p1[0], p2[0]) - threshold <= p[0] <= max(p1[0], p2[0]) + threshold and \
           min(p1[1], p2[1]) - threshold <= p[1] <= max(p1[1], p2[1]) + threshold:
            # Line equation: (y - y1) = m(x - x1) => y = mx + c
            if p1[0] == p2[0]:  # Vertical line
                return abs(p[0] - p1[0]) < threshold
            m = (p2[1] - p1[1]) / (p2[0] - p1[0])
            c = p1[1] - m * p1[0]
            return abs(p[1] - (m * p[0] + c)) < threshold
        return False

    def is_point_in_rectangle(self, p1, p2, p):
        return min(p1[0], p2[0]) <= p[0] <= max(p1[0], p2[0]) and \
               min(p1[1], p2[1]) <= p[1] <= max(p1[1], p2[1])

    def is_point_in_circle(self, center, edge, p):
        r = sqrt((edge[0] - center[0]) ** 2 + (edge[1] - center[1]) ** 2)
        return sqrt((p[0] - center[0]) ** 2 + (p[1] - center[1]) ** 2) <= r

    def is_point_in_ellipse(self, center, rx, ry, p):
        if rx == 0 or ry == 0:
            return False
        return ((p[0] - center[0]) ** 2 / rx ** 2) + ((p[1] - center[1]) ** 2 / ry ** 2) <= 1

    def is_point_in_triangle(self, p1, p2, p):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = x1, y2
        # Barycentric coordinates method
        def sign(px, py, qx, qy, rx, ry):
            return (px - rx) * (qy - ry) - (qx - rx) * (py - ry)
        d1 = sign(p[0], p[1], x1, y1, x2, y2)
        d2 = sign(p[0], p[1], x2, y2, x3, y3)
        d3 = sign(p[0], p[1], x3, y3, x1, y1)
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_neg and has_pos)

    def is_shape_complete(self):
        if self.draw_mode in {"line", "rectangle", "square", "triangle"}:
            return len(self.current_points) == 2
        elif self.draw_mode == "circle":
            return len(self.current_points) == 2
        elif self.draw_mode == "ellipse":
            return len(self.current_points) == 3
        return False

    def add_shape(self):
        self.shapes.append((self.draw_mode, self.current_points.copy(), self.line_color, self.fill_color))

    def draw_point(self, x, y):
        self.canvas.create_oval(x, y, x + 1, y + 1, fill=self.line_color, outline=self.line_color)

    def draw_line(self, p1, p2, line_color):
        self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=line_color)

    def draw_circle(self, center, point, line_color, fill_color):
        r = int(sqrt((point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2))
        self.canvas.create_oval(center[0] - r, center[1] - r, center[0] + r, center[1] + r, outline=line_color, fill=fill_color)

    def draw_ellipse(self, center, rx, ry, line_color, fill_color):
        self.canvas.create_oval(center[0] - rx, center[1] - ry, center[0] + rx, center[1] + ry, outline=line_color, fill=fill_color)

    def draw_rectangle(self, p1, p2, line_color, fill_color):
        self.canvas.create_rectangle(p1[0], p1[1], p2[0], p2[1], outline=line_color, fill=fill_color)

    def draw_square(self, p1, p2, line_color, fill_color):
        side = min(abs(p2[0] - p1[0]), abs(p2[1] - p1[1]))
        self.canvas.create_rectangle(p1[0], p1[1], p1[0] + side, p1[1] + side, outline=line_color, fill=fill_color)

    def draw_triangle(self, p1, p2, line_color, fill_color):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = x1, y2
        self.canvas.create_polygon(x1, y1, x2, y2, x3, y3, outline=line_color, fill=fill_color)

    def translate_shape(self):
        if self.selected_shape_index is None:
            return
        tx = int(simpledialog.askstring("Translate", "Enter translation x:"))
        ty = int(simpledialog.askstring("Translate", "Enter translation y:"))
        shape, points, line_color, fill_color = self.shapes[self.selected_shape_index]
        self.shapes[self.selected_shape_index] = (shape, translate(points, tx, ty), line_color, fill_color)
        self.redraw()

    def scale_shape(self):
        if self.selected_shape_index is None:
            return
        sx = float(simpledialog.askstring("Scale", "Enter scale x:"))
        sy = float(simpledialog.askstring("Scale", "Enter scale y:"))
        shape, points, line_color, fill_color = self.shapes[self.selected_shape_index]
        cx, cy = points[0]
        self.shapes[self.selected_shape_index] = (shape, scale(points, sx, sy, cx, cy), line_color, fill_color)
        self.redraw()

    def rotate_shape(self):
        if self.selected_shape_index is None:
            return
        angle = float(simpledialog.askstring("Rotate", "Enter rotation angle:"))
        shape, points, line_color, fill_color = self.shapes[self.selected_shape_index]
        cx, cy = points[0]
        self.shapes[self.selected_shape_index] = (shape, rotate(points, angle, cx, cy), line_color, fill_color)
        self.redraw()

    def set_line_color(self):
        color = colorchooser.askcolor(title="Choose line color")[1]
        if color:
            self.line_color = color

    def set_fill_color(self):
        color = colorchooser.askcolor(title="Choose fill color")[1]
        if color:
            self.fill_color = color

    def reset_colors(self):
        self.line_color = self.default_line_color
        self.fill_color = self.default_fill_color

    def set_draw_mode_point(self):
        self.draw_mode = "point"

    def set_draw_mode_line(self):
        self.draw_mode = "line"

    def set_draw_mode_circle(self):
        self.draw_mode = "circle"

    def set_draw_mode_ellipse(self):
        self.draw_mode = "ellipse"

    def set_draw_mode_rectangle(self):
        self.draw_mode = "rectangle"

    def set_draw_mode_square(self):
        self.draw_mode = "square"

    def set_draw_mode_triangle(self):
        self.draw_mode = "triangle"

    def redraw(self):
        self.canvas.delete("all")
        for i, (shape, points, line_color, fill_color) in enumerate(self.shapes):
            if shape == "line":
                self.draw_line(points[0], points[1], line_color)
            elif shape == "rectangle":
                self.draw_rectangle(points[0], points[1], line_color, fill_color)
            elif shape == "square":
                self.draw_square(points[0], points[1], line_color, fill_color)
            elif shape == "triangle":
                self.draw_triangle(points[0], points[1], line_color, fill_color)
            elif shape == "circle":
                self.draw_circle(points[0], points[1], line_color, fill_color)
            elif shape == "ellipse":
                self.draw_ellipse(points[0], abs(points[0][0] - points[1][0]), abs(points[0][1] - points[2][1]), line_color, fill_color)

            # Highlight the selected shape
            if i == self.selected_shape_index:
                self.canvas.create_rectangle(self.canvas.bbox(self.canvas.create_line(points[0][0], points[0][1], points[-1][0], points[-1][1])), outline="red", dash=(4, 4))

if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()
