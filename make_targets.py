#!/usr/bin/env python

import sys, os
from os.path import exists, dirname, basename, splitext

def usage():
    sys.stderr.write('Usage: {0} file1.cpp file2.cpp [...]\n'.format(sys.argv[0]))
    sys.exit(1)
    
def main():
    args = sys.argv[1:]
    if len(args) == 0:
        usage()
    
    sources = [path for path in args if exists(path) and path.endswith('.cpp')]
    with open('targets.ninja', 'w') as fp:
        fp.write('# Created by {0}\n'.format(sys.argv[0]))
        fp.write('# THIS FILE WILL BE OVERWRITTEN!\n')
        for src in sources:
            d = {}
            assert src.startswith('src/')
            assert src.endswith('.cpp')
            d['prefix'] = dirname(src).replace('src/','').replace('/','_')
            d['src'] = src
            d['root'], d['ext'] = splitext(basename(src))
            d['target'] = '{prefix}_{root}'.format(**d)
            fp.write('\n# {target}\n'.format(**d))
            fp.write('build $builddir/{target}.o: cxx {src}\n'.format(**d))
            fp.write('build $bindir/{target}: link $builddir/{target}.o\n'.format(**d))
            print('Added build rule for bin/{target}'.format(**d))
        print('Wrote {0}'.format(fp.name))

if __name__ == '__main__':
    main()
