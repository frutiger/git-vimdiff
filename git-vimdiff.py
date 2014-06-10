#!/usr/bin/env python

import io
import os
import subprocess
import sys

def read_until(f, char):
    result = b''
    while True:
        next = f.read(1)
        if next != char:
            result = result + next
        else:
            break
    return result

def parse_status(f):
    def type(char):
        return {
            b'M': 'modified',
            b'C': 'copied',
            b'R': 'renamed',
            b'A': 'added',
            b'D': 'deleted',
            b'U': 'unmerged',
        }[char]

    status = read_until(f, b'\0')
    try:
        score = int(status[1:])
    except ValueError:
        score = None
    return type(status[:1]), score

def parse_change(f):
    first = f.read(1)
    if first == b'':
        return None
    assert(first == b':')

    srcmode     = read_until(f, b' ')
    dstmode     = read_until(f, b' ')
    srchash     = read_until(f, b' ')
    dsthash     = read_until(f, b' ')
    type, score = parse_status(f)
    if type == 'copied' or type == 'renamed':
        srcname = read_until(f, b'\0')
        dstname = read_until(f, b'\0')
    else:
        name    = read_until(f, b'\0')

    if type == 'modified':
        return {
            'type': 'modified',
            'name': name.decode('utf-8'),
            'src': {
                'mode': srcmode.decode('utf-8'),
                'hash': srchash.decode('utf-8'),
            },
            'dst': {
                'mode': dstmode.decode('utf-8'),
                'hash': dsthash.decode('utf-8'),
            },
        }
    elif type == 'copied' or type == 'renamed':
        return {
            'type': type,
            'score': score,
            'src': {
                'mode': srcmode.decode('utf-8'),
                'hash': srchash.decode('utf-8'),
                'name': srcname.decode('utf-8'),
            },
            'dst': {
                'mode': dstmode.decode('utf-8'),
                'hash': dsthash.decode('utf-8'),
                'name': dstname.decode('utf-8'),
            },
        }
    elif type == 'added':
        return {
            'type': 'added',
            'mode': dstmode.decode('utf-8'),
            'hash': dsthash.decode('utf-8'),
            'name': name.decode('utf-8'),
        }
    elif type == 'deleted':
        return {
            'type': 'deleted',
            'mode': srcmode.decode('utf-8'),
            'hash': srchash.decode('utf-8'),
            'name': name.decode('utf-8'),
        }
    elif type == 'unmerged':
        return {
            'type': 'unmerged',
            'name': name,
        }

    raise RuntimeError('unknown type: ' + type)

def parse_changes(args):
    diff = subprocess.Popen(['git', '--no-pager', 'diff', '--raw', '-z',
                             '--abbrev=40', '--find-renames=1%',
                             '--find-copies=1%'] + args,
                            stdout=subprocess.PIPE)

    changes = []
    while True:
        change = parse_change(diff.stdout)
        if change == None:
            break
        changes.append(change)
    return changes

def root():
    return subprocess.check_output(['git',
                                    'rev-parse',
                                    '--show-toplevel']).decode('utf-8')[:-1]

def write_header(f):
    f.write(u'cd {}\n'.format(root()))
    f.write(u'set laststatus=2\n')

counter = 2
def write_hash(f, mode, hash, name, type=None, score=None):
    global counter
    f.write(u'setlocal noswapfile\n')
    f.write(u'set buftype=nowrite\n')

    name = os.path.basename(name).replace(' ', '\\ ')

    if mode == '160000':
        status = '{0}:\\ commit\\ {1}'.format(name, hash[:8])
        f.write(u'setlocal statusline={}\n'.format(status))
        f.write(u'silent file {0}:{1}:{2}\n'.format(hash[:8], counter, name))
        return

    f.write(u'silent 0read !git --no-pager show {}\n'.format(hash))
    f.write(u'+1d\n')

    if score != None:
        status = '{0}\\ [{1}%%\\ similar]\\ ({2})'.format(name, score, mode)
    elif type != None:
        status = '{0}\\ [{1}]\\ ({2})'.format(name, type, mode)
    else:
        status = '{0}\\ ({1})'.format(name, mode)

    f.write(u'setlocal statusline={}\n'.format(status))
    f.write(u'silent file {0}:{1}:{2}\n'.format(hash[:8], counter, name))
    counter = counter + 1

    f.write(u'0\n')

def write_split(f):
        f.write(u'vert diffsplit\n')
        f.write(u'enew\n')

def write_diff(f):
    f.write(u'diffthis\n')
    f.write(u'wincmd l\n')

def write_change(f, change):
    f.write(u'tabnew\n')

    if change['type'] == 'modified':
        if change['dst']['hash'] == '0000000000000000000000000000000000000000':
            f.write(u'e {}\n'.format(change['name'].replace(' ', '\\ ')))
            f.write(u'0\n')
        else:
            write_hash(f,
                       change['dst']['mode'],
                       change['dst']['hash'],
                       change['name'])
        write_split(f)
        write_hash(f,
                   change['src']['mode'],
                   change['src']['hash'],
                   change['name'])
        write_diff(f)
    elif change['type'] == 'copied' or change['type'] == 'renamed':
        write_hash(f,
                   change['dst']['mode'],
                   change['dst']['hash'],
                   change['dst']['name'],
                   change['type'],
                   change['score'])
        write_split(f)
        write_hash(f,
                   change['src']['mode'],
                   change['src']['hash'],
                   change['src']['name'],
                   change['type'])
        write_diff(f)
    elif change['type'] == 'added' or change['type'] == 'deleted':
        write_hash(f,
                   change['mode'],
                   change['hash'],
                   change['name'],
                   change['type'])

def write_footer(f):
    f.write(u'tabfirst\n')
    f.write(u'bdelete\n')

def write_commands(f, changes):
    write_header(f)
    for change in changes:
        write_change(f, change)
    write_footer(f)

def main(args):
    changes = parse_changes(args)
    if len(changes) == 0:
        return

    commands = io.StringIO()
    write_commands(commands, changes)
    subprocess.check_call([os.environ['EDITOR'], '-c', commands.getvalue()])

if __name__ == '__main__':
    main(sys.argv[1:])

