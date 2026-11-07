#!/usr/bin/env python3
"""Herdr Agent adapter: typed operations over the official Herdr TUI CLI.

Python 3.10+, standard library. No shell, daemon, credentials, or auto retries.
"""
import argparse
import getpass
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid

VERSION = '1.0.1'
SCHEMA = '1.0'
MAX_BYTES = 1024 * 1024
MAX_INPUT_BYTES = 65536
ERRORS = {
    'INVALID_INPUT': (2, False, 'Correct inputs using schema or command help.'),
    'DEPENDENCY_MISSING': (3, False, 'Install the official Herdr TUI CLI.'),
    'OUTSIDE_HERDR': (3, False, 'Restart the Agent inside a Herdr-managed pane.'),
    'INCOMPATIBLE_VERSION': (3, False, 'Use the tested Herdr TUI 0.9.5, or validate a new adapter baseline.'),
    'RESOURCE_NOT_FOUND': (3, False, 'Discover current resource IDs before retrying.'),
    'BACKEND_UNAVAILABLE': (4, True, 'Check the inherited Herdr session; do not restart it automatically.'),
    'TIMEOUT': (4, True, 'Inspect resource state before retrying.'),
    'OUTPUT_LIMIT': (1, False, 'Narrow the query or use the documented native interface.'),
    'BACKEND_ERROR': (1, False, 'Inspect backend_code and reconcile target state.'),
    'BACKEND_PROTOCOL': (1, False, 'Check CLI/server compatibility and adapter baseline.'),
    'STATE_CONFLICT': (5, False, 'Read target state and prepare a fresh plan.'),
    'PLAN_MISMATCH': (5, False, 'Run --dry-run again and use its new plan hash.'),
    'INTERNAL': (1, False, 'Stop; inspect local implementation using the request ID.'),
    'INTERRUPTED': (130, False, 'Stop; reconcile any dispatched mutation.'),
}


class Failure(Exception):
    def __init__(self, code, message, outcome='not_started', details=None):
        self.code, self.message, self.outcome = code, message, outcome
        self.details = details or {}


def field(kind='str', required=False, flag=None, **kw):
    return dict(type=kind, required=required, flag=flag, **kw)


# The single command registry drives discovery, input validation, and argv.
OPS = {}
def register(name, fields=None, effect='read', result='json', collection=None, description=''):
    OPS[name] = dict(fields=fields or {}, effect=effect, result=result,
                     collection=collection, description=description)


ID = lambda: field(required=True, pattern=r'w[0-9A-Za-z]+(?::[tp][0-9A-Za-z]+)?')
TARGET = lambda: field(required=True, pattern=r'(?:w[0-9A-Za-z]+:p[0-9A-Za-z]+|[a-z][a-z0-9_-]{0,31})')
for resource, collection in [('workspace','workspaces'),('tab','tabs'),('pane','panes'),('agent','agents')]:
    fields = {} if resource in ['workspace','agent'] else {'workspace':field(flag='--workspace',pattern=r'w[0-9A-Za-z]+')}
    register(resource+'.list', fields, collection=collection, description='List live '+collection)
    register(resource+'.get', {'target':TARGET()} if resource=='agent' else {'id':ID()},description='Inspect one live '+resource)
    if resource != 'agent':
        register(resource+'.close',{'id':ID()},effect='destructive',description='Close the exact '+resource+' and its processes')
    register(resource+'.rename', {'target':TARGET(),'name':field(required=True,pattern=r'[a-z][a-z0-9_-]{0,31}')} if resource=='agent' else {'id':ID(),'label':field(required=True,max_length=160)},effect='write',description='Rename the exact '+resource)
    if resource!='agent':
        pattern={'workspace':r'w[0-9A-Za-z]+','tab':r'w[0-9A-Za-z]+:t[0-9A-Za-z]+','pane':r'w[0-9A-Za-z]+:p[0-9A-Za-z]+'}[resource]
        for action in ['get','close','rename']:
            OPS[resource+'.'+action]['fields']['id']['pattern']=pattern
for resource in ['workspace','tab']:
    fields={'cwd':field('directory',True,'--cwd'),'label':field(required=True,flag='--label',max_length=160)}
    if resource=='tab': fields={'workspace':field(required=True,flag='--workspace',pattern=r'w[0-9A-Za-z]+'),**fields}
    register(resource+'.create',fields,effect='write',description='Create with explicit cwd and label, preserving user focus')
