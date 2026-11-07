import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.dont_write_bytecode=True

SCRIPT=Path(__file__).resolve().parents[1]/'scripts'/'herdr_agent.py'
spec=importlib.util.spec_from_file_location('adapter',SCRIPT)
a=importlib.util.module_from_spec(spec); spec.loader.exec_module(a)


class FixtureBackend:
    """Deterministic contract backend; never contacts a running Herdr session."""
    def __init__(self, timeout):
        self.timeout=timeout
        self.binary=Path(sys.executable)
        self.version='herdr 0.9.5'
        self.calls=[]

    def raw(self,args,*unused,**kwargs):
        self.calls.append(args)
        if args[:2] in [['agent','read'],['pane','read']]: return 'Fixture terminal output\n'
        return 'fixture status\n'

    def call(self,args,*unused,**kwargs):
        self.calls.append(args)
        if args[:2]==['workspace','list']:
            return {'workspaces':[{'workspace_id':'w1','label':'first'},{'workspace_id':'w2','label':'second'}]}
        if args[:2]==['workspace','get']:
            return {'workspace':{'workspace_id':args[2],'label':'fixture'}}
        if args[:2]==['pane','current']:
            return {'pane':{'pane_id':'w1:p1','tab_id':'w1:t1','workspace_id':'w1','terminal_id':'t1'}}
        if args[:2]==['pane','get']:
            return {'pane':{'pane_id':args[2],'tab_id':'w2:t1','workspace_id':'w2','terminal_id':'t2'}}
        if args[:2]==['pane','list']:
            return {'panes':[{'pane_id':'w2:p1','tab_id':'w2:t1','workspace_id':'w2','terminal_id':'t2'}]}
        if args[:2]==['pane','process-info']: return {'process_info':{'foreground_processes':[]}}
        if args[:2]==['agent','list']: return {'agents':[]}
        if args[:2]==['agent','get']:
            return {'agent':{'name':args[2],'agent':'claude','pane_id':'w2:p1','agent_status':'idle','interactive_ready':True}}
        raise AssertionError('Unexpected fixture invocation: '+repr(args))


