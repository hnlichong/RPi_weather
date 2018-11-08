

def my_logger(name, level="DEBUG"):
    import logging
    
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # create formatter
    # formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    formatter = logging.Formatter(
        "%(levelname)s - %(filename)s line %(lineno)s - %(funcName)s:\n%(message)s")
    
    # add formatter to ch
    ch.setFormatter(formatter)
    
    # add ch to logger
    logger.addHandler(ch)
    
    # "application" code
    # logger.debug("my logger created ok!")

    return logger

def bytes_to_hex_str(bs):
    """convert bytes, bytearray to hex str"""
    return "b'%s'" % ''.join('\\x%.2X' % b for b in bs)
