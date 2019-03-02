# hdf compress lib, details see https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#compression
HDF_FILE_COMPRESS_LIB = 'blosc'

# hdf compress level 0-9
HDF_FILE_COMPRESS_LEVEL = 9

# hdf trade to kline chunk size
HDF_TRADE_TO_KLINE_CHUNK_SIZE = 1000000

# TODO
# kline side
# left -> 11:20:00 means kline data are resampled by the trade data from 11:19:00 to 11:20:00
# right -> 11:20:00 mean kline data are resampled by the trade data from 11:20:00 to 11:21:00
KLINE_SIDE = 'right'
