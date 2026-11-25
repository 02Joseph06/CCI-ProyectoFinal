"""Prueba local de la selección de CSV de Drive sin credenciales ni red."""
import ast
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


NOTEBOOK = Path(__file__).resolve().parents[1] / 'notebooks/Proyecto_Final_Colab_Sin_Src.ipynb'


def cargar_selector():
    nb = json.loads(NOTEBOOK.read_text(encoding='utf-8'))
    source = next(''.join(c['source']) for c in nb['cells']
                  if 'ID_CARPETA_DRIVE =' in ''.join(c['source']))
    tree = ast.parse(source)
    selector = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                    and node.name == 'localizar_csv_drive')
    env = {'archivos_esperados': ('monitoreo.csv', 'solicitudes.csv', 'solicitudes_validacion.csv')}
    exec(compile(ast.Module(body=[selector], type_ignores=[]), '<notebook>', 'exec'), env)
    return env['localizar_csv_drive']


class Response:
    def __init__(self, value):
        self.value = value

    def execute(self):
        return self.value


class FakeFiles:
    def __init__(self, pages):
        self.pages = pages

    def get(self, **kwargs):
        return Response({'id': 'root', 'name': 'content',
                         'mimeType': 'application/vnd.google-apps.folder'})

    def list(self, **kwargs):
        folder = kwargs['q'].split("'")[1]
        return Response(self.pages[(folder, kwargs['pageToken'])])


class FakeDrive:
    def __init__(self, pages):
        self.api = FakeFiles(pages)

    def files(self):
        return self.api


class SelectorDriveTest(unittest.TestCase):
    def test_subcarpeta_y_paginacion(self):
        folder = 'application/vnd.google-apps.folder'
        pages = {
            ('root', None): {'files': [{'id': 'data', 'name': 'data', 'mimeType': folder}]},
            ('data', None): {'files': [{'id': 'a', 'name': 'monitoreo.csv', 'mimeType': 'text/csv'}],
                             'nextPageToken': '2'},
            ('data', '2'): {'files': [{'id': 'b', 'name': 'solicitudes.csv'},
                                      {'id': 'c', 'name': 'solicitudes_validacion.csv'}]},
        }
        result = cargar_selector()(FakeDrive(pages), 'root')
        self.assertEqual(result['solicitudes.csv'][0], 'b')
        self.assertEqual(result['monitoreo.csv'][1], 'content/data/monitoreo.csv')

    def test_duplicados_y_faltantes_no_se_eligen_silenciosamente(self):
        pages = {('root', None): {'files': [{'id': 'a', 'name': 'monitoreo.csv'},
                                           {'id': 'b', 'name': 'monitoreo.csv'}]}}
        with self.assertRaisesRegex(ValueError, 'duplicados') as ctx:
            cargar_selector()(FakeDrive(pages), 'root')
        self.assertIn('solicitudes.csv', str(ctx.exception))

    def test_celda_autentica_y_descarga_csv_en_temporal(self):
        nb = json.loads(NOTEBOOK.read_text(encoding='utf-8'))
        source = next(''.join(c['source']) for c in nb['cells']
                      if 'ID_CARPETA_DRIVE =' in ''.join(c['source']))
        files = [{'id': str(i), 'name': name, 'mimeType': 'text/csv'} for i, name in enumerate(
            ('monitoreo.csv', 'solicitudes.csv', 'solicitudes_validacion.csv'))]
        drive = FakeDrive({('1LRNh9PUDtYVXWpt8E1AyL-a59v9Yx-vB', None): {'files': files}})
        drive.api.get_media = lambda **kwargs: Response(('csv-' + kwargs['fileId']).encode())
        google = types.ModuleType('google')
        colab = types.ModuleType('google.colab')
        called = []
        colab.auth = types.SimpleNamespace(authenticate_user=lambda: called.append(True))
        google.colab = colab
        client = types.ModuleType('googleapiclient')
        discovery = types.ModuleType('googleapiclient.discovery')
        discovery.build = lambda *args, **kwargs: drive
        modules = {'google': google, 'google.colab': colab,
                   'googleapiclient': client, 'googleapiclient.discovery': discovery}
        env = {}
        old_path = sys.path[:]
        try:
            with patch.dict(sys.modules, modules), patch('IPython.core.magic.register_cell_magic', lambda f: f):
                exec(compile(source, '<notebook>', 'exec'), env)
            self.assertTrue(called)
            self.assertEqual((env['DATA_RAW'] / 'solicitudes.csv').read_bytes(), b'csv-1')
        finally:
            sys.path[:] = old_path
            if 'ENTORNO_TEMPORAL' in env:
                env['ENTORNO_TEMPORAL'].cleanup()


if __name__ == '__main__':
    unittest.main()
