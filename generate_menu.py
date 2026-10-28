import zipfile
import xml.etree.ElementTree as ET
import json
import re

# Read directly from docx to avoid encoding issues
with zipfile.ZipFile('Dine In Menu 8.10.26.docx') as z:
    xml_content = z.read('word/document.xml')

tree = ET.fromstring(xml_content)
raw_lines = []
for elem in tree.iter():
    if elem.tag.endswith('}p'):
        p_text = ''.join(elem.itertext()).strip()
        if p_text:
            # Clean up character replacements
            cleaned = p_text.replace('\ufffd', ' — ').replace('  ', ' ')
            raw_lines.append(cleaned)

category_defs = [
    {
        'id': 'egg-dosas',
        'name': 'Classic & Spiced Egg Dosas',
        'description': 'Crispy golden rice crepes layered with seasoned eggs, Andhra karam, and coastal ghee roasts.',
        'icon': '🥞'
    },
    {
        'id': 'idly-vada',
        'name': 'Idly & Vada',
        'description': 'Hot steamed idlies, crispy vadas, pepper fry and ghee roast South Indian morning classics.',
        'icon': '🥟'
    },
    {
        'id': 'english-breakfast',
        'name': 'English Breakfast (2 Eggs)',
        'description': 'Farm-fresh 2-egg preparations: Sunny side up, poached, scramble, bhurji and Benedict.',
        'icon': '🍳'
    },
    {
        'id': 'omelets-frittatas',
        'name': 'The Omelet Connoisseur',
        'description': 'French butter omelets, fluffy cheese skillets, Goan Ros, garden harvest and Spanish frittatas.',
        'icon': '🧀'
    },
    {
        'id': 'starters-fusion',
        'name': 'Starters & Fusion Bites',
        'description': 'Wok-tossed Manchurian, Egg 65, Mangalorean ghee roasts, butter garlic and crispy peri-peri.',
        'icon': '🔥'
    },
    {
        'id': 'breakfast-platters',
        'name': 'Signature Breakfast Platters',
        'description': 'Hearty morning platters with sausages, eggs to order, hash browns, pancakes and French toast.',
        'icon': '🍽️'
    },
    {
        'id': 'egg-specials',
        'name': 'Egg Specials & Gratins',
        'description': 'Kashmiri eggs, Middle Eastern Shakshuka, Egg Pani Puri, Surat egg fry and cheesy gratins.',
        'icon': '⭐'
    },
    {
        'id': 'chef-specials',
        'name': 'Chef Special Inventions',
        'description': 'Surti Egg Locha, Egg Loziz, Scotch eggs, Smoky BBQ bites, tacos and savory French toast.',
        'icon': '👨‍🍳'
    },
    {
        'id': 'signature-rolls',
        'name': 'Signature Rolls',
        'description': 'Flaky toasted parathas loaded with egg ghee roast and melted mozzarella.',
        'icon': '🌯'
    },
    {
        'id': 'soups-broths',
        'name': 'Soups & Broths',
        'description': 'Silky egg drop soups, spicy Manchow, Indo-Chinese Lung Fung, and Mexican poached egg broth.',
        'icon': '🥣'
    },
    {
        'id': 'artisan-egg-rice',
        'name': 'Artisan Egg Rice Selection',
        'description': 'Bangalore street egg rice, Japanese Omurice, Korean Gyeran Bap, Mexican and Palak egg rice.',
        'icon': '🍚'
    },
    {
        'id': 'street-noodles',
        'name': 'Wok-Fried Street Noodles',
        'description': 'Indo-Chinese Manchurian noodles, aromatic Thai basil and classic Hakka noodles.',
        'icon': '🍜'
    },
    {
        'id': 'maggi-chronicles',
        'name': 'The Maggi Chronicles',
        'description': 'Silky Egg Drop Maggi, fiery Szechwan dry, crispy fry and our signature Maggi Egg Frittata.',
        'icon': '🍲'
    },
    {
        'id': 'burgers-sandwiches',
        'name': 'Craft Burgers & Sandwiches',
        'description': 'Crispy egg patty burgers, 4-egg smash burgers, Korean Gilgeori toast and chili cheese toasties.',
        'icon': '🍔'
    },
    {
        'id': 'pizzas-sizzlers',
        'name': 'Gourmet Pizzas & Sizzlers',
        'description': 'Chettinad and Surti Ghotala pizzas, plus sizzling Chinese egg & Mexican paneer platters.',
        'icon': '♨️'
    },
    {
        'id': 'salads-meals',
        'name': 'Salads & Main Meals',
        'description': 'Nicoise & Caesar egg salads, dum biryanis, Egg Kothu Parotta and unlimited Andhra thali.',
        'icon': '🥗'
    },
    {
        'id': 'sweets-desserts',
        'name': 'Sweets & Desserts',
        'description': 'Classic Cream Caramel, Bread Butter Pudding with hot chocolate, Bombe Alaska & Blueberry Cheesecake.',
        'icon': '🍰'
    },
    {
        'id': 'beverages-coolers',
        'name': 'Coolers, Shakes & Goli Sodas',
        'description': 'Mojitos, thickshakes, authentic nostalgic Goli Sodas (Jeera, Kala Khatta, Limbu, Nannari).',
        'icon': '🥤'
    },
    {
        'id': 'hot-beverages',
        'name': 'Hot Beverages',
        'description': 'Authentic freshly brewed chai, ginger tea, masala tea, and traditional hot filter coffee.',
        'icon': '☕'
    }
]

