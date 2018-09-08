# licensing-header

## licensing-header.py

A tool with

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

## git pre-commit hook

pre-commit is a bash script for using with git as a pre

## License

Revised source code is licensed under the term of [MIT License](https://en.wikipedia.org/wiki/MIT_License). See attached [LICENSE](https://github.com/crgeee/licensing-header/blob/master/LICENSE) file.

Original source is licensed under the term of MIT License to [Johann Petrak](https://github.com/johann-petrak). See [LICENSE.txt](https://github.com/johann-petrak/licenseheaders/) file for more information.
