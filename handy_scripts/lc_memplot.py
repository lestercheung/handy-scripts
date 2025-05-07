#!/Users/cheule01/.local/py3/bin/python3
#/usr/bin/env python3
import argparse
import os
import sh
import termplotlib as tpl

def parse_args():

    ap = argparse.ArgumentParser()
    ap.add_argument('-c', '--column-width', type=int, default=100)
    ap.add_argument('-l', '--limit', type=int, default=30)

    return ap.parse_args()

def main():

    cfg = parse_args()

    # os.environ['COLUMNS'] = '9999'  # stop lines from truncating
    os.environ['COLUMNS'] = str(cfg.column_width)

    ps_proc = sh.ps(['-a', '-x', '-o', 'rss,comm'])
    #outputs = ps_proc.stdout.decode('utf8').splitlines()[1:]
    outputs = ps_proc.splitlines()[1:]
    tally = {}
    for line in outputs:
        rss, comm = line.strip().split(' ', maxsplit=1)

        prog = comm.split('/')[-1]
        # prog = comm
        if 'firefox' in comm.lower():
            prog = 'Firefox'
        elif 'safari' in comm.lower():
            prog = 'Safari'
        elif 'teams' in comm.lower():
            prog = 'Teams'
        elif 'docker' in comm.lower():
            prog = 'Docker'
        elif 'defender' in comm.lower():
            prog = 'Microsoft Defender'
        elif 'cisco' in comm.lower():
            prog = 'Cisco stuff'
        elif 'spotify' in comm.lower():
            prog = 'Spotify'
        elif 'python' in comm.lower():
            prog = 'Python'
        elif '.app/' in comm:
            prog = ' '.join([x for x in comm.split('/') if x.endswith('.app')])
        elif comm.startswith('/System/Library/'):
            prog = '/'.join(comm.split('/')[0:4])
        elif comm.startswith('/Library/Application Support/'):
            prog = '/'.join(comm.split('/')[0:4])
        # elif comm.startswith('/System/Applications/'):

        tally[prog] = tally.get(prog, 0) + int(int(rss)/1024)

    data = dict(sorted(list(tally.items()), key=lambda x: x[1], reverse=True)[:cfg.limit])

    from pprint import pprint
    # pprint(data)

    mem_usage = list(data.values())
    progs = list(data.keys())
    # print(mem_usage, progs)

    fig = tpl.figure()
    fig.barh(mem_usage, progs, force_ascii=False)
    fig.show()

if __name__ == '__main__':
    main()
