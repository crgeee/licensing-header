#!/usr/bin/env python
# encoding: utf-8

### TODO section ###
# - add support for yaml
# - should consider an ignore flag?
# - update readme

import os
import re
import argparse
import logging
import fnmatch
from string import Template
from shutil import copyfile
import sys
import datetime

# Set script variables
__years__ = datetime.datetime.now().year

# for each processing type, the detailed settings of how to process files of that type
typeSettings = {
    "java": {
        "extensions": [".java",".scala",".groovy",".jape"],
        "keepFirst": None,
        "blockCommentStartPattern": re.compile(r'^\s*/\*'),  ## used to find the beginning of a header bloc
        "blockCommentEndPattern": re.compile(r'\*/\s*$'),   ## used to find the end of a header block
        "lineCommentStartPattern": re.compile(r'\s*//'),    ## used to find header blocks made by line comments
        "lineCommentEndPattern": None,
        "headerStartLine": "/*\n",   ## inserted before the first header text line
        "headerEndLine": " */\n",    ## inserted after the last header text line
        "headerLinePrefix": " * ",   ## inserted before each header text line
        "headerLineSuffix": None,            ## inserted after each header text line, but before the new line
    },
    "script": {
        "extensions": [".sh",".csh",".py",".pl"],
        "keepFirst": re.compile(r'^#!'),
        "blockCommentStartPattern": None,
        "blockCommentEndPattern": None,
        "lineCommentStartPattern": re.compile(r'\s*#'),    ## used to find header blocks made by line comments
        "lineCommentEndPattern": None,
        "headerStartLine": "##\n",   ## inserted before the first header text line
        "headerEndLine": "##\n",    ## inserted after the last header text line
        "headerLinePrefix": "## ",   ## inserted before each header text line
        "headerLineSuffix": None            ## inserted after each header text line, but before the new line
    },
    "xml": {
        "extensions": [".xml"],
        "keepFirst": re.compile(r'^\s*<\?xml.*\?>'),
        "blockCommentStartPattern": re.compile(r'^\s*<!--'),
        "blockCommentEndPattern": re.compile(r'-->\s*$'),
        "lineCommentStartPattern": None,    ## used to find header blocks made by line comments
        "lineCommentEndPattern": None,
        "headerStartLine": "<!--\n",   ## inserted before the first header text line
        "headerEndLine": "  -->\n",    ## inserted after the last header text line
        "headerLinePrefix": "-- ",   ## inserted before each header text line
        "headerLineSuffix": None            ## inserted after each header text line, but before the new line
    },
    "c": {
        "extensions": [".c",".cc",".cpp","c++",".h",".hpp"],
        "keepFirst": None,
        "blockCommentStartPattern": re.compile(r'^\s*/\*'),
        "blockCommentEndPattern": re.compile(r'\*/\s*$'),
        "lineCommentStartPattern": re.compile(r'\s*//'),    ## used to find header blocks made by line comments
        "lineCommentEndPattern": None,
        "headerStartLine": "/*\n",   ## inserted before the first header text line
        "headerEndLine": " */\n",    ## inserted after the last header text line
        "headerLinePrefix": " * ",   ## inserted before each header text line
        "headerLineSuffix": None            ## inserted after each header text line, but before the new line
    }
}

ext2type = {}
patterns = []
validationArr = []
yearsPattern = re.compile(r"Copyright\s*(?:\(\s*[C|c|©]\s*\)\s*)?([0-9][0-9][0-9][0-9](?:-[0-9][0-9]?[0-9]?[0-9]?))",re.IGNORECASE)
licensePattern = re.compile(r"license|copyright",re.IGNORECASE)
emptyPattern = re.compile(r'^\s*$')

