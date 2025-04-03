#!/bin/bash

# Define the list of folders
folders=(
    "town_hall"
    "clan_castle"
    "wall"
    "army_camp"
    "barracks"
    "laboratory"
    "spell_factory"
    "builder's_hut"
    "elixir_collector"
    "gold_mine"
    "elixir_storage"
    "gold_storage"
    "cannon"
    "archer_tower"
    "mortar"
    "air_defense"
    "wizard_tower"
)

# Create each folder if it does not exist
for folder in "${folders[@]}"; do
    mkdir -p "$folder"
    echo "Created: $folder"
done

echo "All folders created successfully!"

