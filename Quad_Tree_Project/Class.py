import pygame


def two_range_overlap(low1, high1, low2, high2):
    if high2 > high1:
        if low1 <= low2 <= high1:
            return True
        else:
            return False

    # elif high1 > high2 or high1 == high2 (Just a note of the cases)
    else:
        if low2 <= low1 <= high2:
            return True
        else:
            return False


class Boundary:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class Rect:
    def __init__(self, x, y, w, h, dx, dy):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = (0,0,0)
        self.dx = dx
        self.dy = dy

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h))

    def update(self, screen_w, screen_h, collisions):
        self.x += self.dx
        self.y += self.dy

        if self.x < 0:
            self.dx *= -1
            self.x = 0
        elif self.x + self.w > screen_w:
            self.dx *= -1
            self.x = screen_w - self.w

        if self.y < 0:
            self.y = 0
            self.dy *= -1
        elif self.y + self.h > screen_h:
            self.dy *= -1
            self.y = screen_h - self.h

        self.collision_check(collisions)

    def collision_check(self, collisions):
        # There is a certain case that this function has to bypass
        # This case is when there is an object touching the border of a quadrant and therefore is not fully part of that quadrant
        # If we were to perform a "retrieve" on that object, we would inherently get only other objects on the border of the same family quadrant
        # Any objects fully within quadrants that are touching the object bordering a line would not be gotten in the "retrieve function"
        # To bypass this, we create a partner effect where is 1 object touches another, both objects are set yo be red
        # This way, an object inside a quadrant touching a bordering object would be accounted for
        # The bordering object would not see the quadrant object while the quadrant object would see the quadrant object

        other_hits = []
        low1_x, high1_x = self.x, self.x + self.w
        low1_y, high1_y = self.y, self.y + self.h
        for collision in collisions:
            y_flag = True  # Collision in x_axis
            x_flag = True  # Collision in y_axis

            low2_x, high2_x = collision.x, collision.x + collision.w
            if two_range_overlap(low1_x, high1_x, low2_x, high2_x):
                x_flag = False

            low2_y, high2_y = collision.y, collision.y + collision.h
            if two_range_overlap(low1_y, high1_y, low2_y, high2_y):
                y_flag = False

            if not x_flag and not y_flag:  # Collision in both axes means overall collision/overlap
                other_hits.append(collision)

        if len(other_hits) > 0:  # If len(other_hits) > 0, it means there was a collision with at leas t 1 object
            self.color = (255, 0, 0)

        for hit in other_hits:
            hit.color = (255, 0, 0)


