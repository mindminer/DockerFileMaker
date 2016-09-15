#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser, os

PLACE_HOLDER_PREFIX = '$$'
DEFAULT_PROPERTIES_FILE = 'properties'
DEFAULT_TEMPLATE_POSTFIX = 'template'
COMMON_TEMPLATE='common'

def parser_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='Output docker file name', type=str, required=False)
    parser.add_argument('-p', '--properties', help='Properties file', type=str, required=True)
    parser.add_argument('-t', '--template', help='Template files', nargs='*', type=str, required=True)
    return parser.parse_args()


def main():
    args = parser_args()
    output = args.output
    docker_file = None
    if(None != output):
        docker_file = open(output, 'w+')

    properties = args.properties
    if(properties == None):
        properties = DEFAULT_PROPERTIES_FILE

    create_docker_file(docker_file, properties, args.template)

    if(None != docker_file):
        docker_file.close()


def append(file, line):
    import sys
    if(None != file):
        file.write(line)
    else:
        sys.stdout.write(line)

def create_docker_file(output, properties, templates):
    from datetime import date

    props = get_properties(properties)
    append(output, '# Create by DockerFile Maker\n'
                 '# Create date:' + date.today().isoformat() + "\n"
                 '# Author: Jeff Wang\n')
    template_file = open(COMMON_TEMPLATE+'.'+DEFAULT_TEMPLATE_POSTFIX, "r")
    make_docker_file(output, template_file, props)

    for template in templates:
        template_file = open(template+'.'+DEFAULT_TEMPLATE_POSTFIX, "r")
        make_docker_file(output, template_file, props)


def get_properties(properties):
    config = ConfigParser.ConfigParser()
    config.optionxform = str
    config.read(properties)
    return config


def make_docker_file(docker_file, template_file, properties):
    import re

    append(docker_file, '\n')

    for line in iter(lambda: template_file.readline(), ''):
        REGEX_PATTERN = r'([$])\1\{([^}]*)\}'
        PLACE_HOLDER_PREFIX = '$${'
        PLACE_HOLDER_POSTFIX = '}'

        def find_placeholder(string):
            prop = re.search(REGEX_PATTERN, string)
            if(None != prop):
                return prop.group(2)

        def get_value(placeholder):
            if(None != placeholder):
                key = placeholder
                for section in properties.sections():
                    try:
                        return properties.get(section, key)
                    except ConfigParser.NoOptionError:
                        None
                return None

        def replace(string, placeholder, replacement):
            if(None != placeholder and None != replacement):
                new_string = string.replace(PLACE_HOLDER_PREFIX+placeholder+PLACE_HOLDER_POSTFIX, replacement)
                new_placeholder = find_placeholder(new_string)
                return replace(new_string, new_placeholder, get_value(new_placeholder))
            return string

        placeholder = find_placeholder(line)
        append(docker_file, replace(line, placeholder, get_value(placeholder)))

main()
