#!/usr/bin/env python3
"""Bounded, schema-discovered Herdr TUI JSON socket client (standard library).

The worker isolates blocking Windows pipe I/O so the parent can enforce a deadline.
It is an implementation detail, not an authorization or operating-system sandbox.
"""
import argparse
from contextlib import ExitStack
import hashlib
import json
import math
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import uuid

sys.dont_write_bytecode = True
from herdr_agent import Failure, clean

ROOT = Path(__file__).resolve().parents[1]
MAX_INPUT = 65536
MAX_FRAME = 1024 * 1024
MAX_OUTPUT = 4 * MAX_FRAME
READ_METHODS = frozenset('''ping session.snapshot server.agent_manifests
workspace.list workspace.get tab.list tab.get pane.list pane.get pane.current
pane.layout pane.process_info pane.neighbor pane.edges pane.read pane.selection.read
pane.link.resolve pane.wait_for_output agent.list agent.get agent.read agent.explain
agent.wait integration.list plugin.list plugin.action.list plugin.log.list
layout.export events.wait events.subscribe'''.split())


def load_schema():
    return json.loads((ROOT / 'sources' / 'herdr-api.schema.json').read_text(encoding='utf-8'))


def methods(schema):
    return {row['properties']['method']['const']: row
            for row in schema['schemas']['request']['oneOf']}


def reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON field: ' + key)
        result[key] = value
    return result


def decode(text):
    return json.loads(text, object_pairs_hook=reject_duplicates,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Non-finite JSON number')))


def read_input(path, timeout):
    if path is None:
        return {}
    if path == '-':
        if sys.stdin.isatty():
            raise ValueError('Use a file or a finite stdin pipe')
        # A daemon reader also bounds an unclosed stdin pipe on Windows.
        import queue
        import threading
        result = queue.Queue(maxsize=1)
        def read_pipe():
            try:
                result.put(sys.stdin.buffer.read(MAX_INPUT + 1))
            except Exception as error:
                result.put(error)
        threading.Thread(target=read_pipe, daemon=True).start()
        try:
            content = result.get(timeout=timeout)
        except queue.Empty:
            raise Failure('TIMEOUT', 'Input pipe did not close before the deadline')
        if isinstance(content, Exception):
            raise content
    else:
        with Path(path).open('rb') as stream:
            content = stream.read(MAX_INPUT + 1)
    if len(content) > MAX_INPUT:
        raise ValueError('Input exceeds 64 KiB')
    return decode(content.decode('utf-8-sig'))


def managed_endpoint():
    if os.environ.get('HC_TERMINAL_ID'):
        raise Failure('OUTSIDE_HERDR', 'This is a Core terminal; use hc, not inherited TUI markers')
    if os.environ.get('HERDR_ENV') != '1':
        raise Failure('OUTSIDE_HERDR', 'TUI runtime control requires a real Herdr-managed pane')
    endpoint = os.environ.get('HERDR_SOCKET_PATH')
    if not endpoint:
        raise Failure('BACKEND_UNAVAILABLE', 'The managed TUI endpoint is missing; do not guess another session')
    return endpoint


def plan_hash(endpoint, requests, timeout, max_events):
    schema_bytes = (ROOT / 'sources' / 'herdr-api.schema.json').read_bytes()
    value = {'endpoint': endpoint, 'requests': requests, 'timeout': timeout,
             'max_events': max_events, 'window': int(time.time() // 300),
             'schema': hashlib.sha256(schema_bytes).hexdigest(),
             'client': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'context': {key: os.environ.get(key) for key in
                         ['HERDR_WORKSPACE_ID', 'HERDR_TAB_ID', 'HERDR_PANE_ID', 'HERDR_SESSION']}}
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                    separators=(',', ':')).encode()).hexdigest()


def check_requests(requests, schema):
    catalog = methods(schema)
    if not isinstance(requests, list) or not 1 <= len(requests) <= 32:
        raise ValueError('A batch requires 1..32 request objects')
    for request in requests:
        if not isinstance(request, dict) or set(request) != {'method', 'params'}:
            raise ValueError('Each request must contain exactly method and params')
        if not isinstance(request['method'], str) or request['method'] not in catalog:
            raise ValueError('Method is absent from the bundled TUI schema')
        if not isinstance(request['params'], dict):
            raise ValueError('params must be an object; use schema --method for its fields')
    return any(request['method'] not in READ_METHODS for request in requests)


