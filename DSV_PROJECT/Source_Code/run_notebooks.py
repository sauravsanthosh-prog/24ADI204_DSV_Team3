"""Execute notebooks sequentially using the Python interpreter running this script."""
from pathlib import Path
import sys
import tempfile
import json
import os
import nbformat
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager

def run():
    root = Path(__file__).resolve().parents[1]
    # Temporary kernel avoids modifying the user's permanent Jupyter configuration.
    with tempfile.TemporaryDirectory(prefix='attrition-kernel-') as tmp:
        spec = Path(tmp)/'kernels'/'attrition-local'
        spec.mkdir(parents=True)
        (spec/'kernel.json').write_text(json.dumps({
            'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
            'display_name':'Attrition local validation','language':'python'}),encoding='utf-8')
        old = os.environ.get('JUPYTER_PATH')
        os.environ['JUPYTER_PATH'] = tmp + (os.pathsep+old if old else '')
        try:
            for path in sorted((root/'Source_Code'/'Notebooks').glob('*.ipynb')):
                nb = nbformat.read(path,as_version=4)
                client = NotebookClient(nb,timeout=300,kernel_name='attrition-local',
                                        resources={'metadata':{'path':str(root)}},
                                        record_timing=False)
                client.execute()
                # Portable metadata for VS Code; never ship validation kernel paths.
                nb.metadata['kernelspec'] = {'name':'python3','display_name':'Python 3','language':'python'}
                nbformat.validate(nb)
                nbformat.write(nb,path)
                print(f'Executed: {path.name}',flush=True)
        finally:
            if old is None: os.environ.pop('JUPYTER_PATH',None)
            else: os.environ['JUPYTER_PATH'] = old

if __name__ == '__main__':
    run()
