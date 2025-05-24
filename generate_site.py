import os
import json
import zipfile
from jinja2 import Template

def load_menu_data(file_path):
    """Loads the menu data from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def generate_html(template_str, output_path, **context):
    """Generates an HTML file from a Jinja2 template."""
    template = Template(template_str)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(template.render(context))

def create_site(menu_data, output_folder):
    """Generates a modern website with Tailwind CSS support, including meal pages and shopping list."""
    os.makedirs(output_folder, exist_ok=True)
    print(f"Creating site in: {output_folder}")

    ### Main Menu Page (index.html)
    index_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Weekly Menu</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 text-gray-900">
  <header class="bg-white shadow-md p-5 flex justify-between items-center">
    <h1 class="text-2xl font-bold">Your Weekly Meal Plan</h1>
    <a href="shopping_list.html" class="text-blue-600 hover:underline">Shopping List</a>
  </header>

  <main class="max-w-4xl mx-auto mt-10">
    <h2 class="text-xl font-semibold text-center mb-6">Meal Schedule</h2>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {% for day, meals in menu['menu'].items() %}
      <div class="bg-white rounded-lg shadow-md p-4 transition hover:shadow-lg">
        <h3 class="text-lg font-bold text-blue-600">{{ day }}</h3>
        <ul class="mt-3">
          {% for meal_type, meal_name in meals.items() %}
          <li class="py-1 border-b last:border-none">
            <strong class="text-gray-700">{{ meal_type }}:</strong> 
            <a href="{{ day.lower() }}_{{ meal_type.lower() }}.html" class="text-blue-500 hover:underline">
              {{ meal_name }}
            </a>
          </li>
          {% endfor %}
        </ul>
      </div>
      {% endfor %}
    </div>
  </main>
</body>
</html>"""
    generate_html(index_template, os.path.join(output_folder, "index.html"), menu=menu_data)

    ### Meal Pages (Includes Daily Notes if available)
    meal_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ meal_name }}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 text-gray-900">
  <header class="bg-white shadow-md p-5 flex justify-between items-center">
    <h1 class="text-2xl font-bold">{{ meal_name }}</h1>
    <a href="index.html" class="text-blue-600 hover:underline">Back to Menu</a>
  </header>

  <main class="max-w-2xl mx-auto mt-10 p-5 bg-white shadow-md rounded-lg">
    <h2 class="text-lg font-semibold">Meal Details</h2>
    
    {% if notes %}
      <h3 class="text-lg font-bold mt-4">{{ notes.title }}</h3>
      {% for section, content in notes.items() %}
        {% if section != "title" and content %}
        <h4 class="font-semibold mt-2 capitalize">{{ section.replace("_", " ") }}:</h4>
        <ul class="list-disc pl-5 text-gray-700">
          {% for item in content %}
            <li>{{ item }}</li>
          {% endfor %}
        </ul>
        {% endif %}
      {% endfor %}
    {% else %}
      <p class="text-gray-700 mt-3">No additional notes for this meal.</p>
    {% endif %}
  </main>
</body>
</html>"""
    for day, meals in menu_data["menu"].items():
        for meal_type, meal_name in meals.items():
            meal_file = f"{day.lower()}_{meal_type.lower()}.html"
            notes = menu_data.get("daily_notes", {}).get(day, {}).get(meal_type, {})
            generate_html(meal_template, os.path.join(output_folder, meal_file),
                          meal_name=meal_name, notes=notes)

    ### Shopping List Page (Properly Categorized & Collapsible)
    shopping_list_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Shopping List</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 text-gray-900">
  <header class="bg-white shadow-md p-5 flex justify-between items-center">
    <h1 class="text-2xl font-bold">Shopping List</h1>
    <a href="index.html" class="text-blue-600 hover:underline">Back to Menu</a>
  </header>

  <main class="max-w-4xl mx-auto mt-10">
    <h2 class="text-xl font-semibold text-center mb-6">Your Ingredients</h2>
    {% for category, items in shopping_list.items() %}
    <div class="mb-4">
      <button class="w-full text-left font-semibold bg-gray-200 p-3 rounded-md"
              onclick="toggleCategory('{{ category }}')">
        {{ category }} ▼
      </button>
      <div id="{{ category }}" class="hidden mt-2">
        {% for item in items %}
        <div class="bg-white rounded-lg shadow-md p-3 text-center cursor-pointer transition hover:bg-gray-200" 
             onclick="toggleItem(this)">
          <p class="text-lg font-medium">{{ item }}</p>
        </div>
        {% endfor %}
      </div>
    </div>
    {% endfor %}
  </main>

  <script>
    function toggleCategory(category) {
      document.getElementById(category).classList.toggle("hidden");
    }
    function toggleItem(element) {
      element.classList.toggle("bg-green-300");
      element.classList.toggle("line-through");
    }
  </script>
</body>
</html>"""
    generate_html(shopping_list_template,
                  os.path.join(output_folder, "shopping_list.html"),
                  shopping_list=menu_data["shopping_list"])

def zip_site(output_folder, zip_name):
    """Creates a zip file of the generated website."""
    print(f"Zipping contents of {output_folder} into {zip_name}")
    if not os.path.exists(output_folder):
        print("Error: Output folder does not exist!")
        return
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, output_folder)
                zipf.write(full_path, arcname=rel_path)
    print("Zip file created successfully.")

def main():
    # Get the path of the folder that contains this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("Script directory is:", script_dir)

    # Build the full path to menu.json in the script's directory
    menu_json_path = os.path.join(script_dir, "menu.json")

    # Load menu data from menu.json
    menu_data = load_menu_data(menu_json_path)

    # Create the 'mysite' folder in the same directory as the script
    output_folder = os.path.join(script_dir, "mysite")
    create_site(menu_data, output_folder)

    # Zip the site into 'mysite.zip' in the same directory
    zip_name = os.path.join(script_dir, "mysite.zip")
    zip_site(output_folder, zip_name)

    print("Website created and zipped successfully.")

if __name__ == "__main__":
    main()