section_headers = [
    ('Classic & Spiced Egg Dosas', 'egg-dosas', 'Classic & Spiced Egg Dosas'),
    ('IDLY & VADA', 'idly-vada', 'Idly & Vada'),
    ('English Breakfast (2 Eggs)', 'english-breakfast', 'English Breakfast (2 Eggs)'),
    ('THE OMELET CONNOISSEUR', 'omelets-frittatas', 'The Omelet Connoisseur'),
    ('Continental & Classic Omelets', 'omelets-frittatas', 'The Omelet Connoisseur'),
    ('Spiced & Regional Traditions', 'omelets-frittatas', 'The Omelet Connoisseur'),
    ('Wholesome & Garden Harvest', 'omelets-frittatas', 'The Omelet Connoisseur'),
    ('International Skillets', 'omelets-frittatas', 'The Omelet Connoisseur'),
    ('Starters Fusion Flavors', 'starters-fusion', 'Starters & Fusion Bites'),
    ('Signature Breakfast Platters', 'breakfast-platters', 'Signature Breakfast Platters'),
    ('Egg Specials', 'egg-specials', 'Egg Specials & Gratins'),
    ('Chef Special', 'chef-specials', 'Chef Special Inventions'),
    ('SIGNATURE ROLLS', 'signature-rolls', 'Signature Rolls'),
    ('Soups & Broths', 'soups-broths', 'Soups & Broths'),
    ('Artisan Egg Rice Selection', 'artisan-egg-rice', 'Artisan Egg Rice Selection'),
    ('Wok-Fried Street Noodles', 'street-noodles', 'Wok-Fried Street Noodles'),
    ('THE MAGGI CHRONICLES', 'maggi-chronicles', 'The Maggi Chronicles'),
    ('SIGNATURE CRAFT BURGERS', 'burgers-sandwiches', 'Craft Burgers & Sandwiches'),
    ('Sandwich', 'burgers-sandwiches', 'Craft Burgers & Sandwiches'),
    ('Gourmet Egg Pizza', 'pizzas-sizzlers', 'Gourmet Pizzas & Sizzlers'),
    ('Sizzlers', 'pizzas-sizzlers', 'Gourmet Pizzas & Sizzlers'),
    ('SALADS', 'salads-meals', 'Salads & Main Meals'),
    ('Main Couse', 'salads-meals', 'Salads & Main Meals'),
    ('SWEETS', 'sweets-desserts', 'Sweets & Desserts'),
    ('Coolers', 'beverages-coolers', 'Coolers, Shakes & Goli Sodas'),
    ('Shakes', 'beverages-coolers', 'Coolers, Shakes & Goli Sodas'),
    ('Goli Sodas', 'beverages-coolers', 'Coolers, Shakes & Goli Sodas'),
    ('Hot Beverage', 'hot-beverages', 'Hot Beverages')
]

skip_phrases = [
    'Menu',
    'Gourmet Whisked Specialties & Fluffy Skillets',
    'Served With Fries',
    'CUSTOMIZE YOUR SKILLET (ADD EXTRAS)',
    'Extra Whole Egg:',
    '(rice, papu, rasam, sambar, palyam, podi, pickals ,curd, chapathi)'
]

cur_cat_id = 'egg-dosas'
cur_cat_name = 'Classic & Spiced Egg Dosas'

dishes = []
i = 0
dish_counter = 1

