import zipfile
import xml.etree.ElementTree as ET
import json
import re

# 1. Read document.xml from docx
with zipfile.ZipFile('Dine In Menu 8.10.26.docx') as z:
    xml_content = z.read('word/document.xml')

tree = ET.fromstring(xml_content)
raw_lines = []
for elem in tree.iter():
    if elem.tag.endswith('}p'):
        text = ''.join(elem.itertext()).strip()
        if text:
            # Clean non-standard unicode characters
            cleaned = text.replace('\ufffd', '-').replace('  ', ' ').strip()
            raw_lines.append(cleaned)

# Category metadata
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

# Section headers mapping (lowercase match)
section_map = {
    'classic & spiced egg dosas': ('egg-dosas', 'Classic & Spiced Egg Dosas'),
    'idly & vada': ('idly-vada', 'Idly & Vada'),
    'english breakfast (2 eggs)': ('english-breakfast', 'English Breakfast (2 Eggs)'),
    'the omelet connoisseur': ('omelets-frittatas', 'The Omelet Connoisseur'),
    'continental & classic omelets': ('omelets-frittatas', 'The Omelet Connoisseur'),
    'spiced & regional traditions': ('omelets-frittatas', 'The Omelet Connoisseur'),
    'wholesome & garden harvest': ('omelets-frittatas', 'The Omelet Connoisseur'),
    'international skillets': ('omelets-frittatas', 'The Omelet Connoisseur'),
    'starters fusion flavors': ('starters-fusion', 'Starters & Fusion Bites'),
    'signature breakfast platters': ('breakfast-platters', 'Signature Breakfast Platters'),
    'egg specials': ('egg-specials', 'Egg Specials & Gratins'),
    'chef special': ('chef-specials', 'Chef Special Inventions'),
    'signature rolls': ('signature-rolls', 'Signature Rolls'),
    'soups & broths': ('soups-broths', 'Soups & Broths'),
    'artisan egg rice selection': ('artisan-egg-rice', 'Artisan Egg Rice Selection'),
    'wok-fried street noodles': ('street-noodles', 'Wok-Fried Street Noodles'),
    'the maggi chronicles': ('maggi-chronicles', 'The Maggi Chronicles'),
    'signature craft burgers': ('burgers-sandwiches', 'Craft Burgers & Sandwiches'),
    'sandwich': ('burgers-sandwiches', 'Craft Burgers & Sandwiches'),
    'gourmet egg pizza': ('pizzas-sizzlers', 'Gourmet Pizzas & Sizzlers'),
    'gourmet egg pizza 9"': ('pizzas-sizzlers', 'Gourmet Pizzas & Sizzlers'),
    'gourmet egg pizza 9-': ('pizzas-sizzlers', 'Gourmet Pizzas & Sizzlers'),
    'sizzlers': ('pizzas-sizzlers', 'Gourmet Pizzas & Sizzlers'),
    'salads': ('salads-meals', 'Salads & Main Meals'),
    'main couse (meals)': ('salads-meals', 'Salads & Main Meals'),
    'main course (meals)': ('salads-meals', 'Salads & Main Meals'),
    'sweets': ('sweets-desserts', 'Sweets & Desserts'),
    'coolers': ('beverages-coolers', 'Coolers, Shakes & Goli Sodas'),
    'shakes': ('beverages-coolers', 'Coolers, Shakes & Goli Sodas'),
    'goli sodas 300ml': ('beverages-coolers', 'Coolers, Shakes & Goli Sodas'),
    'goli sodas': ('beverages-coolers', 'Coolers, Shakes & Goli Sodas'),
    'hot beverage-s': ('hot-beverages', 'Hot Beverages'),
    'hot beverages': ('hot-beverages', 'Hot Beverages')
}

meta_skips = [
    'menu',
    'gourmet whisked specialties & fluffy skillets',
    'served with fries',
    'customize your skillet (add extras)'
]

cur_cat_id = 'egg-dosas'
cur_cat_name = 'Classic & Spiced Egg Dosas'
cur_sub_category = 'Dosas'

dishes = []
i = 0
dish_counter = 1

