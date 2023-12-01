import os
import sqlite3

from fastapi import FastAPI
from pydantic import BaseModel

class Species(BaseModel):
    species_name: str
    common_name: str
    family: str
    other_common_names: str
    characteristics: str
    location: str
    notes: str

def parse_text_file(species_summary_file):
    common_name = ""
    species_name = ""
    family = ""
    other_common_names = ""
    characteristics = ""
    location = ""
    notes = ""
    with open(species_summary_file, "r") as file:
        lines = file.readlines()
        common_name = lines[0].strip()
        species_name = lines[1].strip()
        for line in lines:
            if line.startswith("Family:"):
                family = line.split(":")[1].strip()
            elif line.startswith("Other common names:"):
                other_common_names = line.split(":")[1].strip()
            elif line.startswith("Characteristics:"):
                characteristics = line.split(":")[1].strip()
            elif line.startswith("Location:"):
                location = line.split(":")[1].strip()
            elif line.startswith("Note:"):
                notes = line.split(":")[1].strip()
    return common_name, species_name, family, other_common_names, characteristics, location, notes

# Connect to SQLite database
conn = sqlite3.connect("wildflowers.db")
c = conn.cursor()

# Create Images and Species tables in SQLite database
c.execute('''CREATE TABLE IF NOT EXISTS images
             (species_name text, image text)''')
c.execute('''CREATE TABLE IF NOT EXISTS species
             (species_name text, common_name text, family text, other_common_names text, characteristics text, location text, notes text)''')

# Populate Species table from summary text files
species_dirs = [d for d in os.listdir(r"C:\Apps\FlowerCards\static\SpeciesDetail") if os.path.isdir(os.path.join(r"C:\Apps\FlowerCards\static\SpeciesDetail", d))]

for species_dir in species_dirs:
    species_name = species_dir.lower()
    species_summary_file = os.path.join(r"C:\Apps\FlowerCards\static\SpeciesDetail", species_dir, species_dir + "summary.txt")
    
    if not os.path.exists(species_summary_file):
        print(f"No summary file found for {species_name}")
        continue
    common_name, species_name, family, other_common_names, characteristics, location, notes = parse_text_file(species_summary_file)
        
    # Insert species record into Species table
    c.execute("INSERT INTO species VALUES (?, ?, ?, ?, ?, ?, ?)", (species_name, common_name, family, other_common_names, characteristics, location, notes))
    
     # Add images to Images table
    species_images = [os.path.abspath(os.path.join(species_dir, f)) for f in os.listdir(os.path.join(r"C:\Apps\FlowerCards\static\SpeciesDetail", species_dir)) if f.endswith(".png")]
    for image_path in species_images:
        c.execute("INSERT INTO images VALUES (?, ?)", (species_name, image_path))
conn.commit()
conn.close()
