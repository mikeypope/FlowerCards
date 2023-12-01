import os
import random
import sqlite3

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory=r"C:\Apps\FlowerCards\static"), name="static")
templates = Jinja2Templates(directory="templates")

# Connect to SQLite database
with sqlite3.connect("wildflowers.db") as conn:
    c = conn.cursor()

    # Define Flower and Species models
    class Image(BaseModel):
        species_name: str
        image: str

    class Species(BaseModel):
        species_name: str
        common_name: str
        family: str
        other_common_names: str
        characteristics: str
        location: str
        notes: str

        def to_dict(self):
            return {
                "species_name": self.species_name,
                "common_name": self.common_name,
                "family": self.family,
                "other_common_names": self.other_common_names,
                "characteristics": self.characteristics,
                "location": self.location,
                "notes": self.notes,
            }

    # Load images and species list from SQLite database
    c.execute("SELECT species_name, image FROM images")
    images = [Image(species_name=row[0], image=row[1]) for row in c.fetchall()]
    
    c.execute("SELECT species_name, common_name, family, other_common_names, characteristics, location, notes FROM species")
    species = [Species(**dict(zip(('species_name', 'common_name', 'family', 'other_common_names', 'characteristics', 'location', 'notes'), row))) for row in c.fetchall()]

@app.get("/")
async def index(request: Request, error: str = ""):
    # Choose a random flower and create a list of 4 species names (including the correct answer)
    flower = random.choice(images)
    species_list = [s.species_name for s in species if s.species_name != flower.species_name]
    choices = random.sample(species_list, 3)
    choices.append(flower.species_name)
    random.shuffle(choices)

    # Get all images for the chosen flower's species
    species_images = [i.image for i in images if i.species_name.lower() == flower.species_name.lower()]

    # Convert image path to a relative path for use in the template
    def convert_image_paths(image_path):
        return 'static/' + image_path.replace("\\", "/").replace("C:/Apps/FlowerCards", 'SpeciesDetail')

    species_images_converted = [convert_image_paths(image) for image in species_images]

    # Use dictionary lookups to retrieve species information
    species_info = {s.species_name: s.to_dict() for s in species}
    
      
    # Render the HTML template with the chosen flower, list of species names, and error message (if any)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "flower": flower,
            "choices": choices,
            "error": error,
            "flowerimagepath": species_images_converted[0],
            "species_info": species_info.get(flower.species_name, {}),
            "species_images_converted": species_images_converted
        }
    )

# Define Other Images route
@app.get("/species/{species_name}/image")
async def species_image(request: Request, species_name: str):
    # Get all images for the specified species
    species_images = [i.image for i in images if i.species_name.lower() == species_name.lower()]

    if not species_images:
        # Return a 404 error if no images were found for the specified species
        return Response(status_code=404)

    # Convert image path to a relative path for use in the template
    def convert_image_paths(image_path):
        return 'static/' + image_path.replace("\\", "/").replace("C:/Apps/FlowerCards", 'SpeciesDetail')

    species_images_converted = [convert_image_paths(image) for image in species_images]

    # Choose a random image from the list
    image_path = random.choice(species_images_converted)

    # Render the HTML template with the new image src
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "flowerimagepath": image_path
        }
    )