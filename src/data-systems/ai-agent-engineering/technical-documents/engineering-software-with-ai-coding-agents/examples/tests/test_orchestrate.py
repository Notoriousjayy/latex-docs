import json
from pathlib import Path
import shutil
import tempfile
import unittest
from orchestrate import ROOT, execute, allowed_diff, command

class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        shutil.copyfile(ROOT/'pricing.py', self.root/'pricing.py')
        self.task = json.loads((ROOT/'task.json').read_text())
    def tearDown(self):
        self.temp.cleanup()
    def run_task(self, invoke=None):
        return execute('mock',self.root,self.task,ROOT/'trusted/test_pricing.py',invoke)
    def test_success_is_not_approval(self):
        self.assertEqual(self.run_task()['status'],'awaiting_human_review')
    def test_scope_denied(self):
        def change(root):
            (root/'forbidden.txt').write_text('x')
            return 0
        self.assertEqual(self.run_task(change)['status'],'scope_denied')
    def test_failed_verification_bounded(self):
        def change(root):
            (root/'pricing.py').write_text('def discount(cents, percent): return 0\n')
            return 0
        result = self.run_task(change)
        self.assertEqual(result['status'],'verification_failed')
        self.assertEqual(len(result['events']),2)
    def test_execution_failed(self):
        self.assertEqual(self.run_task(lambda _: 1)['status'],'execution_failed')
    def test_symlink_rejected(self):
        self.assertFalse(allowed_diff({}, {'pricing.py':'SYMLINK'}, ['pricing.py'])[1])
    def test_command_no_shell(self):
        self.assertEqual(command('claude','a; b')[-1],'a; b')
