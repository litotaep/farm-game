import json
import random as r
import time
import os
import sys


script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "saved_data.json")

class Plant:
    def __init__(self, name, growth_stages):
        self.name = name
        self.growth_stages = growth_stages
        self.current_stage = 0
        self.is_ripe = False
    @property
    def symbol(self):
        return self.growth_stages[self.current_stage]
    
    def grow(self):
        if self.current_stage < len(self.growth_stages)-1:
            self.current_stage += 1
            if self.current_stage == len(self.growth_stages)-1:
                self.is_ripe = True
            return True
        return False
    def harvest(self):
        if self.is_ripe == True:
            return self.name
        return None


    

plants_species = {
    "tomatoes": Plant("tomatoes", [".","🪴","🍅"]),
    "potatoes": Plant("potatoes", ["*","🌿","🥔"]),
    "cucumbers": Plant("cucumbers",["O","🌱","🥒"])
}



def create_new_field(width_and_height):
    field = []
    for i in range (width_and_height):
        row = []
        for j in range (width_and_height):
            row.append(None)
        field.append(row)    
    return field


def save_data(*, field, inventory, file_path):  
    try:
        data = {
            "field" : field,
            "inventory": inventory
        } 
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            print("Successfully saved!")
    except Exception as e:
        print(f"Error {e}")

        
def show_field(field):
    for x in range(len(field)):
        row_display = []
        for y in range(len(field)):
            cell = field[x][y]  
            if cell is None:  
                row_display.append("|0|")
            else:  
                row_display.append(cell.symbol)  
        print(" ".join(row_display))  
        

def show_inventory(inventory):
    for plants, quantity in inventory.items():
        print(f"{plants}: {quantity}")
        print()


def get_plant(*, plants_species):
    while True:
        plants = input("Enter plant name or symbol: ")
        if plants in plants_species:  
            return plants_species[plants]
        for plant_name, plant_object in plants_species.items():
            if plants == plant_object.symbol:
                return plants_species[plant_name] 
        print(f"there is no '{plants}' plant. Available: {list(plants_species.keys())}")



def check_inventory(inventory, plant):
    if plant.name not in inventory:
        print("You don't have this plant")
        return False
    return inventory[plant.name] > 0 
    


def share_plant(plant_spieces, inventory):
    plant = get_plant(plants_species=plants_species)
    if check_inventory(inventory, plant):
        return plant
    print(f"Not enough {plant.name} seeds! You have {inventory[plant.name]}")  
    return None



def inventory_change(*, inventory, action, plant):
    if action == "planting_plant":
        inventory[plant.name] -= 1   
    elif action == "harvest":
        inventory[plant.name] += 1

def get_coordinates(field_size):
    while True:
        coordinates = input("Enter coordinates (row col): ")
        coordinates = coordinates.split()
        if len(coordinates) == 2:
            try:
                x = int(coordinates[0])
                y = int(coordinates[1])
                if 0 <= x < field_size and 0 <= y < field_size:
                    return x, y
                else:
                    print(f"coordinates must be in field: {field_size-1} x {field_size-1}")
            except ValueError:
                print("Error: That is not an integer! Try again!")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Please enter exactly 2 numbers!") 
            continue
        


def check_saved_inventory(*, file_path):
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            data = json.load(f)
        for key in data: 
            if key== "inventory":
                inventory = data.get("inventory")
                return inventory
        return None
    except FileNotFoundError: 
        return None
    except json.JSONDecodeError: 
        return None
    except Exception as e:
        print(f"Error: {e}")

def check_saved_field(*, file_path):
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            data = json.load(f)
        for key in data: 
            if key== "field":
                field = data.get("field")
                return field
        return None
    except FileNotFoundError: 
        return None
    except json.JSONDecodeError: 
        return None
    except Exception as e:
        print(f"Error: {e}") 

def planting(*,plant,x,y, field, inventory):
    field[x][y] = plant
    inventory_change(inventory=inventory, action="planting_plant", plant=plant)

        
def harvest(*,x,y, field, inventory):
    if field[x][y] != None:
        plant = field[x][y]
        collected_plant = plant.harvest()
        if collected_plant is None:
            print(f"Sorry! The {collected_plant} is not ready yet!")
            return
        field[x][y] = None
        print(f"{plant.name} successfully collected!")
        inventory_change(inventory=inventory, action="harvest", plant=plant)
         
    else:
        print("The cell is empty!!!")

def game_loop(field, inventory):
    show_field(field)
    while True:
        answer = input("\n1. Inventory\n2. Plant\n3. Show field\n4. Save\n5. Harvest\n6. Quit\nChoose (1-6): ")
        if answer == "1":
            show_inventory(inventory)
        elif answer == "2":
            x, y = get_coordinates(len(field))
            plant = share_plant(plants_species, inventory)
            if plant != None:
                planting(plant=plant, x=x, y=y, field=field, inventory=inventory)
                show_field(field)
            else: 
                continue
        elif answer == "3":
            show_field(field)
        elif answer == "4":
            save_data(field=field,inventory=inventory ,file_path=file_path)
        elif answer == "5":
            x, y = get_coordinates(len(field))
            harvest(x=x, y=y, field=field, inventory=inventory)
        elif answer == "6":
            sys.exit()
        

def main_game():
    while True:
        is_new_game = input("Do you want to start a new game or continue your last game?(new/continue) ")
        inventory = {
            "tomatoes": 0,
            "potatoes": 3,
            "cucumbers": 3
        }

        if is_new_game == "new":
            field = create_new_field(3)
            game_loop(field, inventory)
            break  
        elif is_new_game == "continue":
            field = check_saved_field(file_path=file_path)
            inventory = check_saved_inventory(file_path=file_path)
            if field is not None:
                game_loop(field, inventory)
                break
            else:
                print("No saved game found")
                
        else:
            print("Invalid choice")
main_game()    



# inventory = {
#             "tomatoes": 0,
#             "potatoes": 3,
#             "cucumbers": 3
#         }
# field = create_new_field(3)
# x, y = get_coordinates(len(field))
# plant = share_plant(plants_species, inventory) 
# if plant is not None:   
#     planting(seed=plant.name, plant=plant, x=x, y=y, field=field, inventory=inventory)
# show_field(field)