register('pane.split',{'id':field(required=True,pattern=r'w[0-9A-Za-z]+:p[0-9A-Za-z]+'),'direction':field(required=True,flag='--direction',enum=['right','down']),'cwd':field('directory',True,'--cwd')},effect='write',description='Create sibling pane without taking focus')
register('pane.current',description='Resolve the invoking pane, never UI focus')
register('pane.layout',{'id':field(required=True,flag='--pane',pattern=r'w[0-9A-Za-z]+:p[0-9A-Za-z]+')},description='Inspect pane geometry')
register('pane.process-info',{'id':field(required=True,flag='--pane',pattern=r'w[0-9A-Za-z]+:p[0-9A-Za-z]+')},description='Inspect foreground occupancy')
for resource in ['pane','agent']:
    register(resource+'.read',{'target':TARGET(),'source':field(flag='--source',enum=['visible','recent','recent-unwrapped','detection'],default='recent-unwrapped'),'lines':field('int',flag='--lines',default=80,minimum=1,maximum=500)},result='text',description='Read a bounded terminal snapshot')
OPS['pane.read']['fields']['target']['pattern']=r'w[0-9A-Za-z]+:p[0-9A-Za-z]+'
register('agent.start',{'name':field(required=True,pattern=r'[a-z][a-z0-9_-]{0,31}'),'kind':field(required=True,flag='--kind',enum=['codex','claude']),'pane':field(required=True,flag='--pane',pattern=r'w[0-9A-Za-z]+:p[0-9A-Za-z]+')},effect='write',description='Start Codex or Claude in an existing idle shell; no native permission flags')
register('agent.prompt',{'target':TARGET(),'text':field(required=True,max_length=16000)},effect='write',description='Submit one prompt; submission is not task completion')
register('agent.wait',{'target':TARGET()},description='Wait at most the configured seconds for a settled lifecycle state')
for operation,definition in OPS.items():
    definition.update(is_idempotent=definition['effect']=='read',dry_run_supported=definition['effect']!='read',
                      input_sources=['--input','--file','stdin via --file -'],
                      output_shape='text/line_limit/truncated' if definition['result']=='text' else ('items/pagination/fields' if definition['collection'] else 'official result plus verification for writes'))


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()


def clean(value):
    if isinstance(value,dict):
        return {k:('[REDACTED]' if re.search(r'(?:password|secret|api[_-]?key|authorization|cookie|agent_session|session[_-]?id|access[_-]?token|refresh[_-]?token|client[_-]?secret|private[_-]?key)',k,re.I) else clean(v)) for k,v in value.items()}
    if isinstance(value,list): return [clean(v) for v in value]
    if not isinstance(value,str): return value
    value = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', value)
    value = re.sub(r'\x1b\][^\x07]*(?:\x07|\x1b\\)', '', value)
    value = re.sub(r'(?:sk-[A-Za-z0-9_-]{12,}|(?i:bearer)\s+[A-Za-z0-9._~-]+)', '[REDACTED]', value)
    value = re.sub(r'(?i)(password|api[_-]?key|access[_-]?token|secret|authorization|cookie)(\s*[=:]\s*)[^\s,;]+', r'\1\2[REDACTED]', value)
    value = re.sub(r'-----BEGIN [^-]*PRIVATE KEY-----.*?-----END [^-]*PRIVATE KEY-----', '[REDACTED PRIVATE KEY]', value, flags=re.S)
    return ''.join(c for c in value if c in '\n\t' or (ord(c)>=32 and not 0x7f<=ord(c)<=0x9f and not 0x200b<=ord(c)<=0x200f and not 0x202a<=ord(c)<=0x202e and not 0x2066<=ord(c)<=0x2069))


