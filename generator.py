from rich.table import Table
from rich.console import Console
console = Console()

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


grade = ask_number("Please enter grade to generate: ")

with open("data/grade" + str(grade) + ".csv", encoding="utf8") as c_file:
        for line in parse_csv(c_file.read(), name=("Grade " + str(grade))):
            index = line[0]
            kanji = line[1]
            strok = line[2]
            trans = line[3]
            oread = line[4]
            kread = line[5]
            