while i < len(raw_lines):
    line = raw_lines[i].strip()
    
    # Skip meta lines
    if any(line == sp or line.startswith('Extra Whole Egg:') or line.startswith('(rice, papu') for sp in skip_phrases):
        i += 1
        continue

    # First check if this line is a dish (has price)
    # Handles: 'Egg Dosa119', 'Paneer / Egg Bhurji Dosa 179/159', 'Egg Mandi  369  (for 2)'
    m = re.search(r'^(.*?)\s*(\d+(?:\s*/\s*\d+)?)(?:\s*(\(for \d+\)))?\s*$', line)
    
    # If it is NOT a dish, check if it's a section header
    if not m or any(line.lower() == sh[0].lower() for sh in section_headers):
        matched_sec = False
        for sh_name, cat_id, cat_name in section_headers:
            if line.lower() == sh_name.lower() or line.lower().startswith(sh_name.lower()):
                cur_cat_id = cat_id
                cur_cat_name = cat_name
                matched_sec = True
                break
        if matched_sec:
            i += 1
            continue

    if m:
        d_name = m.group(1).strip()
        price_str = m.group(2).strip().replace(' ', '')
        portion_note = m.group(3)
        if portion_note:
            d_name += f" {portion_note}"

        # Clean name from trailing dashes or typos
        d_name = d_name.rstrip(' -—:')

        # Check if next line is a description
        desc = ''
        if i + 1 < len(raw_lines):
            nxt = raw_lines[i+1].strip()
            nxt_is_sec = any(nxt.lower() == sh[0].lower() or nxt.lower().startswith(sh[0].lower()) for sh in section_headers)
            nxt_is_skip = any(nxt == sp or nxt.startswith('Extra') or nxt.startswith('(rice') for sp in skip_phrases)
            nxt_has_price = bool(re.search(r'\d+(?:\s*/\s*\d+)?(?:\s*\(for \d+\))?\s*$', nxt))
            
            # If next line does NOT have a price and is not a section header, it is a description
            if not nxt_is_sec and not nxt_is_skip and not nxt_has_price:
                desc = nxt
                i += 1
        
        if '/' in price_str:
            price_val = price_str
        else:
            try:
                price_val = int(price_str)
            except ValueError:
                price_val = price_str
            
        tags = []
        name_lower = d_name.lower()
        desc_lower = desc.lower()
        
        is_spicy = any(k in name_lower or k in desc_lower for k in ['spicy', 'chili', 'chilli', 'karam', 'peri peri', 'szechwan', 'pepper', 'fiery', 'schezwan', 'tandoori'])
        is_protein = any(k in name_lower or k in desc_lower for k in ['protein', 'pesarattu', 'gym', 'smash', '4 egg', 'paneer', 'tofu', 'quinoa'])
        is_chef = any(k in name_lower or k in desc_lower for k in ['chef', 'special', 'kashmiri', 'locha', 'loziz', 'shakshuka', 'mandi', 'bombe', 'fusion', 'dragon', 'sprunch', 'nicoise'])
        is_bestseller = any(k in name_lower or k in desc_lower for k in ['timeless classic', 'bestseller', 'ghee roast', 'butter omelet', 'ghotala', 'bangalore street', 'english breakfast', 'all english', 'maggi frittata', 'spanish frittata', 'cheese omelet', 'biryani', 'mojito'])
        
        if is_bestseller:
            tags.append('Bestseller')
        if is_chef:
            tags.append("Chef's Special")
        if is_protein:
            tags.append('High Protein')
        if is_spicy:
            tags.append('Spicy')
            
        spice_level = 0
        if any(k in name_lower or k in desc_lower for k in ['fiery', 'szechwan', 'karam', 'spicy']):
            spice_level = 2
        elif any(k in name_lower or k in desc_lower for k in ['pepper', 'peri peri', 'chili', 'schezwan']):
            spice_level = 1
            
        is_pure_veg = any(k in name_lower for k in ['idly', 'vada', 'paneer ghee roast', 'paneer butter garlic', 'tofu pepper', 'mushrooms', 'sweet corn soup', 'veg manchow', 'chole bhatura', 'andhra meals', 'cream caramel', 'bread butter', 'bombe alaska', 'blue berry', 'mojito', 'guava', 'tea', 'coffee', 'soda', 'shake', 'virgin']) and not any(k in name_lower for k in ['egg', 'omelet', 'bhurji', 'poached', 'scramble', 'frittata'])
        dietary = 'Veg' if is_pure_veg else 'Egg'
        
        eggs_used = 0
        if not is_pure_veg:
            if '4 egg' in name_lower or '4 eggs' in name_lower:
                eggs_used = 4
            elif '2 pieces' in name_lower or '2 egg' in name_lower or '2 half' in name_lower or 'two egg' in desc_lower or 'two fried' in desc_lower:
                eggs_used = 2
            elif 'quail' in desc_lower:
                eggs_used = 6
            else:
                eggs_used = 1
                
        dish_id = f'dish-{dish_counter:03d}'
        dish_counter += 1
        
        dishes.append({
            'id': dish_id,
            'name': d_name,
            'categoryId': cur_cat_id,
            'categoryName': cur_cat_name,
            'price': price_val,
            'description': desc if desc else f'Signature café preparation crafted fresh with artisanal ingredients.',
            'tags': tags if tags else ['House Specialty'],
            'dietary': dietary,
            'spiceLevel': spice_level,
            'eggsUsed': eggs_used
        })
    i += 1

output_data = {
    'categories': category_defs,
    'totalCount': len(dishes),
    'dishes': dishes
}

with open('src/data/menu.json', 'w', encoding='utf-8') as out:
    json.dump(output_data, out, indent=2, ensure_ascii=False)

print(f"Generated src/data/menu.json with {len(category_defs)} categories and {len(dishes)} authentic dishes!")
