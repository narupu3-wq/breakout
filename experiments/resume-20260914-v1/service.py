#!/usr/bin/env python3
"""Start/stop the local paper collector; does not change system settings."""
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
PID=DATA/'service.json'


def running():
    if not PID.exists(): return None
    meta=json.loads(PID.read_text())
    result=subprocess.run(['ps','-p',str(meta['pid']),'-o','command='],capture_output=True,text=True)
    expected=str(ROOT/'research.py')+' paper'
    return meta if result.returncode==0 and expected in result.stdout else None


def main():
    DATA.mkdir(exist_ok=True)
    with (DATA/'service.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        command=sys.argv[1] if len(sys.argv)>1 else 'status'
        meta=running()
        if command=='start':
            if meta: print(json.dumps({'status':'already_running',**meta})); return
            with (DATA/'paper.log').open('ab',buffering=0) as log:
                process=subprocess.Popen([sys.executable,str(ROOT/'research.py'),'paper'],cwd=str(ROOT),
                                         stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
            meta={'pid':process.pid,'started':time.time(),'mode':'paper_only'}
            PID.write_text(json.dumps(meta))
            time.sleep(1)
            if process.poll() is not None: raise RuntimeError('Collector exited; inspect data/paper.log')
            print(json.dumps({'status':'started',**meta}))
        elif command=='stop':
            if not meta: print(json.dumps({'status':'not_running'})); return
            os.kill(meta['pid'],signal.SIGTERM)
            print(json.dumps({'status':'stop_requested','pid':meta['pid']}))
        elif command=='status':
            print(json.dumps({'status':'running' if meta else 'stopped',**(meta or {})}))
        else: raise ValueError('Use start, stop, or status')


if __name__=='__main__': main()
