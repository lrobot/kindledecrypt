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
import os
import shutil
import tempfile
import time
import topaz

def _process(infile, outfile, pid, error):
    try:
        if outfile.endswith(".mobi"):
            # Mobi file
            data_file = open(infile, "rb").read()
            strippedFile = mobidedrm.DrmStripper(data_file, pid)
            file(outfile, 'wb').write(strippedFile.getResult())
        else:
            # Topaz file
            tmp = tempfile.mkdtemp()
            args = ['./cmbtc.py', '-v', '-p', pid[:8], '-d', '-o', tmp, infile]
            topaz.cmbtc.main(argv=args)
            topaz.gensvg.main(['./gensvg.py', tmp])
            topaz.genhtml.main(['./genhtml.py', tmp])
            
            if not os.path.exists(outfile):
                os.mkdir(outfile)
                
            for filename in ["img", "style.css", "book.html"]:
                shutil.move(os.path.join(tmp, filename), os.path.join(outfile, filename))
            
            shutil.rmtree(tmp)
    except Exception, e:
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

