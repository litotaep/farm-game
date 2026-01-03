import json
import random as r
import time
import os
import sys


script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "saved_data.json")

class Plant:
    def __init__(self, name, growth_stages, growth_time):
        self.name = name
        self.growth_time= growth_time
        self.growth_stages = growth_stages
        self.current_stage = 0
        self.is_ripe = False
        self.planted_time = 0
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
    "tomatoes": Plant("tomatoes", [".","🪴","🍅"], 5),
    "potatoes": Plant("potatoes", ["*","🌿","🥔"], 10),
    "cucumbers": Plant("cucumbers",["O","🌱","🥒"], 15)
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
    save_field = []
    for row in field:
        save_row = []
        for cell in row:
            if cell is None:
                save_row.append(None)
            else:
                save_row.append({
                    "name": cell.name,
                    "stage": cell.current_stage,
                    "is_ripe": cell.is_ripe,
                    "planted_time": cell.planted_time
                })
        save_field.append(save_row)
    data = {
        "field": save_field,
        "inventory": inventory
    }
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            print("Successfully saved!")
    except Exception as e:
        print(f"Error {e}")

        
def show_field(field):
    check_growth(field = field)
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
    plant_template = get_plant(plants_species=plants_species) 
    
    if check_inventory(inventory, plant_template):
        new_plant = Plant(
            name=plant_template.name,
            growth_stages=plant_template.growth_stages.copy(), 
            growth_time=plant_template.growth_time
        )
        return new_plant  
    else:
        print(f"Not enough {plant_template.name} seeds! You have {inventory[plant_template.name]}")
        return None



def inventory_change(*, inventory, action, plant):
    if action == "planting_plant":
        inventory[plant.name] -= 1   
    elif action == "harvest":
        inventory[plant.name] += 2

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

def dict_to_object(*, field, plants_species):
    new_field = []
    current_time = time.time()
    for row in field:
        new_row = []
        for cell in row:
            if cell is None:
                new_row.append(None)
            else:
                plant_template = plants_species[cell["name"]]
                plant = Plant(
                    name=plant_template.name, 
                    growth_stages=plant_template.growth_stages,
                    growth_time=plant_template.growth_time)
                plant.current_stage = cell["stage"]
                plant.is_ripe = cell["is_ripe"]
                if "planted_time" in cell:
                    plant.planted_time = cell["planted_time"]
                    time_since_save = current_time - cell["planted_time"]
                    if time_since_save >= plant.growth_time:
                        plant.current_stage = len(plant.growth_stages) - 1 
                        plant.is_ripe = True
                    elif time_since_save >= plant.growth_time / 2:
                        plant.current_stage = 1 
            
            new_row.append(plant)
        new_field.append(new_row)
    return new_field

def check_saved_field(*, file_path):
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            data = json.load(f)
        for key in data: 
            if key== "field":
                field = data.get("field")
                object_field = dict_to_object(field=field, plants_species=plants_species)
                return object_field
        return None
    except FileNotFoundError: 
        return None
    except json.JSONDecodeError: 
        return None
    except Exception as e:
        print(f"Error: {e}") 

def planting(*,plant,x,y, field, inventory):
    if field[x][y] is None:
        field[x][y] = plant
        plant.planted_time = time.time()
        inventory_change(inventory=inventory, action="planting_plant", plant=plant)
    else:
        print("There is another plant in this cell")

def check_growth(*, field):
    current_time = time.time()
    for row in field:
        for plant in row:
            if plant is None:
                continue
            time_passed = current_time - plant.planted_time
            if plant.current_stage == 0 and time_passed >= plant.growth_time/2:
                plant.grow()
            elif plant.current_stage == 1 and time_passed >= plant.growth_time:
                plant.grow()
def harvest(*,x,y, field, inventory):
    if field[x][y] != None:
        plant = field[x][y]
        collected_plant = plant.harvest()
        if collected_plant is None:
            print(f"Sorry! The {plant.name} is not ready yet!")
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


