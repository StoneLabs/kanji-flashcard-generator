import os

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

from fpdf import FPDF

from rich.table import Table
from rich.console import Console
console = Console()

# Note:
template_width = 600
template_height = 1000


# Parse CSV file and return a list of lists
def parse_csv(text, sep=",", name="unknown file"):
    lines = list(map(lambda t: t.strip(), text.split("\n")))
    lines = list(filter(lambda l: l != "" and l[0] != "#", lines))
    ret = list(map(lambda l: l.split(sep), lines))
    table = Table(title=name, show_header=False)
    for row in ret:
        table.add_row(*list(map(lambda l: str(l), row)))
    console.print(table, "\n\n\n")
    return ret

def ask_number(prompt):
    while True:
        try:
            res = int(input(prompt))
            break
        except ValueError:
            console.print("Numbers only please!")
    return res

def create_folder_or_warn(folder):
    try:
        if os.path.isdir(folder):
            input("\nWarning: output folder exists. Press enter to confirm.")
        else:
            os.mkdir(folder)
    except OSError:
        console.print("Could not create output directory!")
        exit(1)

grade_min = ask_number("Please enter first grade to generate: ")
grade_max = ask_number("Please enter last grade to generate: ")

# Create output folder
outputFolder = os.path.join("./output/")
create_folder_or_warn(outputFolder)


font_index = ImageFont.truetype("BabelStoneHan.ttf", 40)
font_kanji = ImageFont.truetype("BabelStoneHan.ttf", 240)
font_oktop = ImageFont.truetype("BabelStoneHan.ttf", 70)
font_onkun = ImageFont.truetype("BabelStoneHan.ttf", 50)

for grade in range(grade_min, grade_max + 1):
    # Create grade folder
    gradeFolder = os.path.join(outputFolder, "grade_" + str(grade))
    create_folder_or_warn(gradeFolder)

    # Create PDF file
    pdf = FPDF(unit = "pt", format = [template_width, template_height])

    with open("data/grade" + str(grade) + ".csv", encoding="utf8") as c_file:
        for line in parse_csv(c_file.read(), name=("Grade " + str(grade))):
            index = line[0]
            kanji = line[1]
            strok = line[2]
            trans = line[3]
            oread = line[4]
            kread = line[5]
            outputFile = os.path.join(gradeFolder, "front_" + str(index) + ".jpg")

            img = Image.open("template.jpg")
            draw = ImageDraw.Draw(img)

            # Translation
            w, h = draw.textsize(str(trans).replace(";", " ").split(" ", 1)[0], font=font_oktop)
            draw.text((template_width * 0.5 - w/2, template_height * 0.19 - h/2), str(trans).replace(";", " ").split(" ", 1)[0], (0, 0, 0), font=font_oktop)

            # Kanji
            w, h = draw.textsize(str(kanji), font=font_kanji)
            draw.text((template_width * 0.5 - w/2, template_height * 0.4 - h/2), str(kanji), (0, 0, 0), font=font_kanji)

            # On
            w, h = draw.textsize("- On -", font=font_oktop)
            draw.text((template_width * 0.5 - w/2, template_height * 0.6 - h/2), "- On -", (0, 0, 0), font=font_oktop)

            # On Value
            w, h = draw.textsize(oread, font=font_onkun)
            draw.text((template_width * 0.5 - w/2, template_height * 0.67 - h/2), oread, (0, 0, 0), font=font_onkun)

            # Kun
            w, h = draw.textsize("- Kun -", font=font_oktop)
            draw.text((template_width * 0.5 - w/2, template_height * 0.75 - h/2), "- Kun -", (0, 0, 0), font=font_oktop)

            # Kun Value
            w, h = draw.textsize(kread, font=font_onkun)
            draw.text((template_width * 0.5 - w/2, template_height * 0.82 - h/2), kread, (0, 0, 0), font=font_onkun)

            # Index
            w, h = draw.textsize("Kanji #" + str(index), font=font_index)
            draw.text((template_width - w, template_height - h), "Kanji #" + str(index), (0, 0, 0), font=font_index)

            img.save(outputFile)

            # Add to pdf
            pdf.add_page()
            pdf.image(outputFile, 0, 0)
    
    # Output pdf
    pdf.output(os.path.join(outputFolder, "grade_" + str(grade) + ".pdf"), "F")