while i < len(raw_lines):
    line = raw_lines[i].strip()
    low = line.lower()

    # Skip top titles / meta phrases
    if low in meta_skips or low.startswith('extra whole egg:'):
        i += 1
        continue

    # Check for section header match
    matched_sec = False
    for sh_key, (c_id, c_name) in section_map.items():
        if low == sh_key or low.startswith(sh_key):
            cur_cat_id = c_id
            cur_cat_name = c_name
            if 'coolers' in low:
                cur_sub_category = 'Coolers'
            elif 'shakes' in low:
                cur_sub_category = 'Thickshakes'
            elif 'goli soda' in low:
                cur_sub_category = 'Goli Sodas'
            elif 'hot beverage' in low:
                cur_sub_category = 'Hot Beverages'
            matched_sec = True
            break

    if matched_sec:
        i += 1
        continue

    # Check for special multi-line descriptions
    if low.startswith('(rice, papu'):
        if dishes and 'andhra' in dishes[-1]['name'].lower():
            dishes[-1]['description'] = f"Traditional unlimited Andhra thali: {line.strip('()')}"
        i += 1
        continue

    if low.startswith('a sizzling sensory delight'):
        if dishes and 'sizzler' in dishes[-1]['name'].lower():
            dishes[-1]['description'] = line
        i += 1
        continue

    # Identify if current line is a dish line
    d_name = None
    portion_note = ''

    # Handle Egg 65 and Egg Gongura 65 edge case where price was directly attached
    if re.search(r'65\s*249', line):
        m_65 = re.match(r'^(.*?65)\s*249$', line)
        if m_65:
            d_name = m_65.group(1).strip()
    else:
        # Standard dish pattern: Name followed by price (e.g. 119 or 179/159 or with (for 2))
        m_dish = re.search(r'^(.*?)\s*(\d+(?:\s*/\s*\d+)?)(?:\s*(\(for \d+\)))?\s*$', line)
        if m_dish:
            d_name = m_dish.group(1).strip()
            if m_dish.group(3):
                portion_note = m_dish.group(3).strip()

    if d_name:
        # Clean trailing dashes, hyphens, colons
        d_name = d_name.rstrip(' -—:')
        if portion_note:
            d_name += f" {portion_note}"

        # Clean specific typo names
        if d_name.lower() == 'bue lagoon':
            d_name = 'Blue Lagoon Cooler'
        elif d_name.lower() == 'sunrise':
            d_name = 'Sunrise Mocktail Cooler'
        elif d_name.lower() == 'oreo':
            d_name = 'Oreo Thickshake'
        elif d_name.lower() == 'strawberry':
            d_name = 'Strawberry Thickshake'
        elif d_name.lower() == 'nutella':
            d_name = 'Nutella Thickshake'
        elif d_name.lower() == 'virgin pina colada':
            d_name = 'Virgin Piña Colada'
        elif d_name.lower() == 'masala butter milk':
            d_name = 'Masala Buttermilk'
        elif d_name.lower() == 'masala jeera soda':
            d_name = 'Masala Jeera Goli Soda'
        elif d_name.lower() == 'cola soda':
            d_name = 'Cola Goli Soda'
        elif d_name.lower() == 'kala khatta soda':
            d_name = 'Kala Khatta Goli Soda'
        elif d_name.lower() == 'limbu soda':
            d_name = 'Limbu (Lemon) Goli Soda'
        elif d_name.lower() == 'pan masala soda':
            d_name = 'Paan Masala Goli Soda'
        elif d_name.lower() == 'nannari soda':
            d_name = 'Nannari Goli Soda'
        elif d_name.lower() == 'milk nannari':
            d_name = 'Milk Nannari Goli Soda'
        elif d_name.lower() == 'egg kothu parrota':
            d_name = 'Egg Kothu Parotta'
        elif d_name.lower() == 'egg ceasar salad':
            d_name = 'Egg Caesar Salad'

        # Look ahead for description
        desc = ''
        if i + 1 < len(raw_lines):
            nxt = raw_lines[i+1].strip()
            nxt_low = nxt.lower()
            nxt_is_sec = any(nxt_low == k or nxt_low.startswith(k) for k in section_map.keys())
            nxt_is_skip = nxt_low in meta_skips or nxt_low.startswith('extra whole egg:')
            nxt_is_dish = bool(re.search(r'\d+(?:\s*/\s*\d+)?(?:\s*\(for \d+\))?\s*$', nxt)) and not nxt_low.startswith('(rice') and not nxt_low.startswith('a sizzling')
            
            if not nxt_is_sec and not nxt_is_skip and not nxt_is_dish:
                desc = nxt
                i += 1

        name_lower = d_name.lower()
        desc_lower = desc.lower()

        # Dietary classification
        is_veg = any(k in name_lower for k in [
            'idly', 'vada', 'paneer ghee roast', 'paneer butter garlic', 'tofu pepper',
            'mushrooms malabar', 'mushrooms crispy', 'sweet corn soup', 'veg manchow',
            'paneer mexican sizzler', 'quinoa avocado', 'mushroom biryani', 'chole bhatura',
            'cream caramel', 'bread butter pudding', 'bombe alaska', 'blue berry cheese cake',
            'cooler', 'mojito', 'guava', 'tea', 'sunrise', 'buttermilk', 'lagoon', 'shake',
            'oreo', 'strawberry', 'nutella', 'colada', 'soda', 'nannari', 'coffee'
        ]) and not any(k in name_lower for k in ['egg', 'omelet', 'bhurji', 'poached', 'frittata'])

        dietary = 'Veg' if is_veg else 'Egg'

        # Egg count calculation
        eggs_used = 0
        if dietary == 'Egg':
            if '4 egg' in name_lower or '4 eggs' in name_lower or 'chinese egg sizzler' in name_lower:
                eggs_used = 4
            elif any(k in name_lower for k in ['2 pieces', '2 egg', '2 half', 'platters', 'english breakfast', 'american breakfast', 'french breakfast']) or 'two egg' in desc_lower or 'two fried' in desc_lower:
                eggs_used = 2
            elif 'quail' in desc_lower or 'mint pearl' in name_lower:
                eggs_used = 6
            else:
                eggs_used = 1

        # Tags classification
        tags = []
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
        if not tags:
            tags.append('House Specialty')

        # Spice Level
        spice_level = 0
        if any(k in name_lower or k in desc_lower for k in ['fiery', 'szechwan', 'karam', 'spicy']):
            spice_level = 2
        elif any(k in name_lower or k in desc_lower for k in ['pepper', 'peri peri', 'chili', 'schezwan']):
            spice_level = 1

        # Fallback rich description if none was given in docx
        if not desc:
            if 'idly' in name_lower:
                desc = 'Soft and authentic South Indian steamed rice cakes prepared fresh daily.'
            elif 'vada' in name_lower:
                desc = 'Crisp on the outside, fluffy inside golden medu vada prepared with savory herbs.'
            elif 'over easy' in name_lower or 'sunny side' in name_lower:
                desc = 'Farm fresh eggs cooked with seasoned butter to your exact preferred yolk consistency.'
            elif 'poached' in name_lower:
                desc = 'Gently simmered farm eggs with a velvety, runny golden yolk center.'
            elif 'scramble' in name_lower:
                desc = 'Slow-whisked soft, creamy eggs cooked gently with dairy butter.'
            elif 'bhurji' in name_lower:
                desc = 'Zesty Indian street-style scrambled eggs tossed with chopped onions, green chilies, and cilantro.'
            elif 'benedict' in name_lower:
                desc = 'Poached eggs perched on toasted bread, blanketed in rich house hollandaise.'
            elif 'tea' in name_lower:
                desc = 'Aromatic freshly brewed house tea prepared with wholesome spices and fresh milk.'
            elif 'coffee' in name_lower:
                desc = 'Traditional South Indian filter coffee brewed strong with frothy steamed milk.'
            elif 'goli soda' in name_lower:
                desc = 'Nostalgic retro carbonated marble soda bursting with crisp, refreshing fizz.'
            elif 'thickshake' in name_lower or 'shake' in name_lower:
                desc = 'Decadently blended chilled milkshake with rich premium cream and toppings.'
            elif 'cooler' in name_lower or 'mojito' in name_lower:
                desc = 'Hand-shaken vibrant, citrusy and herbal mocktail cooler served chilled over ice.'
            elif 'biryani' in name_lower:
                desc = 'Fragrant long-grain basmati rice slow-cooked with aromatic roasted spices, caramelized onions, and fresh mint.'
            elif 'mandi' in name_lower:
                desc = 'Smoky Arabian-inspired spiced fragrant rice platter served with seasoned boiled eggs, fried nuts, and house tomato salsa.'
            else:
                desc = 'Artisanal kitchen specialty prepared fresh to order using farm-fresh ingredients.'

        dish_id = f'dish-{dish_counter:03d}'
        dish_counter += 1

        dishes.append({
            'id': dish_id,
            'name': d_name,
            'categoryId': cur_cat_id,
            'categoryName': cur_cat_name,
            'description': desc,
            'tags': tags,
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

print(f"Successfully generated src/data/menu.json with {len(dishes)} authentic dishes across {len(category_defs)} categories!")