def wire_name(endpoint, windows=None):
    windows = os.name == 'nt' if windows is None else windows
    # Herdr v0.9.5 src/ipc.rs uses GenericNamespaced; interprocess prepends this
    # prefix verbatim. The .sock marker is never opened as a transport file.
    return '\\\\.\\pipe\\' + endpoint if windows else endpoint


def connect(endpoint):
    if os.name == 'nt':
        return open(wire_name(endpoint), 'r+b', buffering=0)
    stream = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        stream.connect(endpoint)
        return stream.makefile('rwb', buffering=0)
    finally:
        stream.close()


class Frames:
    def __init__(self, stream, budget=None):
        self.stream = stream
        self.pending = bytearray()
        self.budget = budget if budget is not None else [0]
        self.events = 0

    def read(self):
        while b'\n' not in self.pending:
            part = self.stream.read(min(4096, MAX_FRAME + 1 - len(self.pending)))
            if not part:
                raise Failure('BACKEND_PROTOCOL', 'Connection ended before a complete response')
            self.pending.extend(part)
            if len(self.pending) > MAX_FRAME:
                raise Failure('OUTPUT_LIMIT', 'A wire frame exceeded 1 MiB')
        line, _, remainder = self.pending.partition(b'\n')
        self.pending = bytearray(remainder)
        value = decode(line.decode('utf-8'))
        if not isinstance(value, dict):
            raise Failure('BACKEND_PROTOCOL', 'Wire frames must be JSON objects')
        return value

    def emit(self, kind, value):
        text = json.dumps({'kind': kind, 'value': value}, ensure_ascii=True, separators=(',', ':')) + '\n'
        self.budget[0] += len(text)
        if self.budget[0] > MAX_OUTPUT:
            raise Failure('OUTPUT_LIMIT', 'Total wire output exceeded 4 MiB')
        sys.stdout.write(text)
        sys.stdout.flush()

    def response(self, request_id):
        while True:
            value = self.read()
            if 'id' in value:
                if value['id'] != request_id or (('result' in value) == ('error' in value)):
                    raise Failure('BACKEND_PROTOCOL', 'Response ID or response envelope did not match')
                return value
            if 'event' not in value or 'data' not in value:
                raise Failure('BACKEND_PROTOCOL', 'Unexpected frame while awaiting a response')
            self.events += 1
            if self.events > 100:
                raise Failure('OUTPUT_LIMIT', 'Too many interleaved events')
            self.emit('event', value)

    def send(self, request):
        remaining = memoryview((json.dumps(request, ensure_ascii=True) + '\n').encode())
        while remaining:
            written = self.stream.write(remaining)
            if not written:
                raise Failure('BACKEND_PROTOCOL', 'Request write did not complete')
            remaining = remaining[written:]
        self.stream.flush()


