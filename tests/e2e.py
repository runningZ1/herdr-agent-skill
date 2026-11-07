#!/usr/bin/env python3
"""Explicit real-Herdr smoke test. Default: owned layout CRUD, no model calls."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
CLI=ROOT/'scripts'/'herdr_agent.py'
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'scripts'))
from herdr_agent import clean


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true',help='Explicitly create and clean up isolated test layout')
    parser.add_argument('--agent',choices=['claude','codex'],help='Also start this Agent and send one no-tools arithmetic prompt')
    args=parser.parse_args()
    if not args.run: parser.error('Pass --run to authorize this real layout test')
    if os.environ.get('HERDR_ENV')!='1': parser.error('Run inside a Herdr-managed pane')
    label='herdr-review-'+uuid.uuid4().hex[:10]
    report={'run_id':label,'steps':[],'expected_panes':[],'passed':False,'cleanup_confirmed':False}
    evidence=ROOT/'development'/'evidence'/('e2e-'+label+'.json')
    evidence.parent.mkdir(parents=True,exist_ok=True)

    def save(): evidence.write_text(json.dumps(clean(report),ensure_ascii=True,indent=2),encoding='utf-8')

    def run(resource,action,inputs=None,flags=(),accepted=(0,)):
        argv=[resource,action]
        if inputs is not None: argv.extend(['--input',json.dumps(inputs,ensure_ascii=True)])
        argv.extend(flags)
        proc=subprocess.run([sys.executable,'-B',str(CLI),*argv],capture_output=True,timeout=90)
        response=json.loads(proc.stdout)
        report['steps'].append({'operation':resource+'.'+action,'exit':proc.returncode,'response':response})
        save()
        if proc.returncode not in accepted or proc.stderr:
            raise RuntimeError('Operation failed: '+resource+'.'+action+': '+response.get('error',{}).get('code','unexpected output'))
        return response

    def write(resource,action,inputs):
        for _ in range(3):
            plan=run(resource,action,inputs,['--dry-run'])['data']
            response=run(resource,action,inputs,['--commit','--confirm',plan['plan_hash']],(0,5))
            if response['ok']: return response['data']
            error=response['error']
            if error['code']!='PLAN_MISMATCH' or error['outcome']!='not_started': raise RuntimeError('Cannot safely re-plan')
            time.sleep(.2)
        raise RuntimeError('Target did not stabilize for preview')

    wid=None
    try:
        # Compare only unique labels, rather than a live global workspace count.
        before=run('workspace','list',flags=['--limit','100'])['data']
        if any(item.get('label')==label for item in before['items']): raise RuntimeError('Unique test label collision')
        inputs={'cwd':str(ROOT),'label':label}
        plan=run('workspace','create',inputs,['--dry-run'])['data']
        after=run('workspace','list',flags=['--limit','100'])['data']
        if any(item.get('label')==label for item in after['items']): raise RuntimeError('Dry-run mutated layout')
        report['dry_run_zero_mutation']=True
        rejected=run('workspace','create',{**inputs,'label':label+'-changed'},['--commit','--confirm',plan['plan_hash']],(5,))
        if rejected['error']['code']!='PLAN_MISMATCH' or rejected['error']['outcome']!='not_started': raise RuntimeError('Changed plan was not safely rejected')
        report['tampered_plan_rejected']=True
        created=write('workspace','create',inputs)
        wid=created['verification']['resource_id']
        report['workspace_id']=wid
        report['expected_panes'].append(created['result']['root_pane']['pane_id'])
        tab=write('tab','create',{'workspace':wid,'cwd':str(ROOT),'label':'review-tab'})
        pane=tab['result']['root_pane']['pane_id']
        report['expected_panes'].append(pane)
        split=write('pane','split',{'id':created['result']['root_pane']['pane_id'],'direction':'right','cwd':str(ROOT)})
        report['expected_panes'].append(split['verification']['resource_id'])
        renamed=write('workspace','rename',{'id':wid,'label':label+'-renamed'})
        if not renamed['verification']['confirmed']: raise RuntimeError('Rename not confirmed')
        if args.agent:
            name='review-'+uuid.uuid4().hex[:12]
            write('agent','start',{'name':name,'kind':args.agent,'pane':pane})
            write('agent','prompt',{'target':name,'text':'Do not call tools or access files. Calculate 9 times 7. Reply on one line with prefix HERDR_REVIEW_REPLY: followed by the answer.'})
            deadline=time.monotonic()+100
            while time.monotonic()<deadline:
                waited=run('agent','wait',{'target':name},['--timeout','20'],(0,4))
                if not waited['ok'] and waited['error']['code']!='TIMEOUT': raise RuntimeError('Unexpected wait failure')
                text=run('agent','read',{'target':name,'lines':80})['data']['text']
                if 'HERDR_REVIEW_REPLY: 63' in text:
                    report['verified_reply']='HERDR_REVIEW_REPLY: 63'
                    break
                current=run('agent','get',{'target':name})['data']['agent']
                if current.get('agent_status')=='blocked': raise RuntimeError('Agent requires manual decision; no approval automated')
                time.sleep(.5)
            else: raise RuntimeError('No verified reply before deadline')
        report['passed']=True
    except Exception as error:
        report['error']=str(error)
    finally:
        if wid:
            try:
                listed=run('pane','list',{'workspace':wid},['--limit','100'])['data']
                actual={item['pane_id'] for item in listed['items']}
                if listed['pagination']['truncated'] or actual!=set(report['expected_panes']):
                    raise RuntimeError('Test topology changed; preserved for reconciliation')
                closed=write('workspace','close',{'id':wid})
                report['cleanup_confirmed']=closed['verification']['confirmed']
            except Exception as error: report['cleanup_error']=str(error)
        save()
    print(json.dumps({'ok':report['passed'] and report['cleanup_confirmed'],'workspace':wid,'cleanup_confirmed':report['cleanup_confirmed'],'evidence':str(evidence)},ensure_ascii=True))
    return 0 if report['passed'] and report['cleanup_confirmed'] else 1


if __name__=='__main__': raise SystemExit(main())