class Backend:
    def __init__(self, timeout):
        self.timeout=timeout
        candidate=os.environ.get('HERDR_BIN_PATH') or shutil.which('herdr')
        if not candidate: raise Failure('DEPENDENCY_MISSING','Official herdr executable not found')
        self.binary=Path(candidate).resolve()
        if self.binary.name.lower() not in ['herdr.exe','herdr'] or not self.binary.is_file():
            raise Failure('DEPENDENCY_MISSING','Resolved executable must be the official herdr binary')
        self.version=self.raw(['--version']).strip()
        if self.version!='herdr 0.9.5': raise Failure('INCOMPATIBLE_VERSION','Adapter baseline is Herdr TUI 0.9.5',details={'observed':self.version})

    def raw(self, argv, mutation=False, timeout=None):
        outcome='unknown' if mutation else 'not_started'
        try:
            proc=subprocess.Popen([str(self.binary),*argv],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=str(Path.cwd()),env=os.environ.copy(),shell=False,bufsize=0)
        except OSError:
            raise Failure('DEPENDENCY_MISSING','Cannot launch resolved herdr executable')
        chunks=[bytearray(),bytearray()]
        overflow=threading.Event()
        completed=[threading.Event(),threading.Event()]
        read_failed=threading.Event()
        def drain(stream,index):
            try:
                while True:
                    chunk=os.read(stream.fileno(),8192)
                    if not chunk: break
                    if len(chunks[index])+len(chunk)>MAX_BYTES:
                        overflow.set()
                        break
                    chunks[index].extend(chunk)
            except (OSError,ValueError):
                read_failed.set()
            finally:
                completed[index].set()
        threads=[threading.Thread(target=drain,args=(stream,i),daemon=True) for i,stream in enumerate([proc.stdout,proc.stderr])]
        for thread in threads: thread.start()
        deadline=time.monotonic()+(timeout or self.timeout)
        error=None
        try:
            # An exited parent can leave inherited stdout open in a child.
            # Bound draining as well as process lifetime; never close a buffered
            # pipe while another thread holds its read lock.
            while proc.poll() is None or not all(event.is_set() for event in completed):
                if overflow.is_set(): error='OUTPUT_LIMIT'; break
                if time.monotonic()>deadline: error='TIMEOUT'; break
                time.sleep(0.01)
        except KeyboardInterrupt:
            error='INTERRUPTED'
        finally:
            if error and proc.poll() is None: proc.kill()
            proc.wait()
            proc.stdout.close(); proc.stderr.close()
            for thread in threads: thread.join(timeout=0.05)
        if overflow.is_set(): error=error or 'OUTPUT_LIMIT'
        if error: raise Failure(error,'Herdr invocation stopped: '+error,outcome,{'mutation_may_continue':mutation})
        if read_failed.is_set(): raise Failure('BACKEND_PROTOCOL','Failed to read complete Herdr response',outcome)
        try: out,err=[bytes(x).decode('utf-8') for x in chunks]
        except UnicodeError: raise Failure('BACKEND_PROTOCOL','Herdr returned invalid UTF-8',outcome)
        if proc.returncode:
            try:
                body=json.loads(err or out)
                body=body.get('error',{}) if isinstance(body,dict) else {}
                if not isinstance(body,dict): body={}
            except ValueError: body={}
            upstream=body.get('code','')
            mapping={'not_found':'RESOURCE_NOT_FOUND','pane_not_found':'RESOURCE_NOT_FOUND','workspace_not_found':'RESOURCE_NOT_FOUND','tab_not_found':'RESOURCE_NOT_FOUND','agent_not_found':'RESOURCE_NOT_FOUND','agent_blocked':'STATE_CONFLICT','agent_not_ready':'STATE_CONFLICT','timeout':'TIMEOUT','agent_prompt_stalled':'STATE_CONFLICT'}
            code='INVALID_INPUT' if proc.returncode==2 else mapping.get(upstream,'BACKEND_ERROR')
            raise Failure(code,'Official Herdr command failed',outcome,{'backend_code':upstream,'backend_message':body.get('message','Unstructured backend error omitted'),'backend_exit':proc.returncode})
        return out

    def call(self,argv,mutation=False):
        raw=self.raw(argv,mutation)
        try: data=json.loads(raw)
        except ValueError: raise Failure('BACKEND_PROTOCOL','Expected one JSON result', 'unknown' if mutation else 'not_started')
        if not isinstance(data,dict) or not isinstance(data.get('result'),dict) or 'error' in data:
            raise Failure('BACKEND_PROTOCOL','Invalid official result envelope','unknown' if mutation else 'not_started')
        return data['result']


def validate_input(op, value):
    if not isinstance(value,dict): raise Failure('INVALID_INPUT','Input must be a JSON object')
    unknown=set(value)-set(op['fields'])
    if unknown: raise Failure('INVALID_INPUT','Unknown input fields',details={'unknown':sorted(unknown),'accepted':list(op['fields'])})
    result={}
    for name,spec in op['fields'].items():
        item=value.get(name,spec.get('default'))
        if item is None:
            if spec['required']: raise Failure('INVALID_INPUT','Required field missing: '+name)
            continue
        if spec['type']=='int':
            if type(item)!=int or not spec['minimum']<=item<=spec['maximum']:
                raise Failure('INVALID_INPUT','Invalid integer range for '+name,details=spec)
        else:
            if not isinstance(item,str) or not item or len(item)>spec.get('max_length',4096):
                raise Failure('INVALID_INPUT','Invalid string field: '+name)
            # No option operands, NUL, ANSI, bidi, or invisible input controls.
            if item.startswith('-') or any((ord(c)<32 and c not in '\n\t') or 0x7f<=ord(c)<=0x9f or 0x200b<=ord(c)<=0x200f or 0x202a<=ord(c)<=0x202e or 0x2066<=ord(c)<=0x2069 or 0xd800<=ord(c)<=0xdfff for c in item):
                raise Failure('INVALID_INPUT','Unsafe option/control characters in '+name)
            if spec.get('pattern') and not re.fullmatch(spec['pattern'],item):
                raise Failure('INVALID_INPUT','Invalid identifier: '+name,details={'pattern':spec['pattern']})
            if 'enum' in spec and item not in spec['enum']:
                raise Failure('INVALID_INPUT','Invalid enum: '+name,details={'accepted':spec['enum']})
            if spec['type']=='directory':
                p=Path(item)
                if not p.is_absolute() or not p.is_dir(): raise Failure('INVALID_INPUT','cwd must be an existing absolute directory')
                item=str(p.resolve())
        result[name]=item
    return result


