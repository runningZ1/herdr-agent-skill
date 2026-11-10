"""Consumer-visible socket framing, boundedness and mutation safety regressions."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import herdr_api as api
import herdr_agent as adapter


class Duplex:
    """A byte stream that can split reads and short-write requests."""
    def __init__(self, data=b'', read_size=7, write_size=3):
        self.input = io.BytesIO(data)
        self.output = bytearray()
        self.read_size = read_size
        self.write_size = write_size

    def read(self, size):
        return self.input.read(min(size, self.read_size))

    def write(self, data):
        size = min(len(data), self.write_size)
        self.output.extend(data[:size])
        return size

    def flush(self):
        pass


def wire(*values):
    return b''.join((json.dumps(value) + '\n').encode() for value in values)


class SocketTests(unittest.TestCase):
    def test_fragmented_event_does_not_satisfy_request_response(self):
        event = {'event': 'pane.agent_status_changed', 'data': {'pane_id': 'wA:p1', 'agent_status': 'done'}}
        response = {'id': 'request', 'result': {'type': 'pong'}}
        frames = api.Frames(Duplex(wire(event, response), read_size=1))
        with contextlib.redirect_stdout(io.StringIO()) as captured:
            self.assertEqual(frames.response('request'), response)
        emitted = json.loads(captured.getvalue())
        self.assertEqual(emitted, {'kind': 'event', 'value': event})
        self.assertEqual(frames.events, 1)

    def test_foreign_id_and_ambiguous_response_are_rejected(self):
        for frame in [{'id': 'other', 'result': {}}, {'id': 'wanted', 'result': {}, 'error': {}}]:
            with self.subTest(frame=frame), self.assertRaises(api.Failure) as raised:
                api.Frames(Duplex(wire(frame))).response('wanted')
            self.assertEqual(raised.exception.code, 'BACKEND_PROTOCOL')

    def test_partial_or_oversized_frame_never_becomes_result(self):
        with self.assertRaises(api.Failure):
            api.Frames(Duplex(b'{"id":"x"}')).read()
        with patch.object(api, 'MAX_FRAME', 32), self.assertRaises(api.Failure) as raised:
            api.Frames(Duplex(b'x' * 33, read_size=33)).read()
        self.assertEqual(raised.exception.code, 'OUTPUT_LIMIT')

    def test_short_writes_preserve_complete_unicode_request(self):
        stream = Duplex()
        request = {'id': 'x', 'method': 'tab.rename', 'params': {'label': '审计'}}
        api.Frames(stream).send(request)
        self.assertEqual(json.loads(stream.output), request)
        self.assertTrue(stream.output.endswith(b'\n'))

    def test_duplicate_fields_and_nonfinite_values_are_rejected(self):
        for content in ['{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}']:
            with self.subTest(content=content), self.assertRaises(ValueError):
                api.decode(content)

    def test_core_context_cannot_use_inherited_tui_markers(self):
        with patch.dict(os.environ, {'HERDR_ENV': '1', 'HERDR_SOCKET_PATH': 'audit', 'HC_TERMINAL_ID': 't7'}):
            for function in [api.managed_endpoint, adapter.require_tui]:
                with self.subTest(function=function.__name__), self.assertRaises(api.Failure) as raised:
                    function()
                self.assertEqual(raised.exception.code, 'OUTSIDE_HERDR')

    def test_write_preview_never_dispatches_and_changed_input_refuses_commit(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            params = Path(directory) / 'params.json'
            params.write_text('{"tab_id":"wA:t1","label":"first"}', encoding='utf-8')
            with patch.object(api, 'managed_endpoint', return_value='audit'), patch.object(api, 'exchange') as exchange:
                with contextlib.redirect_stdout(io.StringIO()) as captured:
                    self.assertEqual(api.main(['call', 'tab.rename', '--file', str(params)]), 0)
                plan = json.loads(captured.getvalue())['data']
                self.assertTrue(plan['dry_run'])
                exchange.assert_not_called()
                params.write_text('{"tab_id":"wA:t1","label":"changed"}', encoding='utf-8')
                with contextlib.redirect_stdout(io.StringIO()) as captured:
                    code = api.main(['call', 'tab.rename', '--file', str(params), '--commit', '--confirm', plan['plan_hash']])
                self.assertEqual(code, 1)
                self.assertEqual(json.loads(captured.getvalue())['error']['code'], 'PLAN_MISMATCH')
                exchange.assert_not_called()

    def test_plan_changes_with_endpoint_or_time_window(self):
        requests = [{'method': 'tab.rename', 'params': {'tab_id': 'wA:t1', 'label': 'topic'}}]
        with patch.object(api.time, 'time', return_value=299):
            old = api.plan_hash('first', requests, 15, 0)
            other = api.plan_hash('other', requests, 15, 0)
        with patch.object(api.time, 'time', return_value=301):
            newer = api.plan_hash('first', requests, 15, 0)
        self.assertNotEqual(old, other)
        self.assertNotEqual(old, newer)

    def test_deadline_after_dispatch_marks_write_unknown_and_not_retryable(self):
        output = wire({'kind': 'dispatched', 'value': {'method': 'tab.rename'}})
        process = unittest.mock.Mock()
        process.communicate.side_effect = [subprocess.TimeoutExpired('worker', 1), (output, b'')]
        with patch.object(api.subprocess, 'Popen', return_value=process):
            with self.assertRaises(api.Failure) as raised:
                api.exchange('audit', [{'method': 'tab.rename', 'params': {}}], 1, 0, 22)
        self.assertEqual(raised.exception.code, 'TIMEOUT')
        self.assertEqual(raised.exception.outcome, 'unknown')
        self.assertFalse(raised.exception.details['automatic_retry'])

    def test_subscription_deadline_returns_collected_events_after_ack(self):
        event = {'event': 'pane.created', 'data': {'pane_id': 'wA:p1'}}
        output = wire({'kind': 'dispatched', 'value': {'method': 'events.subscribe'}},
                      {'kind': 'response', 'value': {'id': 'sub', 'result': {'type': 'subscribed'}}},
                      {'kind': 'event', 'value': event})
        process = unittest.mock.Mock()
        process.communicate.side_effect = [subprocess.TimeoutExpired('worker', 1), (output, b'')]
        with patch.object(api.subprocess, 'Popen', return_value=process):
            result = api.exchange('audit', [{'method': 'events.subscribe', 'params': {}}], 1, 20, 22)
        self.assertEqual(result['reason'], 'deadline')
        self.assertEqual(result['events'], [event])
        self.assertTrue(result['connection_closed'])

    def test_one_request_server_supports_batch_without_reusing_closed_connections(self):
        class OneRequest(Duplex):
            def __init__(self):
                super().__init__(write_size=4096)
                self.accepted = False

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def write(self, data):
                if self.accepted:
                    raise BrokenPipeError('The server closes ordinary requests after one response')
                self.output.extend(data)
                if self.output.endswith(b'\n'):
                    self.accepted = True
                    request = json.loads(self.output)
                    result = {'type': 'pong', 'protocol': 22} if request['method'] == 'ping' else {'type': 'layout_export', 'root': {'type': 'pane'}}
                    self.input = io.BytesIO(wire({'id': request['id'], 'result': result}))
                return len(data)

        payload = {'endpoint': 'audit', 'protocol': 22, 'max_events': 0, 'requests': [
            {'method': 'ping', 'params': {}},
            {'method': 'layout.export', 'params': {'pane_id': 'wA:p1'}},
        ]}
        with patch.object(api, 'connect', side_effect=lambda _: OneRequest()), contextlib.redirect_stdout(io.StringIO()) as captured:
            status = api.worker(payload)
        records = [json.loads(line) for line in captured.getvalue().splitlines()]
        responses = [row['value']['result']['type'] for row in records if row['kind'] == 'response']
        self.assertEqual(responses, ['pong', 'layout_export'])
        self.assertEqual(status, 0)

    def test_backend_rejection_prevents_batch_success(self):
        output = wire({'kind': 'dispatched', 'value': {'method': 'tab.rename'}},
                      {'kind': 'response', 'value': {'id': 'x', 'error': {'code': 'not_found', 'message': 'missing'}}})
        process = unittest.mock.Mock(returncode=1)
        process.communicate.return_value = (output, b'')
        with patch.object(api.subprocess, 'Popen', return_value=process), self.assertRaises(api.Failure) as raised:
            api.exchange('audit', [{'method': 'tab.rename', 'params': {}}], 1, 0, 22)
        self.assertEqual(raised.exception.code, 'BACKEND_ERROR')
        self.assertEqual(raised.exception.details['backend_error']['code'], 'not_found')


if __name__ == '__main__':
    unittest.main()