def parse_command_line(argv):
    """Parse command line argument. See -h option.
    Arguments:
      argv: arguments on the command line must include caller file name.
    """
    import textwrap

    example = textwrap.dedent("""
      ## Some examples of how to use this command!

      python run.sh -v -t agpl-v3 -d examples
    """).format(os.path.basename(argv[0]))
    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description="Python license header updater",
                                     epilog=example,
                                     formatter_class=formatter_class)
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Increases log verbosity.")
    parser.add_argument("-d", "--directory", 
                        dest="dir", nargs=1,
                        help="The directory to recursively process.")
    parser.add_argument("-f", "--files",
                        dest="files", nargs=1,
                        help="Analyze provided csv filepaths only.")
    parser.add_argument("-t", "--tmpl", 
                        dest="tmpl", nargs=1,
                        help="Template name or file to use.")
    parser.add_argument("-y", "--years", 
                        dest="years", nargs=1,
                        help="Year or year range to use.")
    parser.add_argument("-o", "--copyrightowner", 
                        dest="owner", nargs=1,
                        help="Name of copyright owner to use.")
    parser.add_argument("-n", "--projectname", 
                        dest="projectname", nargs=1,
                        help="Name of project to use.")
    parser.add_argument("-u", "--projecturl", 
                        dest="projecturl", nargs=1,
                        help="Url of project to use.")
    parser.add_argument("-r", "--replace", 
                        action="store_true",
                        help="Replace file header when existing license found.")
    parser.add_argument("-V", "--validate",
                        action="store_true",
                        help="Validate whether source files need the header.")
    arguments = parser.parse_args(argv[1:])
    return arguments

def get_paths(patterns, start_dir="."):
    """Retrieve files that match any of the glob patterns from the start_dir and below."""
    for root, dir, files in os.walk(start_dir):
        names = []
        for pattern in patterns:
            names += fnmatch.filter(files, pattern)
        for name in names:
            path = os.path.join(root, name)
            yield path

# return an array of lines, with all the variables replaced
# throws an error if a variable cannot be replaced
def read_template(templateFile, dict):
    with open(templateFile,'r') as f:
        lines = f.readlines()
    lines = [Template(line).substitute(dict) for line in lines]  ## use safe_substitute if we do not want an error
    return lines

# format the template lines for the given type
def for_type(templatelines,fileType):
    lines = []
    settings = typeSettings[fileType]
    headerStartLine = settings["headerStartLine"]
    headerEndLine = settings["headerEndLine"]
    headerLinePrefix = settings["headerLinePrefix"]
    headerLineSuffix = settings["headerLineSuffix"]
    if headerStartLine is not None:
        lines.append(headerStartLine)
    for l in templatelines:
        tmp = l
        if headerLinePrefix is not None:
            tmp = headerLinePrefix + tmp
        if headerLineSuffix is not None:
            tmp = tmp + headerLineSuffix
        lines.append(tmp)
    if headerEndLine is not None:
        lines.append(headerEndLine)
    return lines

