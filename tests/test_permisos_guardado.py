"""Pruebas del guardado temporal sin importar ni ejecutar spaCy."""

import ast
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / 'notebooks/01_preprocesado_spacy.ipynb'


class OutputPermissionsTests(unittest.TestCase):
    def setUp(self):
        # mkdir normal para que la carpeta de salida herede la ACL del proyecto.
        self.root = ROOT / ('.permission-test-' + os.urandom(16).hex())
        self.root.mkdir()
        self.addCleanup(self.root.rmdir)
        notebook = json.loads(NOTEBOOK.read_text(encoding='utf-8'))
        nodes = ast.parse(''.join(notebook['cells'][22]['source']).split('\n', 1)[1])
        helper = next(node for node in nodes.body
                      if isinstance(node, ast.FunctionDef)
                      and node.name == 'temporary_output_directory')
        namespace = {'TemporaryDirectory': tempfile.TemporaryDirectory,
                     'OUT_DIR': self.root, 'os': os}
        exec(compile(ast.Module(body=[helper], type_ignores=[]), str(NOTEBOOK), 'exec'), namespace)
        self.directory = namespace['temporary_output_directory']

    def test_publication_preserves_bytes_and_cleans_staging(self):
        for prefix in ('.lemas-', '.resultados-'):
            with self.subTest(prefix=prefix):
                target = self.root / 'artifact.json'
                self.addCleanup(target.unlink, missing_ok=True)
                with self.directory(prefix) as name:
                    staged = Path(name) / target.name
                    staged.write_bytes(b'{"stats": {}}\n')
                    os.replace(staged, target)
                self.assertFalse(Path(name).exists())
                self.assertEqual(target.read_bytes(), b'{"stats": {}}\n')
                result = subprocess.run(['git', 'hash-object', '--', str(target)],
                                        capture_output=True, check=True)
                self.assertTrue(result.stdout.strip())

    @unittest.skipUnless(os.name == 'nt', 'ACL de Windows')
    def test_published_files_inherit_the_same_acl_as_normal_files(self):
        reference = self.root / 'reference.json'
        reference.write_bytes(b'{}\n')
        self.addCleanup(reference.unlink)
        for prefix in ('.lemas-', '.resultados-'):
            with self.subTest(prefix=prefix):
                target = self.root / 'published.json'
                self.addCleanup(target.unlink, missing_ok=True)
                with self.directory(prefix) as name:
                    staged = Path(name) / target.name
                    staged.write_bytes(reference.read_bytes())
                    os.replace(staged, target)
                # Rutas pasadas en el entorno para evitar interpretarlas como PowerShell.
                command = ('$a=Get-Acl -LiteralPath $env:PERMISSIONS_REFERENCE; '
                           '$b=Get-Acl -LiteralPath $env:PERMISSIONS_TARGET; '
                           'if ($b.AreAccessRulesProtected -or $a.Sddl -ne $b.Sddl) { exit 1 }')
                subprocess.run(['powershell', '-NoProfile', '-Command', command],
                               env={**os.environ, 'PERMISSIONS_REFERENCE': str(reference),
                                    'PERMISSIONS_TARGET': str(target)},
                               capture_output=True, check=True)

    @unittest.skipUnless(os.name == 'nt', 'ACL de Windows')
    def test_acl_failure_stops_before_publication_and_cleans_staging(self):
        target = self.root / 'previous.json'
        target.write_bytes(b'{"previous": true}\n')
        self.addCleanup(target.unlink)
        failure = subprocess.CalledProcessError(1, ['icacls'])
        with patch('subprocess.run', side_effect=failure):
            with self.assertRaises(subprocess.CalledProcessError):
                self.directory('.resultados-')
        self.assertEqual(target.read_bytes(), b'{"previous": true}\n')
        self.assertEqual(list(self.root.glob('.resultados-*')), [])


if __name__ == '__main__':
    unittest.main()
