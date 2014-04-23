#!/usr/bin/env python

import sys, os
from os.path import exists, basename, splitext

def usage():
    sys.stderr.write('Usage: {0} file1.cpp file2.cpp [...]\n'.format(sys.argv[0]))
    sys.exit(1)
    
def main():
    args = sys.argv[1:]
    if len(args) == 0:
        usage()
    
    sources = [path for path in args if exists(path) and path.endswith('.cpp')]
    with open('targets.ninja', 'w') as fp:
        for src in sources:
            (root, ext) = splitext(basename(src))
            fp.write('\n# {0}\n'.format(root))
            fp.write('build $builddir/{0}.o: cxx src/{0}.cpp\n'.format(root))
            fp.write('build $bindir/{0}: link $builddir/{0}.o\n'.format(root))
            print('Added build rule for bin/{0}'.format(root))
        print('Wrote {0}'.format(fp.name))

if __name__ == '__main__':
    main()
