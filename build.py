import pathlib
import py_compile
import sys
import zipfile

if sys.version_info[:2] != (3, 7):
    sys.exit('Build with Python 3.7 (py -3.7 build.py).')

root = pathlib.Path(__file__).resolve().parent
source = root / 'src'
distribution = root / 'dist'
distribution.mkdir(exist_ok=True)
target = distribution / 'CodeBleu-BeefyBoyos.ts4script'
compiled = root / 'obj' / 'pyc'
with zipfile.ZipFile(target, 'w', zipfile.ZIP_STORED) as archive:
    for module in sorted(source.rglob('*.py')):
        relative = module.relative_to(source).with_suffix('.pyc')
        destination = compiled / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        py_compile.compile(str(module), cfile=str(destination), dfile=relative.with_suffix('.py').as_posix(), doraise=True)
        archive.write(destination, relative.as_posix())
print(target)
