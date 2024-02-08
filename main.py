import colorgram, os
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from forms import SettingsForm

sample_path = "./static/assets/palette_pictures/sample.jpg" # DEFAULT - If invalid file or no file selected, defaults will load.


### COLOR PALLET GENERATOR ###
def color_tuple(colorgram_rgb):
    """Creates RGB tuple of colors. Tuple is passed through the page_info function."""
    r = colorgram_rgb[0]
    g = colorgram_rgb[1]
    b = colorgram_rgb[2]
    return (r, g, b)


def page_info(number_of_colors, path):
    """Returns information that will be rendered on the color palette web page."""
    image_path = path
    file_name = image_path.split("/")[-1] # Returns image name
    colors_to_return = number_of_colors # User can set value
    colors = colorgram.extract(image_path, colors_to_return)
    rgb_list = []
    style_colors = []
    hex_list = []
    proportion_list = []
    table_rows = [["Color", "Hex Color Code", "RGB Color Code", "Percentage of Output"]] 

    # Appends colors to RGB list
    for color in colors:
        color_to_add = color_tuple(color.rgb)
        rgb_list.append(color_to_add)

    # Generate Hex color codes and appends to hex list
    for rgb in rgb_list:
        hex_list.append('#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2]))
        
    # Style_colors list will be used to set CSS color for first cell in each row
    for color in hex_list:
        color = color.replace("#", "")
        style_colors.append(color)

    # Generate percentages for colors output. Percentages are appended to the proportion list
    for color in colors:
        proportion_list.append((str(round(color.proportion, 2))))
    for percentage in range(len(proportion_list)):
        if len(proportion_list[percentage]) == 3:
            proportion_list[percentage] = proportion_list[percentage] + "0" # Adds 0 to end of percentages are missing a 0

    # Generates the table rows list. This list is what is displayed on the color palette page.
    for index in range(colors_to_return):
        table_rows.append([style_colors[index], hex_list[index], rgb_list[index], proportion_list[index]])  
    
    return table_rows, file_name

### FLASK APPLICATION ###
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_APP_SECRET_KEY")
bootstrap = Bootstrap5(app)

@app.route("/", methods=["GET", "POST"])
def home():
    page = page_info(number_of_colors=10, path=sample_path) # Defaults
    color_palette = page[0]
    file_name = page[1]
    palette_settings = SettingsForm()
    
    if palette_settings.validate_on_submit():
        
        try:
            new_upload = "./static/assets/palette_pictures/upload.jpg" 
            picture = (palette_settings.picture_upload.data).read()
            
            with open(new_upload, mode="wb") as file:
                file.write(picture)

            colors_to_return = int(palette_settings.number_of_colors.data) # New quantity of colors to return
            page = page_info(number_of_colors=colors_to_return, path=new_upload) # New values to be displayed
            color_palette = page[0]
            file_name = page[1]

            return render_template("index.html",
                                palette_img = file_name,
                                color_palette = color_palette,
                                palette_settings = palette_settings)
        
        # Except is executed when an invalid file type is uploaded. Defaults reloaded.
        except:
            return redirect(url_for("home"))
    
    return render_template(
        "index.html",
        palette_img = file_name,
        color_palette = color_palette,
        palette_settings = palette_settings)


if __name__ == "__main__":
    app.run(debug=True, port=5002)