class ContractTests(unittest.TestCase):
    def invoke(self,args,expected=0):
        p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--fixture',*args],capture_output=True,timeout=20)
        self.assertEqual(p.returncode,expected,p.stdout.decode())
        self.assertEqual(p.stderr,b'')
        self.assertFalse(p.stdout.startswith(b'\xef\xbb\xbf'))
        self.assertNotIn(b'\x1b',p.stdout)
        self.assertEqual(len(p.stdout.splitlines()),1)
        d=json.loads(p.stdout)
        self.assertEqual(d['schema_version'],'1.0')
        self.assertEqual(d['ok'],expected==0)
        return d

    def test_discovery(self):
        d=self.invoke(['schema'])
        self.assertEqual(set(d['data']['commands']),set(a.OPS))
        self.invoke(['version','--output','jsonl','--quiet','--no-input','--no-color'])
        self.invoke(['errors'])

    def test_usage_errors_machine_output(self):
        for args in [[],['wrong'],['workspace','wrong'],['workspace','list','--limit','101'],['workspace','list','--tim','1'],['version','extra'],['version','--commit']]:
            with self.subTest(args=args): self.invoke(args,2)

    def test_precise_identifier_types(self):
        for name,data in [('workspace.close',{'id':'w5:p1'}),('tab.close',{'id':'w1'}),('pane.read',{'target':'reviewer'})]:
            with self.assertRaises(a.Failure): a.validate_input(a.OPS[name],data)
        for name,data in [('workspace.get',{'id':'wA'}),('tab.get',{'id':'wA:tB'}),('pane.get',{'id':'wA:pC'}),('agent.get',{'target':'wA:pC'})]:
            self.assertEqual(a.validate_input(a.OPS[name],data),data)

    def test_hostile_input(self):
        for value in ['--help','a\x1b[31mb','bad\u202ename','bad\u200bname']:
            with self.assertRaises(a.Failure): a.validate_input(a.OPS['agent.prompt'],{'target':'reviewer','text':value})
        with self.assertRaises(a.Failure): a.validate_input(a.OPS['workspace.list'],{'extra':1})
        with self.assertRaises(a.Failure): a.validate_input(a.OPS['pane.read'],{'target':'w1:p1','lines':True})

    def test_metacharacters_are_one_argv_operand(self):
        text='quote " ; $(calc) & | > 中文\nsecond line'
        data=a.validate_input(a.OPS['agent.prompt'],{'target':'reviewer','text':text})
        argv=a.argv_for('agent.prompt',a.OPS['agent.prompt'],data,30)
        self.assertEqual(argv,['agent','prompt','reviewer',text])

    def test_redaction_and_terminal_controls(self):
        canaries=['sk-'+'abc123'*3,'bearer abc.secret.token','password='+'canary-password','api_key=KEY-CANARY']
        out=a.clean({'agent_session':{'value':'native-private-id'},'text':'\x1b[31m'+ ' '.join(canaries)+'\u202e'})
        rendered=json.dumps(out)
        for secret in ['canary-password','KEY-CANARY','abc.secret.token','native-private-id','sk-'+'abc123'*3]:
            self.assertNotIn(secret,rendered)
        self.assertNotIn('\x1b',out['text'])

    def test_nonmanaged_gate(self):
        with patch.dict(os.environ,{'HERDR_ENV':'0'}):
            with self.assertRaises(a.Failure) as cm: a.execute(a.parse(['workspace','list']))
            self.assertEqual(cm.exception.code,'OUTSIDE_HERDR')

    def test_caller_close_guard(self):
        with patch.dict(os.environ,{'HERDR_WORKSPACE_ID':'w1'}),self.assertRaises(a.Failure) as cm:
            a.preflight(None,'workspace.close',{'id':'w1'})
        self.assertEqual(cm.exception.code,'STATE_CONFLICT')

    def test_missing_dependency_and_version(self):
        with patch.dict(os.environ,{'HERDR_BIN_PATH':'Z:/does-not-exist/herdr.exe'}):
            with self.assertRaises(a.Failure) as cm: a.Backend(1)
            self.assertEqual(cm.exception.code,'DEPENDENCY_MISSING')
        with tempfile.TemporaryDirectory() as tmp:
            binary=Path(tmp)/'herdr.exe'
            binary.write_bytes(b'fixture')
            with patch.dict(os.environ,{'HERDR_BIN_PATH':str(binary)}),patch.object(a.Backend,'raw',return_value='herdr 999.0\n'):
                with self.assertRaises(a.Failure) as cm: a.Backend(1)
                self.assertEqual(cm.exception.code,'INCOMPATIBLE_VERSION')

    def test_stdin_utf8_and_large_input(self):
        data=json.dumps({'target':'reviewer','lines':10}).encode()
        driver=[sys.executable,str(Path(__file__).resolve()),'--fixture']
        p=subprocess.run([*driver,'agent','read','--file','-'],input=data,capture_output=True)
        self.assertEqual(p.returncode,0,p.stdout)
        self.assertIn('text',json.loads(p.stdout)['data'])
        p=subprocess.run([*driver,'pane','read','--file','-'],input=b'x'*65537,capture_output=True)
        self.assertEqual(p.returncode,2)
        self.assertEqual(json.loads(p.stdout)['error']['code'],'INVALID_INPUT')

    def test_list_pagination_projection(self):
        first=self.invoke(['workspace','list','--limit','1','--fields','label'])['data']
        second=self.invoke(['workspace','list','--limit','1','--offset','1','--fields','label'])['data']
        self.assertNotEqual(first['items'][0]['workspace_id'],second['items'][0]['workspace_id'])
        self.assertEqual(set(first['items'][0]),{'label','workspace_id'})
        self.assertTrue(first['pagination']['truncated'])
        self.invoke(['workspace','list','--fields','not_a_real_field'],2)

    def test_backend_timeout_flood_and_invalid_json(self):
        backend=a.Backend.__new__(a.Backend)
        backend.binary=Path(sys.executable)
        backend.timeout=.15
        with self.assertRaises(a.Failure) as cm: backend.raw(['-c','import time; time.sleep(2)'],mutation=True)
        self.assertEqual((cm.exception.code,cm.exception.outcome),('TIMEOUT','unknown'))
        backend.timeout=3
        with patch.object(a,'MAX_BYTES',1000):
            with self.assertRaises(a.Failure) as cm: backend.raw(['-c','print("x"*200000)'])
            self.assertEqual(cm.exception.code,'OUTPUT_LIMIT')
        with patch.object(backend,'raw',return_value='bad json'):
            with self.assertRaises(a.Failure) as cm: backend.call(['anything'])
            self.assertEqual(cm.exception.code,'BACKEND_PROTOCOL')

    def test_internal_fault_envelope(self):
        output=io.StringIO()
        with patch.object(a,'execute',side_effect=RuntimeError('private-secret')),patch('sys.stdout',output):
            code=a.main(['schema'])
        self.assertEqual(code,1)
        self.assertEqual(json.loads(output.getvalue())['error']['code'],'INTERNAL')
        self.assertNotIn('private-secret',output.getvalue())

    def test_error_registry_exit_mapping(self):
        for error,(expected,_,_) in a.ERRORS.items():
            output=io.StringIO()
            with patch.object(a,'execute',side_effect=a.Failure(error,'synthetic contract failure')),patch('sys.stdout',output):
                code=a.main(['schema'])
            self.assertEqual(code,expected)
            self.assertEqual(json.loads(output.getvalue())['error']['code'],error)

    def test_unknown_write_is_not_retryable(self):
        output=io.StringIO()
        with patch.object(a,'execute',side_effect=a.Failure('TIMEOUT','dispatched timeout','unknown')),patch('sys.stdout',output):
            code=a.main(['schema'])
        result=json.loads(output.getvalue())
        self.assertEqual(code,4)
        self.assertFalse(result['error']['retryable'])
        self.assertEqual(result['error']['outcome'],'unknown')

    def test_file_sources_and_plan_expiry(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/'input.json'
            file.write_text('{"target":"reviewer","lines":5}',encoding='utf-8-sig')
            self.invoke(['agent','read','--file',str(file)])
            self.invoke(['agent','read','--file',str(file),'--input','{}'],2)
            spec=a.OPS['workspace.create']
            inputs={'cwd':tmp,'label':'contract expiry'}
            backend=FixtureBackend(5)
            argv=a.argv_for('workspace.create',spec,inputs,5)
            with patch.object(a.time,'time',return_value=299): old=a.plan_for(backend,'workspace.create',spec,inputs,argv,{},5)
            with patch.object(a.time,'time',return_value=301): new=a.plan_for(backend,'workspace.create',spec,inputs,argv,{},5)
            self.assertEqual(old['valid_until_unix'],300)
            self.assertNotEqual(a.digest(old),a.digest(new))

    def test_focused_help(self):
        p=subprocess.run([sys.executable,str(SCRIPT),'workspace','create','--help'],capture_output=True)
        self.assertEqual(p.returncode,0)
        self.assertIn(b'cwd',p.stdout)
        self.assertIn(b'Effect: write',p.stdout)

    def test_invalid_requests_never_touch_backend(self):
        for argv in [['workspace','wrong'],['workspace','get','--input',''],['workspace','get','--input','{"id":"w2","id":"w3"}'],['pane','read','--input','{"target":"w2:p1","lines":NaN}'],['pane','get','--input','{"id":"w2:p1"}','--limit','1']]:
            with self.subTest(argv=argv),patch.object(a,'Backend') as backend,self.assertRaises(a.Failure):
                a.execute(a.parse(argv))
            backend.assert_not_called()

    def test_stdin_pipe_without_eof_times_out(self):
        proc=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--fixture','pane','read','--file','-','--timeout','1'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            proc.wait(timeout=4)
            result=json.loads(proc.stdout.read())
            self.assertEqual(proc.returncode,4)
            self.assertEqual(result['error']['outcome'],'not_started')
        finally:
            if proc.poll() is None: proc.kill(); proc.wait()
            proc.stdin.close(); proc.stdout.close(); proc.stderr.close()

    def test_descendant_stdout_drain_is_bounded(self):
        backend=a.Backend.__new__(a.Backend)
        backend.binary=Path(sys.executable)
        backend.timeout=.2
        program='import subprocess,sys; subprocess.Popen([sys.executable,"-c","import time; time.sleep(.7)"]); print("parent exited")'
        with self.assertRaises(a.Failure) as cm: backend.raw(['-c',program])
        self.assertEqual(cm.exception.code,'TIMEOUT')

    def test_backend_envelopes_reject_scalar_results(self):
        backend=a.Backend.__new__(a.Backend)
        for raw in ['[]','{"result":null}','{"result":[]}','{"result":"ok"}']:
            with self.subTest(raw=raw),patch.object(backend,'raw',return_value=raw),self.assertRaises(a.Failure) as cm:
                backend.call(['workspace','close','w2'],mutation=True)
            self.assertEqual((cm.exception.code,cm.exception.outcome),('BACKEND_PROTOCOL','unknown'))

    def test_close_cannot_confirm_from_missing_collection(self):
        for reply in [{},{'workspaces':None},{'workspaces':[{}]}]:
            backend=unittest.mock.Mock()
            backend.call.return_value=reply
            with self.subTest(reply=reply),self.assertRaises(a.Failure) as cm:
                a.verify(backend,'workspace.close',{'id':'w2'},{'type':'ok'})
            self.assertEqual((cm.exception.code,cm.exception.outcome),('BACKEND_PROTOCOL','unknown'))

    def test_create_split_and_rename_verify_actual_postconditions(self):
        backend=unittest.mock.Mock()
        backend.call.return_value={'workspace':{'workspace_id':'w2','label':'wrong'}}
        with self.assertRaises(a.Failure):
            a.verify(backend,'workspace.create',{'label':'desired'},{'workspace':{'workspace_id':'w2'}})
        backend.call.return_value={'pane':{'pane_id':'w2:p9'}}
        with self.assertRaises(a.Failure): a.verify(backend,'pane.split',{}, {'pane':{'pane_id':'w2:p1'}})
        backend.call.return_value={'workspace':{'workspace_id':'w2','label':'desired'}}
        result=a.verify(backend,'workspace.rename',{'id':'w2','label':'desired'},{})
        self.assertTrue(result['confirmed'])

    def test_prompt_requires_resolved_agent_in_response(self):
        with self.assertRaises(a.Failure) as cm:
            a.verify(None,'agent.prompt',{'target':'reviewer'},{})
        self.assertEqual(cm.exception.outcome,'unknown')

    def test_live_caller_alias_and_close_topology(self):
        with patch.dict(os.environ,{'HERDR_WORKSPACE_ID':'w0','HERDR_TAB_ID':'w0:t1','HERDR_PANE_ID':'w0:p1'}):
            with self.assertRaises(a.Failure): a.preflight(FixtureBackend(5),'workspace.close',{'id':'w1'})
            result=a.preflight(FixtureBackend(5),'workspace.close',{'id':'w2'})
        self.assertEqual(result['close_topology'],[('w2:p1','t2')])

    def test_preview_requires_running_backend_and_exposes_changes(self):
        with patch.dict(os.environ,{'HERDR_ENV':'1'}),patch.object(a,'Backend',return_value=FixtureBackend(5)):
            result,_=a.execute(a.parse(['workspace','create','--input',json.dumps({'cwd':str(SCRIPT.parent),'label':'reviewable'})]))
        self.assertEqual(result['plan']['changes']['label'],'reviewable')
        backend=unittest.mock.Mock()
        backend.call.side_effect=a.Failure('BACKEND_UNAVAILABLE','fixture offline')
        with patch.dict(os.environ,{'HERDR_ENV':'1'}),patch.object(a,'Backend',return_value=backend),self.assertRaises(a.Failure):
            a.execute(a.parse(['workspace','create','--input',json.dumps({'cwd':str(SCRIPT.parent),'label':'reviewable'})]))

    def test_secret_key_variants_are_redacted(self):
        for key in ['access_token','refresh-token','private_key','api-key','client_secret']:
            self.assertEqual(a.clean({key:'canary'})[key],'[REDACTED]')

    def test_legacy_doctor_redacts_json_before_truncation(self):
        sys.path.insert(0,str(SCRIPT.parent))
        try:
            doctor_spec=importlib.util.spec_from_file_location('legacy_doctor',SCRIPT.parent/'doctor.py')
            doctor=importlib.util.module_from_spec(doctor_spec)
            doctor_spec.loader.exec_module(doctor)
            payload=json.dumps({'agent_session':{'value':'private-native-id-canary'},'api_key':'private-key-canary'})
            with patch.object(doctor.Backend,'raw',return_value=payload):
                result=doctor.run(sys.executable,[],1,10000)
            self.assertNotIn('private-native-id-canary',result['stdout'])
            self.assertNotIn('private-key-canary',result['stdout'])
            with patch.object(doctor.Backend,'raw',return_value='api_key=private-key-canary'):
                result=doctor.run(sys.executable,[],1,12)
            self.assertNotIn('private',result['stdout'])
        finally: sys.path.pop(0)


if __name__=='__main__':
    if sys.argv[1:2]==['--fixture']:
        a.Backend=FixtureBackend
        os.environ.update(HERDR_ENV='1',HERDR_WORKSPACE_ID='w1',HERDR_TAB_ID='w1:t1',HERDR_PANE_ID='w1:p1')
        raise SystemExit(a.main(sys.argv[2:]))
    unittest.main(verbosity=2)