def worker(payload):
    try:
        budget = [0]
        with connect(payload['endpoint']) as stream:
            probe = Frames(stream, budget)
            ping_id = 'skill-ping-' + uuid.uuid4().hex
            probe.send({'id': ping_id, 'method': 'ping', 'params': {}})
            result = probe.response(ping_id).get('result', {})
            if result.get('type') != 'pong' or result.get('protocol') != payload['protocol']:
                raise Failure('INCOMPATIBLE_VERSION', 'Running TUI protocol differs from bundled schema')
            probe.emit('connected', {'protocol': result['protocol']})
        # TUI serves one request per connection. SSH agent leases retain their
        # own connections while later batch requests use independent ones.
        with ExitStack() as leases:
            lease_stream = None
            subscribed = False
            for request in payload['requests']:
                with ExitStack() as current:
                    stream = current.enter_context(connect(payload['endpoint']))
                    frames = Frames(stream, budget)
                    request_id = 'skill-api-' + uuid.uuid4().hex
                    frames.emit('dispatched', {'method': request['method']})
                    frames.send({'id': request_id, **request})
                    response = frames.response(request_id)
                    frames.emit('response', response)
                    if 'error' in response:
                        return 1
                    if request['method'] == 'server.ssh_agent.register':
                        leases.enter_context(current.pop_all())
                        lease_stream = stream
                    if request['method'] == 'events.subscribe':
                        subscribed = True
                        while frames.events < payload['max_events']:
                            value = frames.read()
                            if 'event' not in value or 'data' not in value or 'id' in value:
                                raise Failure('BACKEND_PROTOCOL', 'Expected a subscription event')
                            frames.events += 1
                            frames.emit('event', value)
            if lease_stream is not None and not subscribed:
                # Retain the lease until the parent deadline; a closed lease
                # cannot silently masquerade as an active registration.
                if not lease_stream.read(1):
                    raise Failure('BACKEND_PROTOCOL', 'SSH agent lease connection ended')
                raise Failure('BACKEND_PROTOCOL', 'Unexpected data on SSH agent lease')
            probe.emit('complete', {'reason': 'event_limit' if payload['max_events'] else 'responses'})
        return 0
    except Failure as error:
        print(json.dumps({'kind': 'failure', 'value': {'code': error.code, 'message': error.message}}), flush=True)
    except (OSError, ValueError, UnicodeError):
        print(json.dumps({'kind': 'failure', 'value': {'code': 'BACKEND_UNAVAILABLE',
                                                     'message': 'Transport failed; inspect the managed endpoint'}}), flush=True)
    return 1


