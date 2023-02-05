import random


class Circle:
    # This class defines the parameters of the holes with the coordinates of the center and the radius. It can also
    # check if the circle intersects with another circle or exceeds a given boundary by calling methods intersect and
    # boundCheck respectively.
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def __str__(self):
        return f'[{self.x}, {self.y}, {self.radius}]'

    __repr__ = __str__

    # This method checks if the circle intersects with another circle. Requires one input of the other circle to
    # check for an intersection.
    def intersect(self, other):
        d = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5  # Find the distance between the two centers
        sep = self.radius + other.radius  # Find the separation needed to not intersect the circles
        if d <= sep:  # If the distance calculated is greater than the separation needed return True, otherwise
            return True  # return False
        else:
            return False

    # This method checks if the circle exceeds the boundary given by the class Rectangle. Requires one input of the
    # rectangle boundaries.
    def boundCheck(self, rectangle):
        x_plus = self.x + self.radius  # Compute the maximum and minimum values of x and y obtained by the circle
        y_plus = self.y + self.radius
        x_minus = self.x - self.radius
        y_minus = self.y - self.radius
        
        if x_plus >= rectangle.x_max or y_plus >= rectangle.y_max or x_minus <= rectangle.x_min or y_minus <= rectangle.y_min:
            return False
        else:
            return True
          
#         x_high = max(x_plus, x_minus)
#         y_high = max(x_plus, y_minus)
#         x_low = min(x_plus, x_minus)
#         y_low = min(y_plus, y_minus)
#         if x_high >= rectangle.x_max:
#             return False
#         elif y_high >= rectangle.y_max:
#             return False
#         else:
#             if x_low <= rectangle.x_min:
#                 return False
#             elif y_low <= rectangle.y_min:
#                 return False
#             else:
#                 return True


class Rectangle:
    # This class defines the matrix parameters including the boundary of the area, the average radius of holes, and the
    # standard deviation of the radius of the holes. It can make the output to the .geo file by calling the method make.
    def __init__(self, x_min, y_min, x_max, y_max, avg_rad, rad_dev):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.avg_rad = avg_rad
        self.rad_dev = rad_dev

    def __str__(self):
        return f'[[{self.x_min}, {self.y_min}], [{self.x_max}, {self.y_max}]]'

    __repr__ = __str__

    # This method generates and outputs the .geo file that create the main domain of RVE/SVE
    def make(self, points):
        # This string creates the title of the frame components and also lists the position of the minimum
        # corner and maximum corner.
        text = '\n\n\n////////////////////////////////////////////////////////////////////////////////\n' \
               + f'// Frame\n// Minimum Corner: ({self.x_min}, {self.y_min})\n// Maximum Corner: ({self.x_max}, {self.y_max})\n' \
               + '////////////////////////////////////////////////////////////////////////////////\n\n'

        # This string creates the box that bounds all the holes and saves it as a surface
        boxtext = f'//+\nPoint(1) = ' + '{' + f'{self.x_min}, {self.y_min}, 0, res' + '};\n' \
                  + f'//+\nPoint(2) = ' + '{' + f'{self.x_min}, {self.y_max}, 0, res' + '};\n' \
                  + f'//+\nPoint(3) = ' + '{' + f'{self.x_max}, {self.y_max}, 0, res' + '};\n' \
                  + f'//+\nPoint(4) = ' + '{' + f'{self.x_max}, {self.y_min}, 0, res' + '};\n' \
                  + '//+\nLine(5) = {1, 2};\n' \
                  + '//+\nLine(6) = {2, 3};\n' \
                  + '//+\nLine(7) = {3, 4};\n' \
                  + '//+\nLine(8) = {4, 1};\n' \
                  + '//+\nLine Loop(9) = {5, 6 , 7, 8};\n' \
                  + '//+\nPlane Surface(10) = {9'

        # This function inputs the hole surfaces into the box surface for each hole
        for i in range(1, points.countholes + 1):
            num = i * 100 + 9  # Hole number is determined by multiples of 100 and surface label of the
            boxtext = boxtext + f', {num}'  # hole is always the 9th label.

        # This string creates the boundary labels and surface label for the matrix
        boxtext = boxtext + '};\n' \
                          + '//+\nPhysical Line("Left") = {5};\n' \
                          + '//+\nPhysical Line("Top") = {6};\n' \
                          + '//+\nPhysical Line("Right") = {7};\n' \
                          + '//+\nPhysical Line("Bottom") = {8};\n' \
                          + '//+\nPhysical Surface("Matrix") = {10};\n'
        return text + boxtext


