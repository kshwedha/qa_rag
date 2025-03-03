import sys
from pathlib import Path
import numpy as np
from custom_logger import logger
from psycopg2.extensions import register_adapter, AsIs

# Add the project root directory to the Python path
sys.path.append(str(Path(__file__).parent))

def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)

def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)

def addapt_numpy_float32(numpy_float32):
    return AsIs(numpy_float32)

def addapt_numpy_int32(numpy_int32):
    return AsIs(numpy_int32)

def addapt_numpy_array(numpy_array):
    return AsIs(list(numpy_array))

logger.info("Registering adapters")
# register_adapter(np.float64, addapt_numpy_float64)
# register_adapter(np.int64, addapt_numpy_int64)
# register_adapter(np.float32, addapt_numpy_float32)
# register_adapter(np.int32, addapt_numpy_int32)
register_adapter(np.ndarray, addapt_numpy_array)