class Quad_tree:
    def __init__(self, bound_x, bound_y, bound_w, bound_h, level):
        self.max_objects = 6
        self.max_depth = 6
        self.boundary = Boundary(bound_x, bound_y, bound_w, bound_h)
        self.nodes = [None, None, None, None]
        self.level = level
        self.objects = []  # Stores the objects for the game (in this case they are rectangles)
        # Note that the majority of items in self.objects should only exist at leaf nodes
        # Cases where items are in self.objects for nodes which are not leaf nodes occur when an item doesn't
        # directly fit into any of the 4 child quadrants and must be stored within the parent quadrant
        # These "irregular items" would later be retrieved by the "retrieve" function

    def clear(self):
        # Recursive Function (Should be using a dfs-like approach)
        if self.nodes[0] != None:  # Base-case Condition (If the child nodes are not "None", that means we are not on a leaf node and that we can traverse deeper)
            self.objects = []  # Clear the parent node of all of its objects (Rectangles in this case)
            for i in range(len(self.nodes)):
                self.nodes[i].clear()  # Recur deeper (this line needs to be placed before the next one since we want ot access another quadtree object instead of a None Object)
                self.nodes[i] = None  # Set the child node to be none once the "bottom-up" occurs

    def split(self):
        # Child quadrants are to be numbers as if they were quadrants on a cartesian plane
        # Here, a parent quadrant is split into 4 child quadrants
        # Boundaries of each child quadrant are calcuklated however the objects within each child quadrant are not calculated here (Done instead by "insert")
        x, y = self.boundary.x, self.boundary.y
        sub_width = self.boundary.w / 2
        sub_height = self.boundary.h / 2

        self.nodes[0] = Quad_tree(x + sub_width, y, sub_width, sub_height, self.level + 1)
        self.nodes[1] = Quad_tree(x, y, sub_width, sub_height, self.level + 1)
        self.nodes[2] = Quad_tree(x, y + sub_height, sub_width, sub_height, self.level + 1)
        self.nodes[3] = Quad_tree(x + sub_width, y + sub_height, sub_width, sub_height, self.level + 1)

    def get_index(self, rect):
        # Calculates if and which parent quadrant a rectangular object belongs to
        # Quadrant indexes relate to quadrant in cartesian plane and -1 means that the object belongs to its parent quadrant

        index = -1  # Defaults to the location being it's parent
        vert_mid = self.boundary.x + self.boundary.w / 2  # Y-axis
        hori_mid = self.boundary.y + self.boundary.h / 2  # X-axis

        top_quadrant = rect.y < hori_mid and rect.y + rect.h < hori_mid
        bottom_qudrant = rect.y > hori_mid

        # Object can completely fill left quadrants
        if rect.x < vert_mid and rect.x  + rect.w < vert_mid:
            if top_quadrant: index = 1  # Quad 2
            elif bottom_qudrant: index = 2  # Quad 3

        # Object can completely fill right quadrants
        if rect.x > vert_mid:
            if top_quadrant: index = 0  # Quad 1
            elif bottom_qudrant: index = 3  # Quad 4

        return index

    def insert(self, rect):
        # Recursive function
        # Eventually, we will either hit a leaf node or we have a case where the rectangle doesn't completely belong
        # In only one quadrant

        # The first part's duty is to recur down to either find the deepest parent quadrant
        # The result will either be a case where we can't recur any deeper or the index of the object is -1
        # The index = -1 case is special because it means that we can go deeper into the tree however no deeper quadrants would include the object
        if self.nodes[0] != None:  # Checks to see if we are a current leaf nodes
            # We are not on a current leaf node
            index = self.get_index(rect)

            if index != -1:
                # The rectangle is found to be capable of fitting in a quadrant completely
                self.nodes[index].insert(rect)  # Recur deeper
                return  # Since we are yet at the lowest level, we don't want ot execute the below code just yet
            #else:
            # The object doesn't completely fit within a child quadrant and therefore will be part of the parent quadrant/node

        # Below code should execute when we have reached a leaf node or when the object's index = -1
        self.objects.append(rect)  # Append the object into either the leaf's nodes' one quadrant or a parent node's quadrant

        if len(self.objects) > self.max_objects and self.level < self.max_depth:
            if self.nodes[0] == None:  # The reason for this line is to account for the index = -1 case (If there was such a case, we wouldn't want to split since we might not be at a leaf node and there might be information in below nodes)
                self.split()  # This line should run every time once the leaf node is reached

            # Anything under this doesn't make sense to me
            i = 0
            while i < len(self.objects):  # The main thing about this line is that the len(self.objects) is not permanent and may change
                index = self.get_index(self.objects[i])
                if index != -1:
                    obj = self.objects[i]
                    # del self.objects[i]  # This line changes the len(self.objects)
                    self.objects.remove(obj)
                    self.nodes[index].insert(obj)
                else:
                    i += 1

    def retrieve(self, return_objects, rect):
        index = self.get_index(rect)
        if index != -1 and self.nodes[0] != None:
            self.nodes[index].retrieve(return_objects, rect)

        # return_objects += self.objects  # Important thing here is that it picks all objects from leaf node AND any objects that were no fully within quadrants
        for obj in self.objects:
            return_objects.append(obj)
        # Retrieval of leaf node objects happens once the dfs hits bottom
        # The getting of objects that were not fully within quadrants is super cool and is done as the dfs goes back up from bottom
        return return_objects

    def draw_trees(self, screen):  # Used to draw quadtree

        # We basically continue recurring deeper as long as we aren't at a leaf leaf

        if self.nodes[0] != None:

            # Horizontal Line
            pygame.draw.line(screen, (0,0,0), (self.boundary.x, self.boundary.y + self.boundary.h/2), (self.boundary.x + self.boundary.w, self.boundary.y + self.boundary.h/2))
            # Vertical Line
            pygame.draw.line(screen, (0,0,0), (self.boundary.x + self.boundary.w/2, self.boundary.y), (self.boundary.x + self.boundary.w/2, self.boundary.y + self.boundary.h))

            for i in range(len(self.nodes)):
                self.nodes[i].draw_trees(screen)