def exchange(endpoint, requests, timeout, max_events, protocol):
    payload = {'endpoint': endpoint, 'requests': requests, 'max_events': max_events, 'protocol': protocol}
    process = subprocess.Popen([sys.executable, '-B', str(Path(__file__).resolve()), '--worker'],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               shell=False)
    timed_out = False
    try:
        out, err = process.communicate(json.dumps(payload).encode(), timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        out, err = process.communicate()
    except BaseException:
        process.kill()
        process.communicate()
        raise
    if len(out) > MAX_OUTPUT + 8192 or err:
        raise Failure('OUTPUT_LIMIT' if len(out) > MAX_OUTPUT + 8192 else 'BACKEND_PROTOCOL',
                      'Worker output was oversized or invalid', outcome='unknown')
    records = []
    for line in out.splitlines():
        try:
            records.append(decode(line))
        except (ValueError, UnicodeError):
            if not timed_out:
                raise Failure('BACKEND_PROTOCOL', 'Invalid worker output', outcome='unknown')
    dispatched = [row['value']['method'] for row in records if row['kind'] == 'dispatched']
    mutated = any(method not in READ_METHODS for method in dispatched)
    responses = [row['value'] for row in records if row['kind'] == 'response']
    events = [row['value'] for row in records if row['kind'] == 'event']
    outcome = 'unknown' if mutated else 'not_started'
    details = {'responses': responses, 'events': events, 'dispatched': dispatched,
               'connection_closed': True, 'automatic_retry': False}
    for response in responses:
        if 'error' in response:
            raise Failure('BACKEND_ERROR', 'The server rejected a request; inspect backend_error',
                          outcome=outcome, details={**details, 'backend_error': response['error']})
    failures = [row['value'] for row in records if row['kind'] == 'failure']
    if failures:
        raise Failure(failures[0]['code'], failures[0]['message'], outcome=outcome, details=details)
    if len(responses) != len(requests):
        raise Failure('TIMEOUT' if timed_out else 'BACKEND_PROTOCOL',
                      'Not all requests returned; reconcile dispatched mutations before retrying',
                      outcome=outcome, details=details)
    if not timed_out and process.returncode:
        raise Failure('BACKEND_PROTOCOL', 'Worker stopped unexpectedly', outcome=outcome, details=details)
    return {**details, 'outcome': 'committed' if mutated else 'not_started',
            'reason': 'deadline' if timed_out else ('event_limit' if max_events else 'responses')}


def parse(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['schema', 'call', 'subscribe', 'batch'])
    parser.add_argument('method', nargs='?')
    parser.add_argument('--method', dest='schema_method')
    parser.add_argument('--file', help='UTF-8 params object, or batch request array; - reads finite stdin')
    parser.add_argument('--timeout', type=float, default=15, help='Transport deadline in seconds, 1..60')
    parser.add_argument('--max-events', type=int, default=None, help='Maximum events collected, 0..100')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--dry-run', action='store_true')
    group.add_argument('--commit', action='store_true')
    parser.add_argument('--confirm', help='Plan hash from the same request and context')
    return parser.parse_args(argv)


def main(argv=None):
    try:
        args = parse(argv)
        if not math.isfinite(args.timeout) or not 1 <= args.timeout <= 60:
            raise ValueError('timeout must be finite and in 1..60 seconds')
        schema = load_schema()
        catalog = methods(schema)
        if args.action == 'schema':
            if args.method or args.file or args.commit or args.dry_run or args.confirm or args.max_events is not None:
                raise ValueError('schema accepts only --method and --timeout')
            if args.schema_method:
                if args.schema_method not in catalog:
                    raise ValueError('Unknown method')
                data = {'protocol': schema['protocol'], 'request': catalog[args.schema_method],
                        'schemas': {'request': {'$defs': schema['schemas']['request']['$defs']}}}
            else:
                data = {'protocol': schema['protocol'], 'method_count': len(catalog),
                        'methods': [{'method': name, 'effect': 'read' if name in READ_METHODS else 'write',
                                     'params': row['properties']['params']} for name, row in sorted(catalog.items())]}
        else:
            if args.schema_method or (args.confirm and not args.commit):
                raise ValueError('--method is schema-only; --confirm requires --commit')
            content = read_input(args.file, args.timeout)
            if args.action == 'batch':
                if args.method or args.file is None:
                    raise ValueError('batch requires --file with a request array')
                requests = content
            else:
                method = 'events.subscribe' if args.action == 'subscribe' else args.method
                if args.action == 'subscribe' and args.method:
                    raise ValueError('subscribe does not take a positional method')
                requests = [{'method': method, 'params': content}]
            mutation = check_requests(requests, schema)
            if any(row['method'] == 'events.subscribe' for row in requests[:-1]):
                raise ValueError('events.subscribe must be the final request in a batch')
            max_events = args.max_events if args.max_events is not None else (20 if args.action == 'subscribe' else 0)
            if not 0 <= max_events <= 100:
                raise ValueError('max-events must be in 0..100')
            if max_events and not any(row['method'] == 'events.subscribe' for row in requests):
                raise ValueError('Event collection requires events.subscribe as the last batch request')
            endpoint = managed_endpoint()
            expected = plan_hash(endpoint, requests, args.timeout, max_events)
            if args.dry_run or (mutation and not args.commit):
                data = {'dry_run': True, 'plan_hash': expected, 'requests': requests,
                        'endpoint': endpoint, 'effect': 'write' if mutation else 'read',
                        'expires_at': (int(time.time() // 300) + 1) * 300,
                        'validation': 'Local method and object shape only; server validates params at execution',
                        'target_resolution': 'Inherited managed endpoint; no live target lookup or transaction'}
            else:
                if mutation and args.confirm != expected:
                    raise Failure('PLAN_MISMATCH', 'Request, endpoint, context or plan window changed; preview again')
                data = exchange(endpoint, requests, args.timeout, max_events, schema['protocol'])
        print(json.dumps(clean({'schema_version': '1.0', 'ok': True, 'data': data}), ensure_ascii=True))
        return 0
    except (Failure, ValueError, OSError, UnicodeError) as error:
        failure = error if isinstance(error, Failure) else Failure('INVALID_INPUT', str(error))
        print(json.dumps(clean({'schema_version': '1.0', 'ok': False,
                                'error': {'code': failure.code, 'message': failure.message,
                                          'outcome': failure.outcome, 'retryable': False,
                                          'details': failure.details}}), ensure_ascii=True))
        return 2 if failure.code == 'INVALID_INPUT' else 1
    except KeyboardInterrupt:
        print(json.dumps({'schema_version': '1.0', 'ok': False,
                          'error': {'code': 'INTERRUPTED', 'outcome': 'unknown', 'retryable': False}}))
        return 130


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--worker':
        raise SystemExit(worker(decode(sys.stdin.buffer.read(MAX_INPUT * 6 + 16384))))
    raise SystemExit(main())
