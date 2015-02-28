__author__ = 'ethan'
import misc_tools
import sys

if len(sys.argv) > 1:
    infile = str(sys.argv[-1])
    test_proj = misc_tools.Project(infile).main()