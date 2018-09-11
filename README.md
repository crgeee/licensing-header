# licensing-header

## licensing-header.py

This tool can be used to scan a directory path or set of file paths for the detection of a header license. If not detected, it will insert the header from a template file and insert parameters.

**The python script can be run standalone or in conjunction with a git pre-commit hook.**

```python
usage: licensing-header.py [-h] [-v] [-d DIR] [-f FILES] [-t TMPL] [-y YEARS] [-o OWNER] [-n PROJECTNAME] [-u PROJECTURL] [-r] [-V]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Increases log verbosity.
  -d, --directory       The directory to recursively process.
  -f, --files           Process csv filepaths provided.
  -t, --tmpl            Template name or file to use.
  -y, --years           Year or year range to use.
  -o, --copyrightowner  Name of copyright owner to use.
  -n, --projectname     Name of project to use.
  -u, --projecturl      Url of project to use.
  -r, --replace         Replace file header when existing license found. Default is false.
  -V, --validate        Validate whether source files need the header.
```

### Supported File types

- JAVA (.java, .scala, .groovy, .jape)
- SCRIPT (.sh, .csh, .py, .pl)
- XML (.xml)
- C (.c, .cc, .cpp, .h, .hpp)

### Usage

Via python and directory parameter:

```bash
python licensing-headers.py -v -t "mit" -d "/path/to/src"
```

Via python and files parameter:

```bash
python licensing-headers.py -v -t "mit" -f "/path/to/file1.java,/path/to/file2.java,/path/to/deep/path/file3.java"
```

## git pre-commit hook

The file pre-commit is a bash git pre-commit script used for calling the licensing-header.py script with every commit. This script allows for customization in how the user wants to be notified when a file fails validation and doesn't have the header.

### Prompt mode

```bash
PROMPT_MODE="auto"
```

Options:

- **enabled**: user will be prompted to modify files that failed validation
- **disabled**: user will not be prompted, file modification won't be made
- **auto**: user will not be prompted, file modification will be made

### File mode

```bash
FILE_MODE="staged"
SRC_DIR="/src" # only used in directory mode
```

Options:

- **staged**: staged will use git staged files
- **directory**: set SRC_DIR to pass a source directory path as opposed to files

## Install

1. Add the following to your git repo's .git/hooks directory:
   - licensing-header.py
   - pre-commit
   - /templates
2. Configure settings in pre-commit file for your personal use

## Future development

1. The pre-commit hook does not consider .gitignore related files such as package manager, IDE and other related files that shouldn't be modified. A future release should add support for .gitignore when in directory mode.
2. YAML support.

## License

Revised source code is licensed under the term of [MIT License](https://en.wikipedia.org/wiki/MIT_License). See attached [LICENSE](https://github.com/crgeee/licensing-header/blob/master/LICENSE) file.

Original source is licensed under the term of MIT License to [Johann Petrak](https://github.com/johann-petrak). See [LICENSE.txt](https://github.com/johann-petrak/licenseheaders/) file for more information.
