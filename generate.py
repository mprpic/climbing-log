#!/usr/bin/python

import re
import sys
import argparse
from os.path import isfile, realpath, dirname
from datetime import datetime
try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print('ERROR: missing jinja2 module')
    sys.exit(1)

# Names of input files in the script's directory
CLIMBING_TEMPLATE = './templates/climbing-template.html'
FERRATA_TEMPLATE = './templates/ferrata-template.html'


def read_data_file(in_file):

    if not isfile(in_file):
        print("%s is not a regular file!" % in_file)
        sys.exit(1)

    with open(in_file, 'r') as my_file:
        text = my_file.read()

    text = text.decode("utf8")

    # Get rid of comments (lines starting with '#')
    text = re.sub(r'(?m)^#.*\n?', '', text).strip()

    return text


def create_html(data, title, template):

    # Load up Jinja template and pass data
    env = Environment(loader=FileSystemLoader(dirname(realpath(__file__))))
    template = env.get_template(template)
    rendered_html = template.render(data=data, title=title)

    return rendered_html


def generate_climbing_log(in_file):

    text = read_data_file(in_file)

    data = []
    for entry in text.split('\n\n'):
        refs = []
        routes = []

        for line in entry.split('\n'):
            if line.split(',')[0].isdigit() and len(line.split(',')[0]) == 8:
                if line.count(',') != 2:
                    print('ERROR: Invalid syntax! Could not parse:\n\n%s' % line)
                    sys.exit(1)
                date_string, place, grading = line.split(',', 3)
                continue

            if line.startswith('ref:'):
                if line.count(',') != 1:
                    print('ERROR: Invalid syntax! Could not parse:\n\n%s' % line)
                    sys.exit(1)
                refs.append(line[4:].split(',', 2))
                continue

            if line.count(',') != 4:
                print('ERROR: Invalid syntax! Could not parse:\n\n%s' % line)
                sys.exit(1)
            routes.append(line.split(',', 5))

        if not routes:
            print('ERROR: Could not parse any routes from:\n\n%s' % entry)
            sys.exit(1)

        if not (date_string and place and grading):
            print('ERROR: Could not parse date/place/grading from:\n\n%s' % entry)
            sys.exit(1)

        human_date = datetime.strptime(date, '%Y%m%d').strftime('%B %e, %Y')
        data.append([date_string, place, grading, refs, routes])

    return data


def generate_ferrata_log(in_file):

    text = read_data_file(in_file)

    data = []
    for entry in text.split('\n\n'):
        refs = []

        for line in entry.split('\n'):
            if line.split(':')[0].isdigit() and len(line.split(':')[0]) == 8:
                if line.count(':') != 2:
                    print('ERROR: Invalid syntax! Could not parse:\n\n%s' % line)
                    sys.exit(1)
                date, place, grading = line.split(':', 3)
                continue

            if line.startswith('ref:'):
                if line.count(';') != 1:
                    print('ERROR: Invalid syntax! Could not parse:\n\n%s' % line)
                    sys.exit(1)
                refs.append(line[4:].split(';', 2))
                continue

        if not refs:
            print('ERROR: Could not parse any refs from:\n\n%s' % entry)
            sys.exit(1)

        if not (date and place and grading):
            print('ERROR: Could not parse date/place/grading from:\n\n%s' % entry)
            sys.exit(1)

        human_date = datetime.strptime(date, '%Y%m%d').strftime('%B %e, %Y')
        data.append([date, human_date, place, grading, refs])

    return data


def main():

    p = argparse.ArgumentParser(description='Generate climbing log HTML page.')
    p.add_option('-i', '--input', dest='in_file', required=True,
                 action='store', help='input file to load climbing data from')
    p.add_option('-o', '--output', dest='out_file',
                 action='store', help='output file (default: "./index.html")')
    p.add_option('-f', '--ferrata', dest='ferrata',
                 action='store_true', help='create a ferrata log HTML page')
    p.add_option('-t', '--title', dest='title',
                 action='store', help='page title (default "Climbing Log" or "Ferrata Log")')
    args = p.parse_args()

    data = generate_ferrata_log(args.in_file)

    if args.ferrata:
        title = args.title if args.title else 'Ferrata Log'
        html = create_html(data, title, FERRATA_TEMPLATE)
    else:
        title = args.title if args.title else 'Climbing Log'
        html = create_html(data, title, CLIMBING_TEMPLATE)

    out_file = args.out_file if args.out_file else './index.html'
    with open(out_file, 'w') as f:
        f.write(html.encode('utf8'))

if __name__ == '__main__':
    main()
