#!/usr/bin/python

import re
import sys
import optparse
from os.path import isfile
from datetime import datetime
try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("ERROR: missing jinja2 module")
    sys.exit(1)

def main():

    p = optparse.OptionParser(description="Generate climbing log HTML page.", prog="doc-text-update", usage="%prog [-h|--help] -i DATAFILE [-o OUTPUTFILE]")
    p.add_option('-i', '--input', dest="in_file",
                 action="store", help="Input file to load climbing data from.")
    p.add_option('-o', '--output', dest="out_file",
                 action="store", help="Output file (default is ./index.html)")
    (opts, args) = p.parse_args()

    if not opts.in_file:
        p.error("You must specify an input file!")
        sys.exit(1)

    if not isfile(opts.in_file):
        p.error("%s is not a regular file!" % opts.in_file)
        sys.exit(1)

    out_file = opts.out_file if opts.out_file else "./index.html"

    with open(opts.in_file, 'r') as my_file:
        text = my_file.read()

    text = text.decode("utf8")

    # Get rid of comments (lines starting with '#')
    text = re.sub(r'(?m)^#.*\n?', '', text).strip()

    data = []
    for entry in text.split("\n\n"):
        refs = []
        routes = []

        for line in entry.split('\n'):
            if line.split(",")[0].isdigit() and len(line.split(",")[0]) == 8:
                if line.count(",") != 2:
                    print("ERROR: Invalid syntax! Could not parse:\n\n%s" % line)
                    sys.exit(1)
                date, place, grading = line.split(",", 3)
                continue

            if line.startswith("ref:"):
                if line.count(",") != 1:
                    print("ERROR: Invalid syntax! Could not parse:\n\n%s" % line)
                    sys.exit(1)
                refs.append(line[4:].split(",", 2))
                continue

            if line.count(",") != 4:
                print("ERROR: Invalid syntax! Could not parse:\n\n%s" % line)
                sys.exit(1)
            routes.append(line.split(",", 5))

        if not routes:
            print("ERROR: Could not parse any routes from:\n\n%s" % entry)
            sys.exit(1)

        if not (date and place and grading):
            print("ERROR: Could not parse date/place/grading from:\n\n%s" % entry)
            sys.exit(1)

        human_date = datetime.strptime(date, "%Y%m%d").strftime("%B %e, %Y")
        data.append([date, human_date, place, grading, refs, routes])

    # Load up our Jinja template and pass our climbing data
    env = Environment(loader=FileSystemLoader('./'))
    template = env.get_template('template.html')
    rendered_html = template.render(data=data)

    with open(out_file, "w") as f:
        f.write(rendered_html.encode("utf8"))
        
if __name__ == "__main__":
    main()
