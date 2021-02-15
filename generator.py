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

warned = False
def create_folder_or_warn(folder):
    global warned
    try:
        if os.path.isdir(folder):
            if not warned:
                console.log("Warning: output folder exists. Press enter to confirm!")
                input()
            else:
                console.log("Warning: output folder exists.")
            warned = True
        else:
            os.mkdir(folder)
    except OSError:
        console.print("Could not create output directory!")
        exit(1)

grade_min = 1 #ask_number("Please enter first grade to generate: ")
grade_max = 6 #ask_number("Please enter last grade to generate: ")

# Create output folder
outputFolder = os.path.join("./output/")
create_folder_or_warn(outputFolder)


font_index = ImageFont.truetype("BabelStoneHan.ttf", 40)
font_kanji = ImageFont.truetype("BabelStoneHan.ttf", 240)
font_kback = ImageFont.truetype("BabelStoneHan.ttf", 360)
font_oktop = ImageFont.truetype("BabelStoneHan.ttf", 70)
font_onkun = ImageFont.truetype("BabelStoneHan.ttf", 50)

for grade in range(grade_min, grade_max + 1):
    # Create grade folder
    gradeFolder = os.path.join(outputFolder, "grade_" + str(grade))
    create_folder_or_warn(gradeFolder)

    # Create PDF file
    pdf = FPDF(unit = "pt", format = [template_width, template_height])
    pdfFrontOnly = FPDF(unit = "pt", format = [template_width, template_height])

    with open("data/grade" + str(grade) + ".csv", encoding="utf8") as c_file:
        console.print("Rendering grade " + str(grade))
        for line in parse_csv(c_file.read(), name=("Grade " + str(grade))):
            index = line[0]
            kanji = line[1]
            strok = line[2]
            trans = line[3]
            oread = line[4]
            kread = line[5]

            # Generate Front
            outputFile = os.path.join(gradeFolder, "front_" + str(index) + ".jpg")
            img = Image.open("template.jpg")
            draw = ImageDraw.Draw(img)

            def writeCenterBigAsPossible(text, fontName, maxFontSize, relCenterX, relCenterY):
                while (True):
                    currentFont = ImageFont.truetype(fontName, maxFontSize)
                    w, h = draw.textsize(text, font=currentFont)

                    if (w > template_width):
                        maxFontSize = maxFontSize - 1
                        continue

                    draw.text((template_width * relCenterX - w/2, template_height * relCenterY - h/2), text, (0, 0, 0), font=currentFont)
                    break

            # Translation
            writeCenterBigAsPossible(str(trans), "BabelStoneHan.ttf", 70, 0.5, 0.19)

            # Kanji
            writeCenterBigAsPossible(str(kanji), "BabelStoneHan.ttf", 240, 0.5, 0.4)

            # On
            writeCenterBigAsPossible("- On -", "BabelStoneHan.ttf", 70, 0.5, 0.6)

            # On Value
            writeCenterBigAsPossible(oread, "BabelStoneHan.ttf", 50, 0.5, 0.67)

            # Kun
            writeCenterBigAsPossible("- Kun -", "BabelStoneHan.ttf", 70, 0.5, 0.75)

            # Kun Value
            writeCenterBigAsPossible(kread, "BabelStoneHan.ttf", 50, 0.5, 0.82)

            # Index
            w, h = draw.textsize("Kanji #" + str(index), font=font_index)
            draw.text((template_width - w, template_height - h), "Kanji #" + str(index), (0, 0, 0), font=ImageFont.truetype("BabelStoneHan.ttf", 40))

            img.save(outputFile)

            # Add to pdf
            pdf.add_page()
            pdf.image(outputFile, 0, 0)

            pdfFrontOnly.add_page()
            pdfFrontOnly.image(outputFile, 0, 0)

            # Generate back
            outputFile = os.path.join(gradeFolder, "back_" + str(index) + ".jpg")

            img = Image.open("template_back.jpg")
            draw = ImageDraw.Draw(img)
            
            # Kanji
            writeCenterBigAsPossible(str(kanji), "BabelStoneHan.ttf", 360, 0.5, 0.5)
            
            # Grade
            writeCenterBigAsPossible("GRADE " + str(grade), "BabelStoneHan.ttf", 50, 0.5, 0.18)
            
            img.save(outputFile)

            # Add to pdf
            pdf.add_page()
            pdf.image(outputFile, 0, 0)
            
            console.print(".", end="")
    
    # Output pdf
    pdf.output(os.path.join(outputFolder, "grade_" + str(grade) + ".pdf"), "F")
    pdfFrontOnly.output(os.path.join(outputFolder, "grade_" + str(grade) + "_front_only.pdf"), "F")