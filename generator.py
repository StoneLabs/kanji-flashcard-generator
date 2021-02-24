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

convert_to_kana = False
if input("Would you like to convert on/kin readings to hiragana (EXPERIMENTAL)? (y/N): ").lower().strip()[:1] == "y":
    import romajitable
    convert_to_kana = True
    

grade_min = 1 #ask_number("Please enter first grade to generate: ")
grade_max = 6 #ask_number("Please enter last grade to generate: ")

# Create output folder
outputFolder = os.path.join("./output/")
create_folder_or_warn(outputFolder)

for grade in range(grade_min, grade_max + 1):
    console.print("\n\nRendering grade " + str(grade))
    
    # Create grade folder
    gradeFolder = os.path.join(outputFolder, "grade_" + str(grade))
    create_folder_or_warn(gradeFolder)

    with open("data/grade" + str(grade) + ".csv", encoding="utf8") as c_file:
        
        imagesFront = []
        imagesBack = []
        
        for line in parse_csv(c_file.read(), name=("Grade " + str(grade))):
            console.print(".", end="")

            index = line[0]
            kanji = line[1]
            strok = line[2]
            trans = line[3]
            oread = line[4]
            kread = line[5]

            # Convert to kana
            if convert_to_kana:
                oread = romajitable.to_kana(oread.replace(" ", "")).hiragana
                kread = romajitable.to_kana(kread.replace(" ", "")).hiragana

            # Generate Front
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

            # Draw front side
            writeCenterBigAsPossible(str(trans), "BabelStoneHan.ttf", 70, 0.5, 0.19)
            writeCenterBigAsPossible(str(kanji), "BabelStoneHan.ttf", 240, 0.5, 0.4)
            writeCenterBigAsPossible("- On -", "BabelStoneHan.ttf", 70, 0.5, 0.6)
            writeCenterBigAsPossible(oread, "BabelStoneHan.ttf", 50, 0.5, 0.67)
            writeCenterBigAsPossible("- Kun -", "BabelStoneHan.ttf", 70, 0.5, 0.75)
            writeCenterBigAsPossible(kread, "BabelStoneHan.ttf", 50, 0.5, 0.82)

            w, h = draw.textsize("Kanji #" + str(index), font=ImageFont.truetype("BabelStoneHan.ttf", 40))
            draw.text((template_width - w, template_height - h), "Kanji #" + str(index), (0, 0, 0), font=ImageFont.truetype("BabelStoneHan.ttf", 40))

            # Save image
            outputFile = os.path.join(gradeFolder, "front_" + str(index) + ".jpg")
            img.save(outputFile)
            imagesFront.append(outputFile)

            # Generate back
            img = Image.open("template_back.jpg")
            draw = ImageDraw.Draw(img)
            
            # Draw back side
            writeCenterBigAsPossible(str(kanji), "BabelStoneHan.ttf", 360, 0.5, 0.5)
            writeCenterBigAsPossible("GRADE " + str(grade), "BabelStoneHan.ttf", 50, 0.5, 0.18)
            
            # Save image
            outputFile = os.path.join(gradeFolder, "back_" + str(index) + ".jpg")
            img.save(outputFile)
            imagesBack.append(outputFile)
    
        # Create PDF file
        # A4 =  210 mm x  297 mm =  595 pt x  842 pt
        pdf = FPDF(unit = "pt", format = "A4")
        margin = 40 #pt

        def addImageRel(fifo, centerX, centerY, ratio, w, border):
            if len(fifo) < 1:
                return

            widthNM = 595 - 2 * margin
            heighthNM = 842 - 2 * margin

            imgWidth = w * widthNM
            imgHight = w * widthNM / ratio

            imgX = margin + centerX * widthNM - imgWidth/2
            imgY = margin + centerY * heighthNM - imgHight/2

            pdf.image(fifo.pop(0), imgX, imgY, imgWidth, imgHight)
            if border:
                pdf.rect(imgX, imgY, imgWidth, imgHight)

        while len(imagesFront) > 0:
            pdf.add_page()
            #pdf.rect(margin, margin, 595 - 2 * margin,  842 - 2 * margin)

            addImageRel(imagesFront, 0.15, 0.17, 6/10, 0.28, True)
            addImageRel(imagesFront, 0.50, 0.17, 6/10, 0.28, True)
            addImageRel(imagesFront, 0.85, 0.17, 6/10, 0.28, True)

            addImageRel(imagesFront, 0.15, 0.5, 6/10, 0.28, True)
            addImageRel(imagesFront, 0.50, 0.5, 6/10, 0.28, True)
            addImageRel(imagesFront, 0.85, 0.5, 6/10, 0.28, True)

            addImageRel(imagesFront, 0.15, 0.83, 6/10, 0.28, True)
            addImageRel(imagesFront, 0.50, 0.83, 6/10, 0.28, True)
            addImageRel(imagesFront, 0.85, 0.83, 6/10, 0.28, True)

            # Print back sides in opposit X order for double side printing
            pdf.add_page()

            addImageRel(imagesBack, 0.85, 0.17, 6/10, 0.28, False)
            addImageRel(imagesBack, 0.50, 0.17, 6/10, 0.28, False)
            addImageRel(imagesBack, 0.15, 0.17, 6/10, 0.28, False)

            addImageRel(imagesBack, 0.85, 0.5, 6/10, 0.28, False)
            addImageRel(imagesBack, 0.50, 0.5, 6/10, 0.28, False)
            addImageRel(imagesBack, 0.15, 0.5, 6/10, 0.28, False)

            addImageRel(imagesBack, 0.85, 0.83, 6/10, 0.28, False)
            addImageRel(imagesBack, 0.50, 0.83, 6/10, 0.28, False)
            addImageRel(imagesBack, 0.15, 0.83, 6/10, 0.28, False)

        # Generate PDF
        pdf.output(os.path.join(outputFolder, "grade_" + str(grade) + ".pdf"), "F")