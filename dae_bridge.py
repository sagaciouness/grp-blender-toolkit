"""Headless adapter for an independently installed Dagor Asset Explorer."""
import ctypes
import lzma
import math
import sys
import types
from pathlib import Path


def load_parser(source, cdk):
    source, cdk = Path(source).resolve(), Path(cdk).resolve()
    if not (source / 'parse/gameres.py').is_file():
        raise ValueError('--dae-source must point to Dagor-Asset-Explorer/src/dae')
    dll_path = cdk / 'daKernel-dev.dll'
    if not dll_path.is_file():
        raise ValueError('--cdk-bin must contain your installed daKernel-dev.dll')
    sys.path.insert(0, str(source))
    # Only the parser is used; QObject is a base class, not a running GUI.
    qt, core = types.ModuleType('PyQt5'), types.ModuleType('PyQt5.QtCore')
    core.QObject = type('QObject', (), {})
    sys.modules.update({'PyQt5': qt, 'PyQt5.QtCore': core})
    codec = types.ModuleType('pylzma')
    codec.decompress, codec.compress = lzma.decompress, lzma.compress
    sys.modules['pylzma'] = codec
    misc = types.ModuleType('util.misc')
    misc.ROOT_FOLDER = str(source)
    misc.getResPath = lambda name: str(source / 'res' / name)
    # Do not bind version-dependent DLL ordinal numbers in the upstream module.
    misc.loadDLL = lambda name: None
    misc.matrixMul = lambda a, b: [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]
    misc.vectorTransform = lambda m, v: [sum(m[i][j] * v[j] for j in range(3)) + m[i][3] for i in range(3)]
    misc.matrixToEuler = lambda m: (math.atan2(-m[1][2], math.hypot(m[1][0], m[1][1])), math.atan2(m[0][2], math.hypot(m[0][0], m[0][1])), math.atan2(m[1][0], m[1][1]))
    sys.modules['util.misc'] = misc
    import util.log as log
    log.log = lambda *args, **kwargs: None
    from parse.gameres import GameResourcePack
    from util.assetcacher import AssetCacher
    import util.decompression as decompression
    dll = ctypes.CDLL(str(dll_path))
    decoder = getattr(dll, '?oodle_decompress@@YA_KPEAX_KPEBX1@Z')
    decoder.argtypes = (ctypes.c_void_p, ctypes.c_int64, ctypes.c_void_p, ctypes.c_int64)
    decoder.restype = ctypes.c_int64
    decompression.oodle_decompress = decoder
    decompression._toolkit_dll = dll
    return GameResourcePack, AssetCacher
