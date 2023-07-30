import random
import math
import sys

import comms
from object_types import ObjectTypes


class Game:
    """
    Stores all information about the game and manages the communication cycle.
    Available attributes after initialization will be:
    - tank_id: your tank id
    - objects: a dict of all objects on the map like {object-id: object-dict}.
    - width: the width of the map as a floating point number.
    - height: the height of the map as a floating point number.
    - current_turn_message: a copy of the message received this turn. It will be updated everytime `read_next_turn_data`
        is called and will be available to be used in `respond_to_turn` if needed.
    """
    def __init__(self):
        tank_id_message: dict = comms.read_message()
        self.tank_id = tank_id_message["message"]["your-tank-id"]
        self.enemy_id = tank_id_message["message"]["enemy-tank-id"]

        self.current_turn_message = None

        # We will store all game objects here
        self.objects = {}

        next_init_message = comms.read_message()
        while next_init_message != comms.END_INIT_SIGNAL:
            # At this stage, there won't be any "events" in the message. So we only care about the object_info.
            object_info: dict = next_init_message["message"]["updated_objects"]

            # Store them in the objects dict
            self.objects.update(object_info)

            # Read the next message
            next_init_message = comms.read_message()

        # We are outside the loop, which means we must've received the END_INIT signal

        # Let's figure out the map size based on the given boundaries

        # Read all the objects and find the boundary objects
        boundaries = []
        for game_object in self.objects.values():
            if game_object["type"] == ObjectTypes.BOUNDARY.value: 
                boundaries.append(game_object)

        # The biggest X and the biggest Y among all Xs and Ys of boundaries must be the top right corner of the map.

        # Let's find them. This might seem complicated, but you will learn about its details in the tech workshop.
        biggest_x, biggest_y = [
            max([max(map(lambda single_position: single_position[i], boundary["position"])) for boundary in boundaries])
            for i in range(2)
        ]

        self.width = biggest_x
        self.height = biggest_y

    def read_next_turn_data(self):
        """
        It's our turn! Read what the game has sent us and update the game info.
        :returns True if the game continues, False if the end game signal is received and the bot should be terminated
        """
        # Read and save the message
        self.current_turn_message = comms.read_message()

        if self.current_turn_message == comms.END_SIGNAL:
            return False

        # Delete the objects that have been deleted
        # NOTE: You might want to do some additional logic here. For example check if a powerup you were moving towards
        # is already deleted, etc.
        for deleted_object_id in self.current_turn_message["message"]["deleted_objects"]:
            try:
                del self.objects[deleted_object_id]
            except KeyError:
                pass

        # Update your records of the new and updated objects in the game
        # NOTE: you might want to do some additional logic here. For example check if a new bullet has been shot or a
        # new powerup is now spawned, etc.
        self.objects.update(self.current_turn_message["message"]["updated_objects"])

        return True

    def respond_to_turn(self):
        """
        This is where you should write your bot code to process the data and respond to the game.
        """

        # Write your code here... For demonstration, this bot just shoots randomly every turn.
        turn = {}
        #turn["shoot"] = self.shoot_at_enemy()
        #print(self.objects, file=sys.stderr)
        turn["path"] = self.path_find()
        
        comms.post_message(turn)

    def shoot_at_enemy(self):
        target_angle = 0
        self_x, self_y = self.objects[self.tank_id]["position"]
        enemy_x, enemy_y = self.objects[self.enemy_id]["position"]
        
        # Calculate distance to enemy tank to get angle 
        x_dist, y_dist = enemy_x - self_x, enemy_y - self_y
        if x_dist == 0: # If angle is 90 or 270
            angle = -90 if y_dist < 0 else 90
        else:
            angle = math.degrees(math.atan(y_dist / x_dist))
            # Flip angle if x_dist is negative
            angle = 180 + angle if x_dist < 0 else angle

        # calculate distance
        dist = math.sqrt(x_dist**2 + y_dist**2)

        inaccuracy_lim = int((45*dist)/(dist+100))
        angle += random.randint(-inaccuracy_lim,inaccuracy_lim)

        target_angle = angle % 360

        return target_angle


    def path_find(self):
        play_area = self.border_restriction()
        print(play_area, file=sys.stderr)
        random_move_x = random.randrange(int(play_area[0][0]), int(play_area[2][0]))
        random_move_y = random.randrange(int(play_area[2][1]), int(play_area[0][1]))
        return [random_move_x, random_move_y]

    def border_restriction(self) -> []:
        boundary = self.objects["closing_boundary-1"]["position"]
        hor_reduce = (boundary[3][0] - boundary[0][0]) * 0.1
        ver_reduce = (boundary[0][1] - boundary[1][1]) * 0.1

        new_border = []
        new_border.append([boundary[0][0] + hor_reduce, boundary[0][1] - ver_reduce]) # top_left
        new_border.append([boundary[1][0] + hor_reduce, boundary[1][1] + ver_reduce]) # bot_left
        new_border.append([boundary[2][0] - hor_reduce, boundary[2][1] + ver_reduce]) # bot_right
        new_border.append([boundary[3][0] - hor_reduce, boundary[3][1] - ver_reduce]) # top_right

        return new_border
    