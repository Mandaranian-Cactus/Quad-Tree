import pygame


def two_range_overlap(low1, high1, low2, high2):  # Assumes a 1-D check
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
        self.state = False  # False = black (off) , True = red (on)

    def draw(self, screen):
        if self.state:
            pygame.draw.rect(screen, (255, 200, 100), (self.x, self.y, self.w, self.h))
        else:
            pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.w, self.h))

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
        # This case is when there is an object overlapping the border of a quadrant and therefore is not fully part of any quadrant
        # If we were to perform a "retrieve" on that object, we would inherently get only other objects overlapping the border of the same family quadrant
        # Any objects fully within child quadrants that are touching the object overlapping a border would not be gotten in the "retrieve function"
        # To bypass this, we create a partner effect where if 1 object touches another, both objects are set to be affected
        # This way, an object inside a child quadrant touching an overlapping object would be accounted for
        # The overlapping object would not see the quadrant object while the quadrant object would see the overlapping object

        other_hits = []
        low1_x, high1_x = self.x, self.x + self.w
        low1_y, high1_y = self.y, self.y + self.h
        for collision in collisions:
            y_flag = False  # Collision in x_axis
            x_flag = False  # Collision in y_axis

            low2_x, high2_x = collision.x, collision.x + collision.w
            if two_range_overlap(low1_x, high1_x, low2_x, high2_x):
                x_flag = True

            low2_y, high2_y = collision.y, collision.y + collision.h
            if two_range_overlap(low1_y, high1_y, low2_y, high2_y):
                y_flag = True

            if x_flag and y_flag:  # Collision in both axes means overall collision/overlap
                other_hits.append(collision)

        if len(other_hits) > 0:  # If len(other_hits) > 0, it means there was a collision with at leas t 1 object
            self.state = True

        for hit in other_hits:
            hit.state = True


