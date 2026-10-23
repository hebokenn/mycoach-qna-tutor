from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('installer',ROOT/'tools/install.py')
installer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

class InstallTests(unittest.TestCase):
    def test_full_install_is_independent(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=installer.install(Path(tmp)/'skills')
            target=Path(result['installed'])
            self.assertTrue((target/'SKILL.md').is_file())
            self.assertTrue((target/'assets/private-qna-standard.xlsx').is_file())
            topics=json.loads(subprocess.check_output([sys.executable,str(target/'scripts/tutor.py'),'topics'],cwd=tmp))
            self.assertEqual(len(topics),20)
    def test_default_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent=Path(tmp);target=parent/'mycoach-qna-tutor';target.mkdir();(target/'user-file').write_text('preserve me')
            with self.assertRaises(ValueError):installer.install(parent)
            self.assertEqual((target/'user-file').read_text(),'preserve me')
    def test_explicit_backup_preserves_previous_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent=Path(tmp);target=parent/'mycoach-qna-tutor';target.mkdir();(target/'user-file').write_text('preserve me')
            result=installer.install(parent,backup=True)
            self.assertEqual((Path(result['backup'])/'user-file').read_text(),'preserve me')
            self.assertTrue((target/'SKILL.md').exists())

if __name__=='__main__':unittest.main()