## read a file and return a dictionary with the following elements:
## lines: array of lines
## skip: number of lines at the beginning to skip (always keep them when replacing or adding something)
##   can also be seen as the index of the first line not to skip
## headStart: index of first line of detected header, or None if non header detected
## headEnd: index of last line of detected header, or None
## yearsLine: index of line which contains the copyright years, or None
## haveLicense: found a line that matches a pattern that indicates this could be a license header
## settings: the type settings
## If the file is not supported, return None
def read_file(file):
    skip = 0
    headStart = None
    headEnd = None
    yearsLine = None
    haveLicense = False
    extension = os.path.splitext(file)[1]
    ## if we have no entry in the mapping from extensions to processing type, return None
    fileType = ext2type.get(extension)
    if not fileType:
        return None
    settings = typeSettings.get(fileType)
    with open(file,'r') as f:
        lines = f.readlines()
    ## now iterate throw the lines and try to determine the various indies
    ## first try to find the start of the header: skip over shebang or empty lines
    keepFirst = settings.get("keepFirst")
    blockCommentStartPattern = settings.get("blockCommentStartPattern")
    blockCommentEndPattern = settings.get("blockCommentEndPattern")
    lineCommentStartPattern = settings.get("lineCommentStartPattern")
    i = 0
    for line in lines:
        if i==0 and keepFirst and keepFirst.findall(line):
            skip = i+1
        elif emptyPattern.findall(line):
            pass
        elif blockCommentStartPattern and blockCommentStartPattern.findall(line):
            headStart = i
            break
        elif lineCommentStartPattern and lineCommentStartPattern.findall(line):
            headStart = i
            break
        elif not blockCommentStartPattern and lineCommentStartPattern and lineCommentStartPattern.findall(line):
            headStart = i
            break
        else:
            ## we have reached something else, so no header in this file
            return {"fileType":fileType, "lines":lines, "skip":skip, "headStart":None, "headEnd":None, "yearsLine": None, "settings":settings, "haveLicense": haveLicense}
        i = i+1
    ## now we have either reached the end, or we are at a line where a block start or line comment occurred
    # if we have reached the end, return default dictionary without info
    if i == len(lines):
        return {"fileType":fileType, "lines":lines, "skip":skip, "headStart":headStart, "headEnd":headEnd, "yearsLine": yearsLine, "settings":settings, "haveLicense": haveLicense}
    # otherwise process the comment block until it ends
    if blockCommentStartPattern:
        for j in range(i,len(lines)):
            if licensePattern.findall(lines[j]):
                haveLicense = True
            elif blockCommentEndPattern.findall(lines[j]):
                return {"fileType":fileType, "lines":lines, "skip":skip, "headStart":headStart, "headEnd":j, "yearsLine": yearsLine, "settings":settings, "haveLicense": haveLicense}
            elif yearsPattern.findall(lines[j]):
                haveLicense = True
                yearsLine = j
        # if we went through all the lines without finding an end, maybe we have some syntax error or some other
        # unusual situation, so lets return no header
        return {"fileType":fileType, "lines":lines, "skip":skip, "headStart":None, "headEnd":None, "yearsLine": None, "settings":settings, "haveLicense": haveLicense}
    else:
        for j in range(i,len(lines)-1):
            if lineCommentStartPattern.findall(lines[j]) and licensePattern.findall(lines[j]):
                haveLicense = True
            elif not lineCommentStartPattern.findall(lines[j]):
                return {"fileType":fileType, "lines":lines, "skip":skip, "headStart":i, "headEnd":j-1, "yearsLine": yearsLine, "settings":settings, "haveLicense": haveLicense}
            elif yearsPattern.findall(lines[j]):
                haveLicense = True
                yearsLine = j
        ## if we went through all the lines without finding the end of the block, it could be that the whole
        ## file only consisted of the header, so lets return the last line index
        return {"fileType":fileType, "lines":lines, "skip":skip, "headStart":i, "headEnd":len(lines)-1, "yearsLine": yearsLine, "settings":settings, "haveLicense": haveLicense}