def argv_for(name,op,inputs,seconds):
    argv=name.split('.')
    for key,spec in op['fields'].items():
        if key not in inputs: continue
        if spec.get('flag'): argv.append(spec['flag'])
        argv.append(str(inputs[key]))
    if name in ['workspace.create','tab.create','pane.split']: argv.append('--no-focus')
    if name=='pane.current': argv.append('--current')
    if name in ['agent.start','agent.wait']:
        argv.extend(['--timeout',str(max(4000,int((seconds-1)*1000)))])
    return argv


def preflight(backend,name,inputs):
    resource,action=name.split('.')
    target=inputs.get('id') or inputs.get('target')
    if action=='close' and target in [os.environ.get('HERDR_WORKSPACE_ID'),os.environ.get('HERDR_TAB_ID'),os.environ.get('HERDR_PANE_ID')]:
        raise Failure('STATE_CONFLICT','Adapter refuses to close its own inherited caller context; use an explicitly authorized native workflow')
    state={}
    caller=None
    if OPS[name]['effect']!='read':
        caller=backend.call(['pane','current','--current']).get('pane')
        if not isinstance(caller,dict) or not caller.get('pane_id'):
            raise Failure('BACKEND_PROTOCOL','Cannot resolve live caller context before mutation')
        if action=='close' and target in [caller.get('workspace_id'),caller.get('tab_id'),caller.get('pane_id')]:
            raise Failure('STATE_CONFLICT','Close target contains the live invoking pane')
    if action in ['get','close','rename','read','layout','process-info','split'] and target:
        state=backend.call([resource,'get',target])
    if name=='tab.create': state=backend.call(['workspace','get',inputs['workspace']])
    if action=='close' and resource in ['workspace','tab']:
        workspace=target if resource=='workspace' else target.split(':')[0]
        panes=backend.call(['pane','list','--workspace',workspace]).get('panes')
        if not isinstance(panes,list) or any(not isinstance(p,dict) or not p.get('pane_id') for p in panes):
            raise Failure('BACKEND_PROTOCOL','Invalid topology for close preview')
        state['close_topology']=sorted(
            [(p['pane_id'],p.get('terminal_id')) for p in panes if resource=='workspace' or p.get('tab_id')==target])
    if name=='agent.start':
        state=backend.call(['pane','get',inputs['pane']])
        pane=state.get('pane',{})
        if pane.get('agent'): raise Failure('STATE_CONFLICT','Agent start requires an available shell pane')
        # Windows does not expose Unix foreground groups reliably. Refuse any
        # explicit non-shell foreground process, and let official start enforce readiness.
        process=backend.call(['pane','process-info','--pane',inputs['pane']])
        foreground=process.get('process_info',{}).get('foreground_processes',[])
        shells={'powershell','powershell.exe','pwsh','pwsh.exe','cmd','cmd.exe','bash','bash.exe','zsh','fish','sh'}
        if any(p.get('name','').lower() not in shells for p in foreground):
            raise Failure('STATE_CONFLICT','Pane foreground is not an available shell')
        agents=backend.call(['agent','list']).get('agents',[])
        if any(a.get('name')==inputs['name'] for a in agents): raise Failure('STATE_CONFLICT','Agent name already in use')
    if name=='agent.prompt':
        state=backend.call(['agent','get',inputs['target']])
        agent=state.get('agent',{})
        if agent.get('agent_status') not in ['idle','done'] or agent.get('interactive_ready') is not True:
            raise Failure('STATE_CONFLICT','Agent must be interactive_ready and idle/done before a new prompt',details={'status':agent.get('agent_status')})
    # Strip display revisions/completion badges: only identity and readiness
    # should invalidate a plan, not the user looking at a pane.
    def identity(node):
        if isinstance(node,dict): return {k:identity(v) for k,v in node.items() if k in ['workspace','tab','pane','agent','workspace_id','tab_id','pane_id','terminal_id','cwd','name','agent_session','value','kind','source','close_topology']}
        return node
    return identity(state)


