#!/usr/bin/env python3
"""Small student workflow: up, test, demo, failure-demo, logs, down."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.request import urlopen
ROOT = Path(__file__).resolve().parents[1]


def compose(*args):
    if shutil.which('docker') and subprocess.run(['docker','compose','version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        command = ['docker','compose']
    elif shutil.which('docker-compose'):
        command = ['docker-compose']
    else:
        raise RuntimeError('Docker + Compose are required. See README.md for setup.')
    env = os.environ.copy()
    if 'DOCKER_CONTEXT' not in env:
        names = subprocess.check_output(['docker','context','ls','--format','{{.Name}}'], text=True).splitlines()
        if 'colima-placement-lab' in names:
            env['DOCKER_CONTEXT'] = 'colima-placement-lab'
    subprocess.run(command + list(args), cwd=ROOT, env=env, check=True)


def wait_ready(timeout=90):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            for port in (8000,8001,8002):
                with urlopen(f'http://localhost:{port}/health', timeout=2) as r:
                    if not json.load(r)['workers_alive']:
                        raise RuntimeError('Workers not ready')
            return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError('Services did not become ready; run python3 tools/dev.py logs')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['up','down','test','demo','failure-demo','logs','status'])
    args = p.parse_args()
    python = ROOT/'.venv/bin/python'
    if args.action == 'up':
        compose('up','-d','--build','--wait','--wait-timeout','180')
        wait_ready()
        print('Ready: orders http://localhost:8000/docs, inventory :8001/docs, payments :8002/docs')
    elif args.action == 'down':
        compose('down')  # Preserve PostgreSQL learning data.
    elif args.action == 'logs':
        compose('logs','--tail','80')
    elif args.action == 'status':
        compose('ps')
    elif args.action in ('test','failure-demo'):
        wait_ready()
        marker = 'disruption' if args.action == 'failure-demo' else 'not disruption'
        subprocess.run([str(python),'-m','pytest','-q','-m',marker],cwd=ROOT,check=True)
    else:
        wait_ready()
        subprocess.run([str(python),str(ROOT/'tools/demo.py')],cwd=ROOT,check=True)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError,subprocess.CalledProcessError) as e:
        print(e,file=sys.stderr)
        sys.exit(1)
