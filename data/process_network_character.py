import json

# Load the JSON data
with open('data/raw/characters.json', 'r') as f:
    data = json.load(f)

# Initialize lists for nodes and links
nodes = []
links = []
node_ids = set()  # Track existing node IDs

# Track bidirectional relationships to avoid duplicates
bidirectional_pairs = set()

# Helper function to add bidirectional relationships
def add_bidirectional_link(source, target, category):
    # Create a sorted tuple of the pair to ensure consistent ordering
    pair = tuple(sorted([source, target]))
    pair_with_category = (pair[0], pair[1], category)
    
    # Only add if this pair hasn't been seen before
    if pair_with_category not in bidirectional_pairs:
        links.append({
            "source": source,
            "target": target,
            "category": category
        })
        bidirectional_pairs.add(pair_with_category)

# Process each character
for character in data['characters']:
    # Add node
    node = {
        "id": character['characterName'],
        "characterImageThumb": character.get('characterImageThumb', ''),
        "characterImageFull": character.get('characterImageFull', '')
    }
    nodes.append(node)
    node_ids.add(character['characterName'])
    
    # Process relationships
    # Unidirectional relationships
    if 'killed' in character:
        for target in character['killed']:
            links.append({
                "source": character['characterName'],
                "target": target,
                "category": "Kills"
            })
            
    if 'serves' in character:
        for target in character['serves']:
            links.append({
                "source": character['characterName'],
                "target": target,
                "category": "Serves"
            })
            
    if 'guardianOf' in character:
        for target in character['guardianOf']:
            links.append({
                "source": character['characterName'],
                "target": target,
                "category": "GuardianOf"
            })
            
    if 'parents' in character:
        for target in character['parents']:
            links.append({
                "source": target,
                "target": character['characterName'],
                "category": "ParentOf"
            })
    
    # Bidirectional relationships
    if 'allies' in character:
        for target in character['allies']:
            add_bidirectional_link(character['characterName'], target, "Allies")
            
    if 'siblings' in character:
        for target in character['siblings']:
            add_bidirectional_link(character['characterName'], target, "Siblings")
            
    if 'marriedEngaged' in character:
        for target in character['marriedEngaged']:
            add_bidirectional_link(character['characterName'], target, "Married")

# After all links are processed, add missing nodes
all_referenced_ids = set()
for link in links:
    all_referenced_ids.add(link['source'])
    all_referenced_ids.add(link['target'])

# Add missing nodes
for node_id in all_referenced_ids:
    if node_id not in node_ids:
        nodes.append({
            "id": node_id,
            "characterImageThumb": "",
            "characterImageFull": ""
        })

# Save nodes to file
with open('data/processed/got_network_nodes.json', 'w') as f:
    json.dump(nodes, f, indent=2)

# Save links to file
with open('data/processed/got_network_links.json', 'w') as f:
    json.dump(links, f, indent=2)