class Quad_tree:
    def __init__(self, bound_x, bound_y, bound_w, bound_h, level):
        self.max_objects = 3
        self.max_depth = 6
        self.boundary = Boundary(bound_x, bound_y, bound_w, bound_h)
        self.nodes = [None, None, None, None]
        self.level = level
        self.objects = []  # Stores the objects for the game (in this case they are rectangles)
        # Note that the majority of items in self.objects should only exist at leaf nodes
        # Cases where items are in self.objects for nodes which are not leaf nodes occur when an item doesn't
        # directly fit into any of the 4 child quadrants and must be stored within the parent quadrant
        # These "irregular items" would later be retrieved by the "retrieve" function

    def clear(self):  # Clears the quad_tree of all stored objects (rectangles in this case) from its current level down to the leaf node level
        # Recursive Function (Should be using a dfs-like approach)
        self.objects = []  # Clear the parent node (Current layer) of all of its objects (Rectangles in this case)
        if self.nodes[0] != None:  # Base-case Condition (If the child nodes are not "None", that means we are not on a leaf node and that we can traverse deeper)
            for i in range(len(self.nodes)):
                self.nodes[i].clear()  # Recur deeper (this line needs to be placed before the next one since we want ot access another quadtree object instead of a None Object)
                self.nodes[i] = None  # Set the child node of the current later to be none once the "bottom-up" occurs (We can't take it out as we go "top-bottom" since we need to access it before deleting it)

    def split(self):
        # Child quadrants are to be numbered similarly to quadrants on a cartesian plane
        # Here, a parent quadrant is split into 4 child quadrants (Occurs due to the over-population of a parent quadrant)
        # Boundaries of each child quadrant are calculated however the objects within each child quadrant are not calculated here (Done instead by "insert")
        x, y = self.boundary.x, self.boundary.y
        sub_width = self.boundary.w / 2
        sub_height = self.boundary.h / 2

        # Quadrants here are like the quadrants on a cartesian plane
        self.nodes[0] = Quad_tree(x + sub_width, y, sub_width, sub_height, self.level + 1)
        self.nodes[1] = Quad_tree(x, y, sub_width, sub_height, self.level + 1)
        self.nodes[2] = Quad_tree(x, y + sub_height, sub_width, sub_height, self.level + 1)
        self.nodes[3] = Quad_tree(x + sub_width, y + sub_height, sub_width, sub_height, self.level + 1)

    def get_index(self, rect):
        # Calculates if and which child (or its own parent in a special case) quadrant a rectangular object belongs to
        # Quadrant indexes relate to quadrant in cartesian plane and -1 means that the object belongs to its parent quadrant

        index = -1  # Defaults to the location being it's parent
        vert_mid = self.boundary.x + self.boundary.w / 2  # Y-axis
        hori_mid = self.boundary.y + self.boundary.h / 2  # X-axis

        top_quadrant = rect.y < hori_mid and rect.y + rect.h < hori_mid  # 2 checks needed due to the nature of the rectangle shape and coordinate placement
        bottom_qudrant = rect.y > hori_mid  # 1 check needed due to the nature of the rectangle shape and coordinate placement

        # Object can completely fill left quadrants
        if rect.x < vert_mid and rect.x + rect.w < vert_mid:
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
        # The index = -1 case is special because it means that we can go deeper down the tree however we choose not to
        if self.nodes[0] != None:  # Checks to see if we are on a leaf node
            # We are not on a current leaf node
            index = self.get_index(rect)

            if index != -1:
                # The rectangle is found to be capable of fitting in a quadrant completely
                self.nodes[index].insert(rect)  # Recur deeper
                return  # Since we are yet at the lowest level, we don't want ot execute the below code
            #else:
            # The object doesn't completely fit within a child quadrant and therefore will be part of the parent quadrant/node

        # Below code should execute when we have reached a leaf node or when the object's index = -1 (overlap/irregular case)
        self.objects.append(rect)  # Append the object into either one of the leaf's nodes' quadrant or a parent node's quadrant

        if len(self.objects) > self.max_objects and self.level < self.max_depth:

            # Check to confirm that we are at a leaf node
            if self.nodes[0] == None:  # The reason for this line is to account for the index = -1 case (If there was such a case, we wouldn't want to split since we might not be at a leaf node and there might be information in below nodes)
                self.split()  # This line should run every time once the leaf node is reached

                # REASONS FOR WHY WE PUT THE "ASSIGN OBJECTS TO CHILD QUADRANT" INSIDE "if self.nodes[0] == None:" INSTEAD OF OUTSIDE AND AFTER IT.
                # Assume that self.max_objects = 3
                # Case 1: 3 Irregular cases (Doesn't fully fit) at a leaf node. We add a regular case (Fully fits). As a result, we then split. We ten assign objects to child quadrants
                # Case 2: 3 Irregular cases not at a leaf node. We add a regular case. We don't split since regular cases can still keep on recurring down.

                # Below code assumes that that "self.split()" has been executed
                # Now, we look at all of the objects within the parent quadrant and send them to owned by the child quadrants
                i = 0
                while i < len(self.objects):  # The main thing about this line is that the len(self.objects) is not permanent and may change
                    obj = self.objects[i]
                    index = self.get_index(obj)
                    if index != -1:  # For objects that follow the "irregular items" / overlap case, we don't assign them to the child quadrants. Instead, the object remains as a part of the parent quadrant
                        del self.objects[i]  # This line changes the len(self.objects)
                        self.nodes[index].insert(obj)  # On top of just inserting the object into a child quadrant, we also gotta do another check to see if child quadrant is "stable" (Doesn't overpopulate)
                    else:  # The else statement accounts for the occasional size change of self.objects
                        i += 1

    def retrieve(self, return_objects, rect):
        # Description:
        # Given a rectangle, we start at the root level and traverse down until we find out the location where the rectangle is held (At a leaf/lowest quadrant)
        # We then bottom-up from the lowest level while taking:
                # 1: Rectangles that were also being held within the final level (alongside and including the rectangle)
                # 2: Any other rectangles that fell under the "irregular items" / overlap case
        # With these "return_objects", we use them to test collisions

        index = self.get_index(rect)
        if index != -1 and self.nodes[0] != None:
            self.nodes[index].retrieve(return_objects, rect)

        # Retrieval of leaf node objects happens once the dfs hits bottom
        # The getting of objects that were not fully within quadrants is super cool and is done as the dfs goes back up from bottom
        return_objects += self.objects  # Important thing here is that it picks all objects from leaf node AND any objects that were no fully within quadrants
                                        # The "return_objects" contents are NOT copied as we recur down. Rather, as we go down, we have a pointer pointing onto the memory location of "return_objects")

        return return_objects

    def draw_trees(self, screen):  # Used to draw quadtree lines

        # We basically continue recurring deeper as long as we aren't at a leaf leaf

        if self.nodes[0] != None:

            # Horizontal Line
            pygame.draw.line(screen, (0,0,0), (self.boundary.x, self.boundary.y + self.boundary.h/2), (self.boundary.x + self.boundary.w, self.boundary.y + self.boundary.h/2))
            # Vertical Line
            pygame.draw.line(screen, (0,0,0), (self.boundary.x + self.boundary.w/2, self.boundary.y), (self.boundary.x + self.boundary.w/2, self.boundary.y + self.boundary.h))

            for i in range(len(self.nodes)):
                self.nodes[i].draw_trees(screen)

