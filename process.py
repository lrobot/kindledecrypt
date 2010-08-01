#!/usr/bin/python

"""
    Utilities for decrypting a book in a separate process. This gets its own
    module as the multiprocessing module duplicates the global namespace when
    spawning new processes. This separate module limits the amount of stuff
    that gets duplicated and prevents serialization errors on certain platforms
    with e.g. wxWidgets.
"""

import mobidedrm
import multiprocessing
import time

def _process(infile, outfile, pid, error):
    try:
        data_file = open(infile, "rb").read()
        strippedFile = mobidedrm.DrmStripper(data_file, pid)
        file(outfile, 'wb').write(strippedFile.getResult())
    except mobidedrm.DrmException, e:
        error.value = str(e)

def decrypt(infile, outfile, pid):
    """
        Decrypt a Kindle book in a different process. This periodically yields
        so that status information can be shown. Use like:
        
            >>> for error in decrypt(infile, outfile, pid):
            >>>     progress_update()
            >>> if error:
            >>>     print error
        
    """
    error = None
    
    errorobj = multiprocessing.Array("c", 512)
    proc = multiprocessing.Process(target=_process, args=(infile, outfile, pid, errorobj))
    proc.start()
    while proc.is_alive():
        yield ""
        time.sleep(0.1)
    proc.join()
    
    if errorobj.value:
        error = errorobj.value
    
    yield error