def plan_for(backend,name,op,inputs,argv,state,seconds):
    return {'operation':name,'effect':op['effect'],'inputs':inputs,'argv':argv,
            'binary':str(backend.binary),'binary_sha256':hashlib.sha256(backend.binary.read_bytes()).hexdigest(),
            'actor':getpass.getuser(),'cwd':str(Path.cwd().resolve()),
            'environment_sha256':digest(dict(os.environ)),
            'target_socket':os.environ.get('HERDR_SOCKET_PATH'),
            'target_session':os.environ.get('HERDR_SESSION','default'),
            'identity':state,'timeout_seconds':seconds,'valid_until_unix':(int(time.time())//300+1)*300,
            'isolation':'existing Herdr permissions; no added sandbox'}


def verify(backend,name,inputs,result):
    resource,action=name.split('.')
    if action=='create':
        item=result.get(resource)
        key=resource+'_id'
        if not isinstance(item,dict) or not isinstance(item.get(key),str): raise Failure('BACKEND_PROTOCOL','Create response missing stable ID','committed')
        confirmed=backend.call([resource,'get',item[key]])
        current=confirmed.get(resource)
        if not isinstance(current,dict) or current.get(key)!=item[key] or current.get('label')!=inputs['label']:
            raise Failure('BACKEND_PROTOCOL','Created resource did not reconcile with its ID and label','committed')
        return {'state':'created','confirmed':True,'resource_id':item[key]}
    if name=='pane.split':
        pane=result.get('pane')
        pane=pane.get('pane_id') if isinstance(pane,dict) else None
        if not pane: raise Failure('BACKEND_PROTOCOL','Split missing pane ID','committed')
        current=backend.call(['pane','get',pane]).get('pane')
        if not isinstance(current,dict) or current.get('pane_id')!=pane:
            raise Failure('BACKEND_PROTOCOL','Split ID did not reconcile','committed')
        return {'state':'created','confirmed':True,'resource_id':pane}
    if action=='close':
        items=backend.call([resource,'list']).get(OPS[resource+'.list']['collection'])
        if not isinstance(items,list) or any(not isinstance(x,dict) or not isinstance(x.get(resource+'_id'),str) for x in items):
            raise Failure('BACKEND_PROTOCOL','Cannot confirm close from an invalid resource list','unknown')
        if any(x.get(resource+'_id')==inputs['id'] for x in items): raise Failure('STATE_CONFLICT','Close target still listed','unknown')
        return {'state':'closed','confirmed':True,'resource_id':inputs['id']}
    if name=='agent.start':
        agent=backend.call(['agent','get',inputs['name']]).get('agent')
        if not isinstance(agent,dict) or agent.get('name')!=inputs['name'] or agent.get('pane_id')!=inputs['pane'] or agent.get('agent')!=inputs['kind'] or agent.get('interactive_ready') is not True:
            raise Failure('STATE_CONFLICT','Agent launched but not verified ready','committed')
        return {'state':'ready','confirmed':True,'name':inputs['name'],'pane_id':inputs['pane']}
    if name=='agent.prompt':
        agent=result.get('agent')
        if not isinstance(agent,dict) or not agent.get('pane_id'):
            raise Failure('BACKEND_PROTOCOL','Prompt response missing resolved Agent','unknown')
        return {'state':'submitted','task_complete':False,'target':inputs['target']}
    if action=='rename':
        target=inputs['name'] if resource=='agent' else inputs['id']
        current=backend.call([resource,'get',target]).get(resource)
        field='name' if resource=='agent' else 'label'
        if not isinstance(current,dict) or current.get(field)!=inputs[field]:
            raise Failure('BACKEND_PROTOCOL','Renamed value did not reconcile','committed')
        return {'state':'renamed','confirmed':True,'resource_id':current.get(resource+'_id') or current.get('pane_id')}
    return {'state':'accepted','confirmed':False}


def project(items,fields):
    if not fields: return items
    if any(not isinstance(item,dict) for item in items): raise Failure('BACKEND_PROTOCOL','Invalid list record')
    accepted=sorted({key for item in items for key in item})
    if any(x not in accepted for x in fields) and items:
        raise Failure('INVALID_INPUT','Unknown projection field',details={'accepted':accepted})
    return [{k:v for k,v in item.items() if k in fields or k in ['workspace_id','tab_id','pane_id','name']} for item in items]


def schema():
    return {'tool_version':VERSION,'schema_version':SCHEMA,'tested_backend':'herdr 0.9.5','tested_platform':'Windows x86_64',
            'commands':OPS,'errors':{k:{'exit':v[0],'retryable':v[1],'next_action':v[2]} for k,v in ERRORS.items()},
            'input':{'sources':['--input JSON','--file UTF-8 path','--file -'],'maximum_bytes':65536,'unknown_fields':'reject'},
            'output':{'formats':['json','jsonl'],'terminal_envelopes':1,'errors_channel':'stdout','projection':'flat top-level list item keys; identity fields retained'},
            'pagination':{'default_limit':20,'max_limit':100,'mechanism':'client-side offset over live native list; not a snapshot cursor'},
            'execution':{'timeout_seconds_default':30,'timeout_seconds_max':60,'output_bytes_per_backend_stream_max':MAX_BYTES,'automatic_retry':False,'idempotency_key':False,'dry_run':'default for writes','commit':'--commit --confirm SHA256 from dry-run'},
            'native_only_domains':['worktree','SSH machines','plugins','integrations','configuration','session recovery','socket subscriptions','terminal attach','raw shell input'],
            'examples':['workspace list --limit 10','workspace create --file request.json --dry-run','agent prompt --file - --dry-run']}


class Parser(argparse.ArgumentParser):
    def error(self,message): raise Failure('INVALID_INPUT',message)


def parse(argv):
    extra='Example: python herdr_agent.py workspace list --limit 10. Use schema for typed JSON input fields. Writes default to preview; explicit --commit --confirm HASH executes the unchanged plan.'
    if len(argv)>=2 and argv[0]+'.'+argv[1] in OPS:
        op=OPS[argv[0]+'.'+argv[1]]
        extra+='\nOperation: '+op['description']+'\nEffect: '+op['effect']+'\nInput fields: '+json.dumps(op['fields'],ensure_ascii=True)
    parser=Parser(description=__doc__,allow_abbrev=False,epilog=extra,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('resource',choices=['version','schema','errors','doctor','workspace','tab','pane','agent'])
    parser.add_argument('action',nargs='?')
    sources=parser.add_mutually_exclusive_group()
    sources.add_argument('--input',help='JSON object; never shell source')
    sources.add_argument('--file',help='UTF-8 JSON input path; - means stdin')
    parser.add_argument('--output',choices=['json','jsonl'],default='json')
    parser.add_argument('--timeout',type=float,default=30,help='Seconds per backend call, 1..60; wait/start require >=5')
    parser.add_argument('--limit',type=int,default=20)
    parser.add_argument('--offset',type=int,default=0)
    parser.add_argument('--fields',help='Comma-separated top-level list item fields, identity retained')
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--dry-run',action='store_true')
    mode.add_argument('--commit',action='store_true')
    parser.add_argument('--confirm',help='SHA256 from the unchanged current dry-run plan')
    parser.add_argument('--quiet',action='store_true',help='Only terminal response (already the default)')
    parser.add_argument('--no-input',action='store_true',help='Never open a prompt (always enforced)')
    parser.add_argument('--no-color',action='store_true',help='Never emit ANSI (always enforced)')
    args=parser.parse_args(argv)
    if not math.isfinite(args.timeout) or not 1<=args.timeout<=60 or not 1<=args.limit<=100 or args.offset<0:
        raise Failure('INVALID_INPUT','timeout 1..60 seconds, limit 1..100, offset >=0 required')
    return args


def read_stdin(limit, timeout):
    """Read redirected UTF-8 bytes without an interactive or open-pipe hang."""
    if sys.stdin.isatty(): raise Failure('INVALID_INPUT','--file - requires redirected stdin, not an interactive terminal')
    fd=sys.stdin.fileno()
    deadline=time.monotonic()+timeout
    content=bytearray()
    if os.name=='nt':
        import ctypes
        from ctypes import wintypes
        import msvcrt
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        handle=wintypes.HANDLE(msvcrt.get_osfhandle(fd))
        kernel.GetFileType.argtypes=[wintypes.HANDLE]
        kernel.GetFileType.restype=wintypes.DWORD
        kind=kernel.GetFileType(handle)
        if kind==1: return os.read(fd,limit)  # bounded regular file
        if kind!=3: raise Failure('INVALID_INPUT','stdin must be a file or pipe')
        peek=kernel.PeekNamedPipe
        peek.argtypes=[wintypes.HANDLE,wintypes.LPVOID,wintypes.DWORD,wintypes.LPVOID,ctypes.POINTER(wintypes.DWORD),wintypes.LPVOID]
        peek.restype=wintypes.BOOL
    while len(content)<limit:
        if time.monotonic()>=deadline: raise Failure('TIMEOUT','Timed out waiting for JSON stdin; no mutation dispatched')
        if os.name=='nt':
            available=wintypes.DWORD()
            if not peek(handle,None,0,None,ctypes.byref(available),None):
                if ctypes.get_last_error() in [109,232]: break
                raise Failure('INVALID_INPUT','Cannot read stdin pipe')
            if not available.value:
                time.sleep(0.01)
                continue
            size=min(available.value,limit-len(content))
        else:
            import select
            readable,_,_=select.select([fd],[],[],max(0,deadline-time.monotonic()))
            if not readable: raise Failure('TIMEOUT','Timed out waiting for JSON stdin; no mutation dispatched')
            size=limit-len(content)
        chunk=os.read(fd,size)
        if not chunk: break
        content.extend(chunk)
    return bytes(content)


def decode_input(raw):
    def object_pairs(pairs):
        result={}
        for key,value in pairs:
            if key in result: raise Failure('INVALID_INPUT','Duplicate JSON field: '+key)
            result[key]=value
        return result
    def constant(value): raise Failure('INVALID_INPUT','Non-finite JSON constant is not supported: '+value)
    return json.loads(raw,object_pairs_hook=object_pairs,parse_constant=constant)


def load_input(args):
    try:
        if args.file:
            if args.file=='-': raw=read_stdin(MAX_INPUT_BYTES+1,args.timeout)
            else:
                path=Path(args.file)
                if not path.is_file(): raise Failure('INVALID_INPUT','--file must point to a regular JSON file')
                with path.open('rb') as stream: raw=stream.read(MAX_INPUT_BYTES+1)
            if len(raw)>MAX_INPUT_BYTES: raise Failure('INVALID_INPUT','JSON input exceeds 64 KiB')
            return decode_input(raw.decode('utf-8-sig'))
        if args.input is not None:
            if len(args.input.encode('utf-8'))>MAX_INPUT_BYTES: raise Failure('INVALID_INPUT','JSON input exceeds 64 KiB')
            return decode_input(args.input)
        return {}
    except (ValueError,UnicodeError,OSError,RecursionError): raise Failure('INVALID_INPUT','Cannot read a valid UTF-8 JSON input object')


def execute(args):
    if args.resource in ['schema','errors','version','doctor'] and args.action:
        raise Failure('INVALID_INPUT','This discovery command has no action operand')
    if args.resource in ['schema','errors','version','doctor'] and (args.input is not None or args.file is not None or args.commit or args.confirm or args.dry_run or args.fields or args.limit!=20 or args.offset):
        raise Failure('INVALID_INPUT','Discovery commands do not accept business inputs or write flags')
    if args.resource=='schema': return schema(),{}
    if args.resource=='errors': return schema()['errors'],{}
    if args.resource=='version': return {'tool':'herdr-agent','tool_version':VERSION,'schema_version':SCHEMA,'tested_backend':'herdr 0.9.5'},{}
    if args.resource=='doctor':
        if os.environ.get('HERDR_ENV')!='1': raise Failure('OUTSIDE_HERDR','Runtime control requires HERDR_ENV=1')
        backend=Backend(args.timeout)
        return {'backend':backend.version,'binary':str(backend.binary),'status':backend.raw(['status']),'config':backend.raw(['config','check']),'caller':backend.call(['pane','current','--current'])},{}
    name=args.resource+'.'+str(args.action)
    if name not in OPS: raise Failure('INVALID_INPUT','Unsupported operation',details={'accepted':list(OPS)})
    op=OPS[name]
    if name in ['agent.start','agent.wait'] and args.timeout<5: raise Failure('INVALID_INPUT','Agent start/wait requires timeout >=5 seconds')
    if args.fields and not op['collection']: raise Failure('INVALID_INPUT','--fields is supported only for list operations')
    if not op['collection'] and (args.limit!=20 or args.offset): raise Failure('INVALID_INPUT','--limit/--offset are supported only for list operations')
    if op['effect']=='read' and (args.commit or args.dry_run or args.confirm): raise Failure('INVALID_INPUT','Write flags are not valid for read operations')
    inputs=validate_input(op,load_input(args))
    if args.commit and not args.confirm: raise Failure('PLAN_MISMATCH','Commit requires --confirm hash from dry-run')
    if args.confirm and not args.commit: raise Failure('INVALID_INPUT','--confirm requires --commit')
    if os.environ.get('HERDR_ENV')!='1': raise Failure('OUTSIDE_HERDR','Runtime control requires HERDR_ENV=1')
    backend=Backend(args.timeout)
    state=preflight(backend,name,inputs)
    argv=argv_for(name,op,inputs,args.timeout)
    meta={'operation':name,'backend':backend.version,'effect':op['effect'],'automatic_retry':False}
    if op['effect']!='read':
        plan=plan_for(backend,name,op,inputs,argv,state,args.timeout)
        plan_hash=digest(plan)
        meta['plan_hash']=plan_hash
        if not args.commit:
            # Do not echo user prompt or full inherited environment into plans.
            preview={k:v for k,v in plan.items() if k not in ['inputs','argv','identity']}
            preview['input_fields']=list(inputs)
            preview['target']=inputs.get('id') or inputs.get('target') or inputs.get('workspace') or inputs.get('pane')
            preview['impact']='Stops processes in the exact target; no automatic group-close escalation' if op['effect']=='destructive' else op['description']
            preview['changes']={key:({'characters':len(value),'sha256':hashlib.sha256(value.encode('utf-8')).hexdigest()} if key=='text' else value) for key,value in inputs.items()}
            if 'close_topology' in state:
                preview['affected_panes']=[pane[0] for pane in state['close_topology']]
            return {'state':'planned','dry_run':True,'plan_hash':plan_hash,'plan':preview,'next_action':'Repeat the same command/input with --commit --confirm '+plan_hash},meta
        if args.confirm!=plan_hash: raise Failure('PLAN_MISMATCH','Inputs, target, environment, timeout or binary changed since preview')
        try:
            result=backend.call(argv,mutation=True)
        except Failure as failure:
            target=inputs.get('target') or inputs.get('id') or inputs.get('name') or inputs.get('pane')
            reconcile=['agent','get'] if name.startswith('agent.') else [name.split('.')[0],'list']
            payload={'target':target} if reconcile==['agent','get'] else None
            next_argv=[sys.executable,str(Path(__file__).resolve()),*reconcile]
            if payload: next_argv.extend(['--input',json.dumps(payload)])
            failure.details.update(operation=name,plan_hash=plan_hash,target=target,reconcile_argv=next_argv)
            raise
        try: verification=verify(backend,name,inputs,result)
        except Failure as failure:
            if failure.outcome=='not_started': failure.outcome='committed'
            failure.details.update({'plan_hash':plan_hash,'mutation_response':result})
            raise
        return {'state':verification['state'],'result':result,'verification':verification},meta
    if op['result']=='text':
        raw=clean(backend.raw(argv))
        return {'text':raw[:64000],'line_limit':inputs.get('lines',80),'truncated':len(raw)>64000},meta
    result=backend.call(argv)
    if op['collection']:
        items=result.get(op['collection'])
        if not isinstance(items,list) or any(not isinstance(item,dict) for item in items): raise Failure('BACKEND_PROTOCOL','Missing or invalid list collection')
        fields=args.fields.split(',') if args.fields else None
        projected=project(items,fields)
        page=projected[args.offset:args.offset+args.limit]
        next_offset=args.offset+len(page)
        return {'items':page,'pagination':{'offset':args.offset,'limit':args.limit,'returned':len(page),'total':len(items),'truncated':next_offset<len(items),'next_offset':next_offset if next_offset<len(items) else None,'consistency':'live list, client-side slicing'},'fields':fields},meta
    if name.split('.')[1] in ['get','current']:
        item=result.get(name.split('.')[0])
        if not isinstance(item,dict): raise Failure('BACKEND_PROTOCOL','Missing expected resource object')
    return result,meta


def main(argv=None):
    start=time.monotonic()
    request='req_'+uuid.uuid4().hex
    try:
        args=parse(sys.argv[1:] if argv is None else argv)
        data,meta=execute(args)
        envelope={'schema_version':SCHEMA,'ok':True,'type':'result','data':clean(data),'meta':meta}
        code=0
    except Failure as failure:
        code,retryable,next_action=ERRORS[failure.code]
        # Retrying the same non-idempotent mutation is never recommended.
        if failure.outcome in ['unknown','committed']: retryable=False
        followup=['schema'] if failure.code in ['INVALID_INPUT','PLAN_MISMATCH'] else ['doctor']
        if failure.outcome in ['unknown','committed']:
            followup=['workspace','list']
        next_argv=failure.details.get('reconcile_argv') or [sys.executable,str(Path(__file__).resolve()),*followup]
        envelope={'schema_version':SCHEMA,'ok':False,'type':'error','error':{'code':failure.code,'message':clean(failure.message),'retryable':retryable,'outcome':failure.outcome,'details':clean(failure.details),'next_actions':[{'argv':next_argv,'purpose':next_action}]},'meta':{}}
    except KeyboardInterrupt:
        code=130
        envelope={'schema_version':SCHEMA,'ok':False,'type':'error','error':{'code':'INTERRUPTED','message':'Interrupted','retryable':False,'outcome':'unknown','details':{},'next_actions':[{'action':'Inspect target state before retrying'}]},'meta':{}}
    except Exception:
        code=1
        envelope={'schema_version':SCHEMA,'ok':False,'type':'error','error':{'code':'INTERNAL','message':'Unexpected internal error; no unredacted exception emitted','retryable':False,'outcome':'unknown','details':{},'next_actions':[{'action':'Stop and inspect local implementation'}]},'meta':{}}
    envelope['meta'].update(request_id=request,duration_ms=int((time.monotonic()-start)*1000))
    if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    sys.stdout.write(json.dumps(envelope,ensure_ascii=True,separators=(',',':'))+'\n')
    return code


if __name__=='__main__': raise SystemExit(main())