def main():
    """Main function."""
    ## init: create the ext2type mappings
    for t in typeSettings:
        settings = typeSettings[t]
        exts = settings["extensions"]
        for ext in exts:
            ext2type[ext] = t
            patterns.append("*"+ext)
    try:
        error = False
        settings = {
        }
        templateLines = None
        arguments = parse_command_line(sys.argv)
        files = []
        # set logging
        if arguments.verbose:
            logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        else:
            logging.basicConfig(stream=sys.stderr, level=logging.INFO)
        # set directory
        if arguments.dir:
            start_dir = arguments.dir[0]
            files = get_paths(patterns,start_dir)
        elif arguments.files:
            # these are csv filepaths
            files = arguments.files[0].split(',')
        else:
            ## defaults to root where script was run
            start_dir = "."
            files = get_paths(patterns,start_dir)
        if len(files) < 1:
            logging.error("No files found.")
            logging.error("files arr: " + str(files))
            error = True
        else:
            logging.debug("files arr: " + str(files))
        # set years
        if arguments.years:
            settings["years"] = arguments.years[0]
        else:
            settings["years"] = __years__
        # set copyright owner
        if arguments.owner:
            settings["owner"] = arguments.owner[0]
        if arguments.projectname:
            settings["projectname"] = arguments.projectname[0]
        if arguments.projecturl:
            settings["projecturl"] = arguments.projecturl[0]
        ## if we have a template name specified, try to get or load the template
        if arguments.tmpl:            
            opt_tmpl = arguments.tmpl[0]
            ## first get all the names of our own templates
            ## for this get first the path of this file
            templatesDir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"templates")
            logging.debug("File run path: " + os.path.abspath(__file__))
            ## get all the templates in the templates directory
            templates = [f for f in get_paths("*.tmpl",templatesDir)]
            templates = [(os.path.splitext(os.path.basename(t))[0],t) for t in templates]
            ## filter by trying to match the name against what was specified
            tmpls = [t for t in templates if opt_tmpl in t[0]]
            if len(tmpls) == 1:
                tmplName = tmpls[0][0]
                tmplFile = tmpls[0][1]
                logging.info("Using template \"" + tmplName + "\"")
                logging.debug("Template file is located " + tmplFile)
                templateLines = read_template(tmplFile,settings)
            else:
                if len(tmpls) == 0:
                    ## check if we can interpret the option as file
                    if os.path.isfile(opt_tmpl):
                        logging.info("Using file " + os.path.abspath(opt_tmpl))
                        templateLines = read_template(os.path.abspath(opt_tmpl),settings)
                    else:
                        logging.error("Not a built-in template and not a file, cannot proceed: " + opt_tmpl)
                        logging.info("Built in templates: " + ", ".join([t[0] for t in templates]))
                        error = True
                else:
                    ## notify that there are multiple matching templates
                    templates = [t[0] for t in tmpls]
                    logging.error("There are multiple matching template names: " + str(templates))
                    error = True
        else: # no tmpl parameter
            logging.error("No template specified. Please at -t <name> and run again.")
            error = True
        if not error:
            ## now do the actual processing: if we did not get some error, we have a template loaded
            ## now process all the files and either replace the years or replace/add the header
            for file in files:
                dict = read_file(file)
                if not dict:
                    continue
                if not templateLines:
                    logging.error("No templateLines found.")
                    continue
                haveLicense = dict["haveLicense"]
                if arguments.validate and not haveLicense:
                    logging.debug("[validation][hasLicense] " + file + " doesn't have a license.")
                    validationArr.append(file)
                    continue
                if haveLicense and not arguments.replace:
                    logging.debug("[hasLicense][noreplace] " + file)
                    continue            
                with open(file,'w') as fw:
                    ## if we found a header, replace it
                    ## otherwise, add it after the lines to skip
                    headStart = dict["headStart"]
                    headEnd = dict["headEnd"]                    
                    fileType = dict["fileType"]
                    skip = dict["skip"]
                    lines = dict["lines"]
                    logging.debug("headStart: " + str(headStart))
                    logging.debug("headEnd: " + str(headEnd))
                    logging.debug("haveLicense: " + str(haveLicense))
                    logging.debug("fileType: " + str(fileType))
                    logging.debug("skip: " + str(skip))
                    logging.debug("replace flag: " + str(arguments.replace))
                    if headStart is not None and headEnd is not None and haveLicense:
                        logging.info("Replacing header in file " + file)
                        ## first write the lines before the header
                        fw.writelines(lines[0:headStart])
                        ## now write the new header from the template lines
                        fw.writelines(for_type(templateLines,fileType))
                        ## now write the rest of the lines
                        fw.writelines(lines[headEnd+1:])
                    else:
                        logging.info("Adding header to file " + file)
                        fw.writelines(lines[0:skip])
                        fw.writelines(for_type(templateLines,fileType))
                        fw.writelines(lines[skip:])
            if arguments.validate:
                count = len(validationArr)
                if (count > 0):              
                    logging.info("VALIDATION_VALID: false")
                    logging.info("VALIDATION_COUNT: " + str(count))
                    logging.info("VALIDATION_FILES:")
                    for file in validationArr:
                        print(file)
                    logging.info("There are " + str(count) + " files without a header.")
                else:
                    logging.info("VALIDATION_VALID: true")
                    logging.info("VALIDATION_COUNT: " + str(count))
                    logging.info("There are " + str(count) + " files without a header.")
    finally:
        logging.shutdown()

if __name__ == "__main__":
    sys.exit(main())