class Points:
    # This class defines all the holes in the matrix. Requires inputs of the boundary rectangle and the number of points
    # in the matrix. It generates and outputs the .geo file by calling the method generate.
    def __init__(self, rectangle, points):
        self.rectangle = rectangle
        self.points = points
        self.list = []
        self.countholes = 0

    def __str__(self):
        out = ''
        for i in range(len(self.list)):
            out = out + f'[{self.list[i]}]'
        return out

    __repr__ = __str__

    # This method translates the hole into the .geo for the output file. Requires input of the circle to be translated.
    def __form2D__(self, circle):
        self.countholes += 1
        countholes = self.countholes * 100
        count = countholes
        pointstext = ''
        loopstext = ''

        if self.countholes - 1 == 0:  # If this is the first hole, don't skip as many lines for nicer formatting
            text = ''
        else:
            text = '\n\n\n'

        # This string creates the title for the following hole that describe the hole number, coordinates of the center
        # of the circle, and radius of the circle.
        text = text + '////////////////////////////////////////////////////////////////////////////////\n' \
                    + f'// Hole #{self.countholes}\n// Center: ({circle.x}, {circle.y})\n// Radius: {circle.radius}\n' \
                    + '////////////////////////////////////////////////////////////////////////////////\n\n'

        # This function generates the point and circle .geo formats for the circle by using 2 alternating series that
        # determines when to add and subtract the radius from the x and y coordinates for the center and 4 points on the
        # circumference. It also generates the circumference lines.
        for n in range(1, 6):
            an = (1 / 3) * (n - 1) * (n ** 2 - 8 * n + 15)
            if n == 1:
                bn = 0
            else:
                m = n - 1
                bn = (5 - m) * m - 5

            pointstext = pointstext + f'//+\nPoint({count}) = ' + '{' + f'{circle.x + an * circle.radius}, {circle.y + (an + bn) * circle.radius}' + ', 0, res};\n'

            if n == 5:
                loopstext = loopstext + f'//\nCircle({count + 4}) = ' + '{' + f'{count}, {count - n + 1}, {count - n + 2}' + '};\n'
            elif n >= 2:
                loopstext = loopstext + f'//\nCircle({count + 4}) = ' + '{' + f'{count}, {count - n + 1}, {count + 1}' + '};\n'
            count += 1

        # This string unifies the circumference lines, makes the hole into a surface, and labels the surface by the hole
        # number.
        loopstext = loopstext + f'//+\nLine Loop({count + 4}) = ' + '{' + f'{count}, {count + 1}, {count + 2}, {count + 3}' + '};\n' \
                              + f'//+\nSurface({count + 5}) = ' + '{' + f'{count + 4}' + '};\n' \
                              + f'//+\nPhysical Surface("Hole {self.countholes}") = ' + '{' + f'{count + 5}' + '};\n'

        return text + pointstext + loopstext

    # This method generates the complete .geo output file. Requires the name of the file to be generated and the maximum
    # number of guesses allowed per hole.
    def generate(self, file, max_iterations=1000):
        text = ''  # String for collecting the 2D .geo format of the holes generated
        for i in range(self.points):
            j = 0  # Reset the number of guesses for the new hole generation
            look = True
            while look is True:
                if j > max_iterations:  # If the number of guesses exceeds max guesses allowed send error to file
                    fileout = open(file, 'w')
                    fileout.write(f'Max iterations exceeded for hole {i}')
                    fileout.close()
                    return None
                j += 1
                # rad = self.rectangle.avg_rad * (random.gauss(1, self.rectangle.rad_dev))
                rad = avg_radius * random.lognormvariate(avg_radius,
                                                         std_radius)  # Choose random radius using log normal distribution.
                xspan = self.rectangle.x_max - self.rectangle.x_min - 2 * rad  # Span possible by x and y coordinates
                yspan = self.rectangle.y_max - self.rectangle.y_min - 2 * rad  # must be 1 radius away from each side.
                x = self.rectangle.x_min + rad + xspan * random.random()  # Position of coordinate is one radius above
                y = self.rectangle.y_min + rad + yspan * random.random()  # the minimum plus a random distance in the span
                new_circle = Circle(x, y, rad)
                for existing in self.list:  # Check that the new circle does not intersect the pre-existing circles
                    if new_circle.intersect(existing) is True:
                        break
                    elif new_circle.boundCheck(self.rectangle) is False:
                        break
                else:
                    self.list = self.list + [new_circle]
                    text = text + self.__form2D__(new_circle)
                    look = False

        boxtext = self.rectangle.make(self)  # Generate the Matrix
        fileout = open(file, 'w')
        fileout.write(f'res = 0.1;\n\n')
        fileout.write(text)
        fileout.write(boxtext)
        fileout.close()


# Example of setting parameters and generating the output file
x_minimum = 0
y_minimum = 0
x_maximum = 0.5
y_maximum = 0.5
avg_radius = 0.1
std_radius = 0
holes = 1
output_file = 'final2D.geo'

rect = Rectangle(x_minimum, y_minimum, x_maximum, y_maximum, avg_radius, std_radius)
pts = Points(rect, holes)
pts.generate(output_file)