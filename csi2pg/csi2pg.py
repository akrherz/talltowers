#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
Convert file(s) of Campbell Scientific
TOB1 or TOB3 to TOA5 (comma-separated ASCII).
The reuslts are stored in sub directories by YYYY/MM/DD, where the root is the
location of the origional file.
The file names are also decoded into human readable format, which indicates
"site_dataTable_date-time.dat"
Then the resultant TOA5 file is parsed and COPYed into the database.

TOB1  is avaiable to both CR6 and CR3000.  for the "TableFile()" function,
it is type "0".
TOB3  is card-native binary, and only availble for dataloggers with CRD: drive.
for the "TableFile()" function, it is type "64".

This has command line options, which include
 * seecifying directory of file (default is "/home/csiftp"),
 * naming a specific file or files (default is search for pattern sent from
   CR6s),
 * choosing a different timestamp format (default is CSI emulated, i.e.
   minimal characters, disregard sig.figs.)
 * print troubleshooting info, which is especially useful for TOB3 minor
   frames.
 * database to COPY data to (default is talltowers)

The reason the ASCII file is parsed for COPY into database is for modularity.
It would be more efficeint to create the .sql file at the same time as the
ASCII file, but it is more convienent to code one program which parses CSI's
standard TOA5 output into .sql form.
=====================================================================================

*** TOB1 ***
TOB1 file has 5 line header:
 1) Environment ["file-type","station-name","model-name","serial-number",
                 "os-version","dld-name","dld-signature","table-name"]
 2) Field Names
 3) Field Units
 4) Field Processing
 5) Field Data Types  *(see definition of "data_type_dict")

This Binary fine type does NOT have frames; each record is written
  sequentially,
  without reference to frame footers or headers, just like TOA5 files, ...
  but in binary.  That is, unlike TOB3 formats, there are no footers or
  headers to parse.
The binary values are decoded by using the Field Data Types, which specify how
  many Bytes are are used by each measurment; and in sum how many Bytes are
  used per row.

Script Procedure:
 1) identify file to convert
 2) define dictionaries and functions
 3) read files header information
 4) calculations based on Field Data Types (row 5 of header)
     a) length of each record in Bytes
     b) format of each record's output string (taking into account significant
        figures available due to the Bytes allocated for it.)
     c) make modifications, if TIMESTAMP is present
 5) write modified header to output file
 6) decode each record, and write to output file

=====================================================================================

*** TOB3 ***
TOB3 file has 6 line header:
 1) Experiment Environment ["File Type", "Station Name", "Model Name",
                            "Serial Number", "OS Version", "DLD Name",
                            "DLD Signature", "File Creation Time"]
 2) Additional Decode Information ["Table Name",
                                   "Non-Timestamped Record Interval",
                                   "Data Frame Size", "Intended Table Size",
                                   "Validation Stamp", "Frame Time Resolution",
                                   "Ring Record Number", Card Removal Time",
                                   "Internal Table CRC"]
 3) Field Names
 4) Field Units
 5) Field Processing
 6) Field Data Types  *(see definition of "data_type_dict")

each Frame has header, data, & footer.
 Frame Header)  12 byte (8byte for TOB2)
 Frame Data)    "Data Frame Size" - ( frame header size + frame footer size )
 Frame Footer)  4 byte; this contains flags regarding how/if frame processing
   should proceed; an invalid frame can be as short as 2-Bytes.

notes: CSI encodes data with a mix of little and big endian, specific to each
 data type.

TOB3 Script Procedure:
 1) read file as binary
 2) read header information
 3) define dictionaries and functions
 4) calculations based on header information
 5) loop tHough MAJOR Frames, from beginning to end of file.
     0) get MAJOR footer information
     1) if validation fails: go to next Major frame.
     2) if "E" (empty) flag == 1 or "M" (minor frame) flag == 1:
         # not sure if both of these must happen at end of Dirty frame.
         # "E" doesn't mean an empty Major frame, it only means an empty minor
         # frame at the end of that Major frame.
         a) get size of minor frame
         b) if "E" == 1:
              Move to previous minor frame, within the Major frame
            else:
              1) process header
              2) process data ("decode_data_bin()")
              3) move to previous minor frame
         c) process next minor frame's footer
              *) do not process Validation for subsequnent minor frames within
                 current MAJOR frame.
         d) after processing all minor frames within Major frame,
              reverse order of records for each minor frame (but Not within
              each minor frame!)
         e) write data to output file
     3) process header, for timestamp & record number
     4) process data ("decode_data_bin()"), from beginning to end of MAJOR
        frame
     5) write data to putput file
     6) go to next MAJOR frame
 6) close read file, close write file

=============================================================================

 *** NOTES on struct module ***
##import struct
# structure format codes
  # H := 2-Byte unsigned short
  # I := 4-Byte unsigned integer
  # L := 4-Byte unsigned long
  # f := 4-Byte float
# struc encoding codes
  # < little-endian; least significant digit first
  # > big-endian; most significant digit first

@date: Feb 2016
@author: joesmith@iastate.edu
"""

import argparse   # use command line arguments
import os         # os.path.join()  &  os.listdir()
import datetime   # datetime & timedelta
import sys        # sys.exit() & email (tail -5) & sys.path.append
import re         # re.match()
import struct     # unpacking binary
import psycopg2   # connect to database
import ftplib     # deleting file from datalogger
import json

# email
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import subprocess

# logging
import logging.config
from log_conf import logger_configurator

# assume we run the script from this directory
CONFIG = json.load(open("../config/settings.json", 'r'))

# create logger
logger_config = logger_configurator()
logger_config.make_log_files()
logging.config.dictConfig(logger_config.log_conf_dict)
logger = logging.getLogger(__name__)

# CSI datalogger timestamps are based on seconds since midnight, 1-Jan-1990
csi_epoch = datetime.datetime(1990, 1, 1)

data_type_dict = {
    # primary dictionary for decoding bytes and formatting output stirngs
    # used for decoding all TOB file types, even if some datatypes only appear
    # in one type of TOB file
    # name         format        size         reformat_string
    # {Bool8} string of eight bits; the bit order is reveresed (no idea why.)
    'BOOL8':    {'fmt': 'B',   'size': 1,    'refmt': '"{}"'},
    # {Boolean} "0" or "-1" (aka. False/True)
    'BOOL4':    {'fmt': '4B',  'size': 4,    'refmt': '{}'},
    # {Boolean} "0" or "-1" (aka. False/True)
    'BOOL2':    {'fmt': '2B',  'size': 2,    'refmt': '{}'},
    # {Boolean} "0" or "-1" (aka. False/True)
    'BOOL':     {'fmt': 'B',   'size': 1,    'refmt': '{}'},
    #
    'UINT2':    {'fmt': '>H',  'size': 2,    'refmt': '{}'},
    #   TOB1
    'UINT4':    {'fmt': '>L',  'size': 4,    'refmt': '{}'},
    #   TOB3
    'INT4':     {'fmt': '>l',  'size': 4,    'refmt': '{}'},
    # {TIMESTAMP & RECORD}
    'ULONG':    {'fmt': '<L',  'size': 4,    'refmt': '{}'},
    # {Long} signed integer; twos compliment! ?????
    'LONG':     {'fmt': '<l',  'size': 4,    'refmt': '{}'},
    # {FP2}
    'FP2':      {'fmt': '>H',  'size': 2,    'refmt': '{:.4g}'},
    # {IEEE4}  little-Endian for TOB1 !!!  TOB1
    'IEEE4':    {'fmt': '<f',  'size': 4,    'refmt': '{:.7g}'},
    # {IEEE4}  little-Endian for TOB1 !!!  ...same as IEEE4
    'IEEE4L':   {'fmt': '<f',  'size': 4,    'refmt': '{:.7g}'},
    # {IEEE4}   Big-Endian  for  TOB3 !!!  TOB3
    'IEEE4B':   {'fmt': '>f',  'size': 4,    'refmt': '{:.7g}'},
    # {Nsec} string YYYY-MM-DD hh:mm:ss.  TOB1
    'SecNano':  {'fmt': '<2L', 'size': 8,    'refmt': '"{}"'},
    # {Nsec} string YYYY-MM-DD hh:mm:ss.  TOB3
    'NSec':     {'fmt': '>2I', 'size': 8,    'refmt': '"{}"'},
    # {String}; is still in ASCII, NOT binary!!!
    'ASCII':    {'fmt': 's',   'size': None, 'refmt': '"{}"'},
}

file_type_dict = {
    # for TOB2 & TOB3
    # fhs := frame header size
    # ffs := frame footer size
    'TOB2': {'fhs':  8, 'ffs': 4},
    'TOB3': {'fhs': 12, 'ffs': 4},
}

interval_dict = {
    # for TOB2 & TOB3
    # this dictionary converts the "Frame Time Resolution"
    # (header line 2) from,
    #   its subseconds (integer) into seconds (float value, if result is less
    # than one second)
    'NSEC': 1e-9,
    'USEC': 1e-6,
    'MSEC': 1e-3,
    'SEC':  1,
    'MIN':  60,
    'HR':   3600,
    'DAY':  86400,
}

resolution_dict = {
    # for TOB2 & TOB3
    # used to decode the TOB3 headers timestamp (sub-second value).
    # This dictionary
    #  returns the number of microseconds for each "subsecond" 4-Byte integer
    # in the header.
    # This is the multiplier of the sub-second part, in order to achieve
    # microseconds.
    # MICROsecond are the 3rd value in datatime.timedelta(day,seconds,
    # microseconds)
    'Sec10Usec':  10,
    'Sec100Usec': 100,
    'SecUSec':    10,
}


def decode_data_bin(rec, dtl, bl, csi_epoch=csi_epoch):
    """
    Decode binary data according to data type.

    Parameters
    ----------
    rec: string
        one data record (aka. row) worth of Binary data
    dtl: list of strings
        list of datatypes, for each value in record; header[4], EXCEPT "ASCII"
        instead of "ASCII(#)" variants
    bl: list of integers
        the number of bytes, for each value in record
    csi_epoch: boolean (optional, as long as csi_epoch set in main program)
        the CSI epoch is 1-Jan-1990 00:00:00.

    Returns
    -------
    values: list
        the formatted ASCII data values from one record (aka. row).

    Notes
    -----
    This is the work horse for decodeing TOB1 or TOB3 records' data.
    """
    offset = 0  # offset into buffer
    values = []  # list of values to return
    for size, dtype in zip(bl, dtl):
        fmt = data_type_dict[dtype]['fmt']
        if dtype == "FP2":  # special handling: FP2 floating point number
            fp2 = struct.unpack(fmt, rec[offset:offset+size])[0]
            mant = fp2 & 0x1FFF    # mantissa is in bits 1-13
            exp = fp2 >> 13 & 0x3  # exponent is in bits 14-15
            sign = fp2 >> 15       # sign is in bit 16
            value = (-1)**sign * float(mant) / 10**exp
            if exp == 0:
                if mant == 8190:  # and sign == 0:
                    value = float('nan')
                if mant == 8191:
                    if sign == 0:
                        value = float('inf')
                    else:
                        value = float('-inf')
        elif "ASCII" in dtype:
            string = rec[offset:offset+size-1]   # the -1 is because the null
            # terminator (\x00) is included in the dimmensioning allocation.
            # ...sometimes hex values come through in the converstion, often
            # "\x00" but sometimes others like "\x05"
            # ...based on a very few (!) observations, if there is one "\x00"
            # value, ignore everything after it within that string's remaining
            # byte allocation.
            value = string.split('\x00', 1)[0]
        elif dtype == "SecNano" or dtype == "NSec":
            ts_list = struct.unpack(fmt, rec[offset:offset+size])
            # ts_list[seconds since CSI epoch, NANOseconds into second]
            ts = csi_epoch + datetime.timedelta(0, ts_list[0], ts_list[1]/1000)
            value = ts_formatter(ts)
        else:
            # standard processing for all other data types
            value = struct.unpack(fmt, rec[offset:offset+size])[0]
            if "BOOL" in dtype:
                # special processing for Boolean data types.
                if dtype == "BOOL":
                    # returns -1 for True, and 0 for False
                    value = -1 if value != 0 else 0
                if dtype == "BOOL2" or dtype == "BOOL4":
                    # BOOL4 is 1 for True, and 0 for False, which is
                    # different than BOOL!!!!
                    value = 1 if value != 0 else 0
                if dtype == "BOOL8":
                    # returns a stiring of 1/0 bits (True/False)
                    #  ...the native bit order is reversed, based on
                    # CardConvert results, to the output is reversed before
                    # being formatted as a string.
                    value = "{0:08b}".format(value)[::-1]
        values.append(value)
        offset += size
    # Return decoded values
    return values


def ts_formatter(ts, ts_format='csi'):
    """
    Format datetime.dateteim object, with option to match CSI's output.

    Parameteres
    -----------
    ts: datetime.datetime object
    ts_format = string (optional, as long as ts_format set in main program)
        "millisec","sec","csi"
        this round to seconds or milliseconds, or minimal characters ("csi")

    returns
    -------
    value: string
        standardized format
    """
    if ts_format == "csi":
        value = "{:%Y-%m-%d %H:%M:%S.%f}".format(ts).strip("0").strip(".")
    elif ts_format == "millisec":
        # millisecond resolution
        value = "{:%Y-%m-%d %H:%M:%S.%f}".format(ts)[:-3]
    elif ts_format == "sec":
        # second resolution
        value = "{:%Y-%m-%d %H:%M:%S}".format(ts)
    else:
        # microseconds resolutionn, because datatime rounds/?truncates?
        # to nanoseconds to microseconds
        value = "{:%Y-%m-%d %H:%M:%S.%f}".format(ts)
    return value


def footer_parse(footer, validation_int):
    """
    Parse the footer of a TOB3 endoced frame.

    Parameters
    ----------
    footer: string
        binary encoded string with length of 4-Bytes
    validation_int: integer
        the validation code from header[1][4]

    Returns
    -------
    Valid_frame: Boolean
        did the file's header and frames validation code match?
    F: binary (1=true, 0=false)
        File mark; a programaticly controlled marker
    R: binary (1=true, 0=false)
        Removed card during writing of frame (frame is held open for the entire
            data writting period, which is defined in CSI's TableFile()
            instruction.)
    E: binary (1=true, 0=false)
        Empty frame
    M: binary (1=true, 0=false)
        Minor frame
    minor_frame_size: integer
        the size of a minor frame, otherwise for TOB3 major frame this is 0

    Notes
    -----
    Length of footer is 4 btes.
    """
    logger = logging.getLogger(__name__)
    # CSI documentation says "read as a 4-Byte unsigned integer with least
    # significant byte stored first".
    # ...that is, with little-Endian encoding, and then operate on the
    # bits of those 4-Bytes.
    #    bits  0 - 11:  Offset
    #    bits 12 - 15:  Flags (F, R, E, M)
    #    bits 16 - 31:  validation --> a 2-Byte integer
    # HOWEVER the bits are all reversed from the documentation!!!  --
    # Not a big/little endian issue.
    # That means the 32 bits of the 4-Byte are as follows:
    #   validation  = footer[0:16]
    #   flags       = footer[16:20]
    #   offset/size = footer[20:32]
    footer_bits = "{0:032b}".format(struct.unpack('<I', footer)[0])
    # validation
    #  the second/last 2-Byte interger, must match (or be the ones compliment)
    # the validation stamp from the header
    V = int(footer_bits[:16], base=2)
    if V == validation_int:
        valid_frame = True
    # ones compliment, i.e. switch the bit values
    elif V == (validation_int ^ 0xFFFF):
        valid_frame = True
    else:
        valid_frame = False
    # for a major frame, if the validation does not match, ignore the frame
    # for a minor frame, ignore the validation; unless the minor frame is also
    # a Major frame boundary, i.e. the last minor frame in the major frame.
    # frame flags
    FREM = int(footer_bits[16:20], base=2)
    (F, R, E, M) = (0, 0, 0, 0)  # reset all flags
    if FREM != 0:
        if FREM & 0b0001:
            # all records in current frame occure before the FILE Mark and
            # all records subsequent were after the Mark.  The mark is set
            # by the program.
            F = 1
        if FREM & 0b0010:
            # card was REMOVED for datalogger after the data in the frame was
            # written.  set by pressing the eject button on hte card.
            R = 1
        if FREM & 0b0100:
            # frame is EMPTY, do not try to access the frame header, minimum
            # frame size is 4-Bytes
            E = 1
        if FREM & 0b1000:
            # frame is a MINOR or Dirty frame,
            M = 1
    # minor frame size:
    minor_frame_size = int(footer_bits[20:], base=2)
    # size includes the minor frame header.
    # This is 0 for a TOB3 Major frame, but if there are minor frames, the
    # major frames footer
    #  is the last minor frame's footer, so this will will have a value, when
    # there is a minor frame flag.
    logger.debug("footer pasred")
    # if invalid, the unknown what the minor_frame_size is
    return valid_frame, F, R, E, M, minor_frame_size


def header_parse(header, ts_resolution, csi_epoch=csi_epoch):
    """
    parses the header of a TOB3 frame.

    Parameters
    ----------
    header: string
        of binary encoded dat with length of 12-Bytes
    ts_resolution:
        frame time resolution.  multiplier for sub-second part of frame
        timestamp to
        acheive microsecond resolution.  from header[1][5]
    csi_epoch: boolean (optional, as long as csi_epoch set in main program)
        the CSI epoch is 1-Jan-1990 00:00:00.

    Returns
    -------
    frame_ts: datetime object
    frame_rec: integer

    Notes
    -----
    assumes header of TOB3, which is 12-Bytes.
    """
    # seconds & sub-seconds: "two four bytes integers (least significant
    # byte fist)"
    #  seconds since CSI epoch (1-Jan-1990)
    #  sub-seconds into number of "Frame Time Resolution" values into current
    # second.
    # beginning record number:  "four byte UNSIGNED integer stored least
    # significant byte first"
    # ...assume all are unsigned, and unpack all of them at once.
    # <<<=====  Assume TOB3 format, i.e. 12-Byte header, not 8-Byte of TOB2
    header_tuple = struct.unpack('<3L', header)
    # datetime.timedelta(days, seconds, microseconds)
    ts = csi_epoch + datetime.timedelta(0, header_tuple[0],
                                        header_tuple[1]*ts_resolution)
    return ts, header_tuple[2]


def decode_frameTOB3(head_and_data, fhs, trs, dtl, bl, rfs, rec_interval,
                     ts_resolution, csi_epoch=csi_epoch):
    """
    decode the data in TOB3 binary frame, after header and footer have
    been decoded.

    Parameters
    ----------
    head_and_data: string
        binary encoded data
    fhs: integer
        Frame Header Size, in bytes
    trs: integer
        Table Record Size, in bytes.
        The number of bytes to encode one record (aka row)
    dtl: list of integers
        Data Type Length.
        the list of number of bytes per measurment in record.
    rfs: string
        Record Format String.  the string to use with .format(),
        for each record.
    rec_interval: integer
        the time period between records, in seconds.
        calculated form header[1][1]
    ts_resolution:
        frame time resolution.  multiplier for sub-second part of frame
            timestamp to acheive microsecond resolution.  from header[1][5]
    csi_epoch: boolean (optional, as long as csi_epoch set in main program)
        the CSI epoch is 1-Jan-1990 00:00:00.

    Returns
    -------
    list of strings
        from the data (including TIMESTAMP & RECORD), in the order of the
            frame, whether Major or minor.

    Notes
    -----
    Decodes major or minor frame, whichever's data is in theparameter.
    """
    logger = logging.getLogger(__name__)
    logger.debug('+++ decoding TOB3 frame +++')
    # --- frame header  ---
    frame_ts, frame_rec = header_parse(head_and_data[:fhs], ts_resolution)
    # --- frame Data ---
    data = head_and_data[fhs:]
    # loop though frame's data by the size of each records data,
    # until the end of the frame.
    # call "decode_databin()" convert each record to a sting,
    # & write it to output
    records_raw = []
    for pt in range(0, len(data), trs):
        # 1) decode the bytes coresponding to one row's data
        # 2) format each row using the format string calculated from the header
        # 3) replace 'nan' with '"NAN"'
        # 4) append each formatted data row to records list
        record_list = decode_data_bin(data[pt:pt+trs], dtl, bl)
        raw_str = rfs.format(*record_list)
        records_raw.append((raw_str.replace('nan', '"NAN"').
                            replace('inf', '"INF"').
                            replace('-inf', '"-INF"')))
    # calculate TIMESTAMP & RECORD number for each record and prepend to each
    # formatted data row,
    #   This results in the format how each row will be written to file.
    records = []
    for row in records_raw:
        ts_str = ts_formatter(frame_ts)
        records.append('"' + ts_str + '",' + str(frame_rec) + ',' + row)
        frame_ts += datetime.timedelta(seconds=rec_interval)
        frame_rec += 1
    # Return a list of strings (formatted data rows)
    return records


def decode_TOB3(ffn, toa5_file):
    """
    Decode TOB3 binary file (written to CRD) to TOA5 formatted ASCII (the
        standard CSI file type).

    Parameters
    ----------
    ffn : string
        full file name, including path and extention.
    toa5_file: string
        full file name of output file.
    _troubleshooting_: boolean (set by script, not an argument!)
        set by program, this option prints intermediate results and pauses
        script for monitoring progres.

    Returns
    -------
    none
        this just writes a new file.

    Notes
    -----
    TOB3 files are written in major and minor frames, from top to bottom.  Each
        frame's footer must be check first.  If the frame if valid, it is
        decoded.
    This function was written as the main(), but has since been incorporated as
        a function of its own.
    """
    logger = logging.getLogger(__name__)
    fn = os.path.basename(ffn)
    logger.info("starting to decode TOB3 file:  {}".format(fn))
    rec_cnt = 0
    header = []
    valid_frame_cnt, not_valid_frame_cnt = 0, 0
    with open(ffn, "rb") as rf:
        for ii in range(6):
            header.append((rf.readline().replace('"', "")
                           .replace("\r\n", "").replace("\n", "").split(",")))
        # extract header information
        #  bl := Byte Length; list of bytes length per measurment for each
        # record.
        # dtl := Data Type List; datatypes, but with "ASCII" instead of
        # "ASCII(?+)", necessicary for dictionary lookup
        # rfs := Record Format String; the string to use with .format(),
        # for each record
        # trs := Table Record Size; number of Bytes per record
        # remove trailing spaces from last data type definition from header,
        # which may be padded with spaces, so that the table header ends as
        # a sector boundary.
        dtypes = [ss.replace(" ", "") for ss in header[5]]
        dtl = [xx.split("(")[0] for xx in dtypes]
        rfs = ",".join([data_type_dict[xx]['refmt'] for xx in dtl]) + '\n'
        bl = [int(xx.split("(")[1][:-1])
              if ('ASCII' in xx) else data_type_dict[xx]['size']
              for xx in dtypes]
        trs = sum(bl)
        # -- look-up header & footer size --
        # fs := data Frame Size
        # tbl := table size; intendes number of records in file
        fs = int(header[1][2])
        tbl = int(header[1][3])
        # fft := file format type
        # fhs := frame header size
        # ffs := frame footer size
        fft = header[0][0]
        # check file's format
        if fft != 'TOB3':
            logger.critical("File ({}) is not TOB3 type!")
            email_exit()
        fhs = file_type_dict[fft]['fhs']
        ffs = file_type_dict[fft]['ffs']
        # nr := number of records per [major] frame
        # ds := data size, within frame
        # ## <<<=====  Assume interval dirven data record ###
        interval_driven = True
        if interval_driven:
            if (trs + fhs + ffs) < 1024:
                ds = 1024 - (fhs + ffs)
                nr = ds/trs
                fs_check = nr*trs + fhs + ffs
            else:
                fs_check = trs + fhs + ffs
            if fs_check != fs:
                # this should be a more serious issue, that the file and CSI
                # standard do not match, but after months of WARNINGS this is
                # demoted to debug
                logger.debug(("File ({}) header Inconsistentcy for bytes per "
                              "framesize; using header data, not manual's "
                              "equation."
                              ).format(fn))
        # interval := non-timestamped record interval; for intra-frame
        # timestamps; in seconds
        interval_str = header[1][1].split(" ")
        interval = int(interval_str[0])*interval_dict[interval_str[1]]
        # resolution := frame time resolution;  multiplier for sub-second
        # part of frame timestamp to acheive microsecond resolution.
        ts_resolution = resolution_dict[header[1][5]]
        # validation := 2-Byte unsigned integer, this or its compliment, are
        # compared with footer for validating frame integrity
        validation_int = int(header[1][4])
        # validation_bits = "{:016b}".format(int(header[1][4]))
        # reformat header for output
        ho = [header[xx] for xx in [0, 2, 3, 4]]
        ho[0][0] = "TOA5"
        ho[0][-1] = header[1][0]
        ho[0].append(fn)        # add origional file name to header.
        ho[1] = ["TIMESTAMP", "RECORD"] + ho[1]
        ho[2] = ["TS", "RN"] + ho[2]
        ho[3] = ["", ""] + ho[3]
        # open output file for writing
        with open(toa5_file, "w") as outfile:
            # outfile = open(output,"w")
            # write header
            for hh in ho:
                outfile.write('"' + '","'.join(hh) + '"\n')
            logger.debug("header written")
            # examine contents
            # loop though file's Major Frames
            major_cnt = 0  # used only for debugging
            frame = rf.read(fs)
            while len(frame) == fs:
                logger.debug("MajorFrame: {}".format(major_cnt))
                major_cnt += 1  # used only for above
                # read frame footer
                (valid_frame, F, R, E, M, minor_frame_size
                 ) = footer_parse(frame[-ffs:], validation_int)
                if valid_frame:
                    valid_frame_cnt += 1
                    # initialize list to hold formatted strings, which will
                    # be written to out file, after processing
                    # each Major frame.
                    records = []
                    if not(E == 1 or M == 1):
                        # standard Major Frame processing
                        records = decode_frameTOB3(frame[:-ffs], fhs, trs,
                                                   dtl, bl, rfs, interval,
                                                   ts_resolution)
                    else:
                        subframe_cnt = 0  # ### for debug only ####
                        skip_sub_frame, cnt_sub_frame = 0, 0  # debugging only
                        # enter sub-frame loop
                        # this processes the unknown number of sub-frames
                        # within the Major frame
                        # start from the back of the major frame, and based
                        # on the footer,
                        #   identify the size of the sub-frame; analyze; then
                        # move forward
                        #   in the major frame by the size of the sub-frame.
                        logger.debug("MINOR Frame processing!!!!")
                        # initialize sub-frame loop (only 1 recursion deep, so
                        # an "if" control works fine)
                        # Byte count from the *END* of the Major Frame; when
                        # this == fs, the sub-frame while loop breaks.
                        subframe_offset = 0
                        # the location of the end for the current sub-frame;
                        # byte count from the front of the file.
                        subframe_end_ptr = fs
                        sub_frame = frame[
                            (subframe_end_ptr - minor_frame_size):
                                subframe_end_ptr]
                        while True:
                            # sub-frame at a Major frame boundary may be listed
                            # as empty, but the other sub-frames may have data
                            if not(E == 1):
                                # append sub-frame records to records, i.e.
                                # make a list (i.e. major frame) of lists
                                # (i.e. minor frames).
                                records.append(
                                    decode_frameTOB3(
                                        sub_frame[:-ffs], fhs, trs, dtl,
                                        bl, rfs, interval,
                                        ts_resolution))
                            # identify location of next sub-frame
                            subframe_offset += minor_frame_size
                            subframe_end_ptr = fs - subframe_offset
                            if logger.isEnabledFor(logging.DEBUG):
                                debugstr = ("subframe: {}   "
                                            ).format(subframe_cnt)
                                debugstr += ("F={}, R={}, E={}, M={}\n"
                                             ).format(F, R, E, M)
                                debugstr += ("\t\tminor_frame_size = {}"
                                             ).format(minor_frame_size)
                                debugstr += ("subframe_offset = {}\t"
                                             ).format(subframe_offset)
                                debugstr += ("\t\tnext footer slice of "
                                             "frame [{}:{}]\n"
                                             ).format(-(subframe_offset+ffs),
                                                      -subframe_offset)
                                debugstr += ("\t\t                          "
                                             "[{}:{}]\n"
                                             ).format(fs-(subframe_offset+ffs),
                                                      fs-subframe_offset)
                                debugstr += ("\t\tnext minor frame slice of "
                                             "frame [{}:{}]\n"
                                             ).format((subframe_end_ptr -
                                                       minor_frame_size),
                                                      subframe_end_ptr)
                                debugstr += "- "*20
                                logger.debug(debugstr)
                                if skip_sub_frame == cnt_sub_frame:
                                    # int(raw_input("**-Paused for
                                    # debugging-**\n**Enter number of MINOR
                                    # frames to skip over; 0 (zero) is
                                    # default.**\n"))
                                    skip_sub_frame = 0
                                    cnt_sub_frame = -1
                                cnt_sub_frame += 1  # used for skip subframes
                                subframe_cnt += 1   # only used for debugging
                            if subframe_offset >= fs:
                                # the total lenght of sub-frames has exhausted
                                # the length of the Major frame
                                #   exit the while loop, and return to the main
                                # loop to write records to output.
                                # A slice of major frame with a negative first
                                # index results in an empty set,
                                #   and processing that empty set in the footer
                                # parse results in an index error.
                                #   read next (actaull previous in memory)
                                # frame's footer
                                break
                            # read next subframe' footer
                            (valid_frame, F, R, E, M, minor_frame_size
                             ) = footer_parse(
                                frame[-(subframe_offset+ffs):-subframe_offset],
                                validation_int)
                            # read next subframe
                            sub_frame = (
                                frame[(subframe_end_ptr - minor_frame_size):
                                      subframe_end_ptr])
                    # record list of valid frame has been assembled.
                    # check if sub-frames exist; if yes, reorder sub-frames,
                    # and prepare for writing
                    if records and type(records[0]) == list:
                        # have a list of lists, which needs to be reveresed
                        # (becaue sub-frames are
                        #   read from bottom to top of major frame).
                        # Then flatten, so that record is
                        #   a list of strings, and not a list of lists of
                        # strings.
                        records.reverse()
                        records = [jj for ii in records for jj in ii]
                    rec_cnt += len(records)
                    # write to output file
                    outfile.writelines(records)
                else:
                    not_valid_frame_cnt += 1
                    if not_valid_frame_cnt > 5:
                        # ### 5 is arbitrary, because
                        # after 1 it is probably done.
                        logger.info(("breaking out of major frame parse loop, "
                                     "becaue not_valid_frame_cnt > 5"))
                        break
                # move to next MAJOR frame
                frame = rf.read(fs)
    logger.debug("TOB3 file ({});  rec_cnt = {}".format(fn, rec_cnt))
    return rec_cnt, tbl


def decode_TOB1(ffn, toa5_file):
    """
    Decode TOB1 binary file to TOA5 formatted ASCII
    (the standard CSI file type).

    Parameters
    ----------
    ffn : string
             full file name, including path and extention.
    toa5_file: string
        full file name of output file.

    Returns
    -------
    none
        this just writes a new file.

    Notes
    -----
    TOB1 files are written from top to bottom, without frames; each row is
        self containted.  This function calls many other supporting functions.
    This function was written as the main(), but has since been incorporated as
        a function of its own.
    """
    logger = logging.getLogger(__name__)
    fn = os.path.basename(ffn)
    logger.info("starting to decode TOB1 file {}".format(fn))
    rec_cnt = 0
    header = []
    with open(ffn, "rb") as rf:
        # read the 5 header lines into variable and then parse it.
        for _ in range(5):
            header.append((rf.readline().replace('"', "")
                           .replace("\r\n", "").replace("\n", "").split(",")))
        # extract header information
        #  bl := Byte Length; list of bytes length per measurment for each
        #        record.
        # dtl := Data Type List; datatypes, but with "ASCII" instead of
        #        "ASCII(?+)", necessicary for dictionary lookup
        # rfs := Record Format String; the string to use with .format(),
        #        for each record
        # trs := Table Record Size; number of Bytes per record
        dtypes = header[4]
        dtl = [xx.split("(")[0] for xx in dtypes]
        rfs = ",".join([data_type_dict[xx]['refmt'] for xx in dtl]) + '\n'
        bl = [int(xx.split("(")[1][:-1])
              if ('ASCII' in xx) else data_type_dict[xx]['size']
              for xx in dtypes]
        trs = sum(bl)
        if (header[1][0] == "SECONDS" and header[1][1] == "NANOSECONDS" and
                dtypes[0] == "ULONG" and dtypes[1] == "ULONG"):
            # assume the record's first value is TIMESTAMP
            TIMESTAMP = True
            rfs = '"{}",' + rfs.split(",", 2)[-1]
            logger.debug("file has 'TIMESTAMP'")
        else:
            TIMESTAMP = False
        # write to output file
        # format output file's header
        if TIMESTAMP:
            ho = [xx[1:] for xx in header[:4]]
            ho[0].insert(0, "TOA5")
            ho[1][0] = "TIMESTAMP"
            ho[2][0] = "TS"
        else:
            ho = header[:4]
            ho[0][0] = "TOA5"
        ho[0].append(fn)        # add origional file name to header.
        # write output
        with open(toa5_file, "w") as outfile:
            for hh in ho:
                outfile.write('"' + '","'.join(hh) + '"\n')
            logger.debug("header written")
            # -----------------------------------
            # increment though file one record at a time, write each to file
            rec = rf.read(trs)
            while len(rec) == trs:
                values = decode_data_bin(rec, dtl, bl)
                if TIMESTAMP:
                    # remove the first two ULONG values from list, and
                    # convert to timestamp
                    ts_list = values[:2]
                    values = values[2:]
                    ts = csi_epoch + datetime.timedelta(0, ts_list[0],
                                                        ts_list[1]/1000)
                    values.insert(0, ts_formatter(ts))
                values = ['"NAN"' if xx == 'nan' else xx for xx in values]
                outfile.write(rfs.format(*values))
                rec = rf.read(trs)
                rec_cnt += 1
    logger.debug("TOB1 file ({});  rec_cnt = {}".format(fn, rec_cnt))
    return rec_cnt

# expected file header
#   used as a check, before importing into database
analog = ["TIMESTAMP", "RECORD", "AirTC_120m_1", "AirTC_120m_2", "AirTC_80m",
          "AirTC_40m", "AirTC_20m", "AirTC_10m", "AirTC_5m", "RH_120m_1",
          "RH_120m_2", "RH_80m", "RH_40m", "RH_20m", "RH_10m", "RH_5m",
          "BP_80m", "BP_10m", "WS_120m_NWht", "WS_120m_S", "WS_80m_NW",
          "WS_80m_S", "WS_40m_NWht", "WS_40m_S", "WS_20m_NW", "WS_20m_S",
          "WS_10m_NWht", "WS_10m_S", "WS_5m_NW", "WS_5m_S", "WindDir_120m_NW",
          "WindDir_120m_S", "WindDir_80m_NW", "WindDir_80m_S",
          "WindDir_40m_NW", "WindDir_40m_S", "WindDir_20m_NW",
          "WindDir_20m_S", "WindDir_10m_NW", "WindDir_10m_S", "WindDir_5m_NW",
          "WindDir_5m_S"]
sonic = ["TIMESTAMP", "RECORD", "Ux_120m", "Uy_120m", "Uz_120m", "Ts_120m",
         "Diag_120m", "Ux_80m", "Uy_80m", "Uz_80m", "Ts_80m", "Diag_80m",
         "Ux_40m", "Uy_40m", "Uz_40m", "Ts_40m", "Diag_40m", "Ux_20m",
         "Uy_20m", "Uz_20m", "Ts_20m", "Diag_20m", "Ux_10m", "Uy_10m",
         "Uz_10m", "Ts_10m", "Diag_10m", "Ux_5m", "Uy_5m", "Uz_5m",
         "Ts_5m", "Diag_5m"]
monitor = ["TIMESTAMP", "RECORD", "CR6_BattV", "CR6_PTemp", "BoardTemp_120m",
           "BoardHumidity_120m", "InclinePitch_120m", "InclineRoll_120m",
           "BoardTemp_80m", "BoardHumidity_80m", "InclinePitch_80m",
           "InclineRoll_80m", "BoardTemp_40m", "BoardHumidity_40m",
           "InclinePitch_40m", "InclineRoll_40m", "BoardTemp_20m",
           "BoardHumidity_20m", "InclinePitch_20m", "InclineRoll_20m",
           "BoardTemp_10m", "BoardHumidity_10m", "InclinePitch_10m",
           "InclineRoll_10m", "BoardTemp_5m", "BoardHumidity_5m",
           "InclinePitch_5m", "InclineRoll_5m"]
chk_header = {'analog': analog, 'sonic': sonic, 'monitor': monitor}

# decoding dict for decode_filename()
table_code = {'S': 'sonic', 'A': 'analog', 'M': 'monitor'}

# database's chn_id code
#  based on decode_filename()'s file naming convetions
chn_code = {
            'sites': {'sto': 1000, 'ham': 2000},
            'tables': {'analog': 100, 'sonic': 200, 'monitor': 300}
            # tens & ones digits of chn_id are based the zero-based column
            # position in the .dat file
           }

# for COPYing to dat file
dat_tablecolumns = {'table': 'dat', 'columns': ('ts', 'chn_id', 'val')}


def b38(xx):
    """
    convert base 38 character into its equavalent decimal value.

    Parameters
    ----------
    xx: string
        lenght must be 1!!

    Returns
    -------
    yy: integer
        number in decimal

    Notes
    -----
    This is a custom code for CSI dataloggers, and is probably not used
    anywhere else.
    """
    logger = logging.getLogger(__name__)
    value = ord(xx)
    if value == 45:     # - (dash)
        yy = 36
    elif value < 58:    # [0-9]
        yy = value - 48
    elif value > 96:    # [a-z]
        yy = value - 87
    elif value == 95:   # _ (underscore)
        yy = 37
    else:
        logger.error("character is not in custom Base 38 encoding.  Abort!")
        email_exit()
    return yy


def decode_filename(fn, dirpath):
    """
    decodes the file name from the logger

    Parameters
    ----------
    fn: string
        filename
    dirpath: string
        directory path to root of storage, in which directories
            of year/month/day will be built and data stored.
    table_code: dictionary [optional]
        decode table characters to table names

    Returns
    -------
    newffn: string
        new full-filename, without extention (extention added
        after file closes)

    Notes
    -----
    the file format is as follows
        sto|ham :: site name
        [SAM] :: Sonic, Analog (CR3000), Monitor
            (CSAT3Bs' health & orientation)
        [0-9a-z_-]{5} :: YYYY-2000, MM, DD, minutes since midnight --
            all in base 38 the order is 0-9 a-z - _
        .bdat :: binary data file
    this also cals mkdir so that the output path is valid.
    """
    logger = logging.getLogger(__name__)
    decode = [b38(xx) for xx in fn[4:9]]
    yyyy = str(decode[0]+2000)
    mm = "{:02}".format(decode[1])
    dd = "{:02}".format(decode[2])
    hhtt = "{:02}{:02}".format(*divmod(decode[3]*38+decode[4], 60))
    filepath = os.path.join(dirpath, yyyy, mm, dd)
    chkmkdir(filepath)
    newfn = (fn[:3] + '_' + table_code[fn[3]] + '_' +
             yyyy[2:]+mm+dd + '-' + hhtt)
    newffn = os.path.join(filepath, newfn)
    logger.info("filename decoded:  {} = {}".format(fn, newfn))
    return newffn


def directory_traverse(dirpath, dates):
    """
    relative directories which contain data within the date range of dates
        variable. This traverses the driectory tree as built by
        decode_filename().

    Parameters
    ----------
    dirpath: string
        the root of the ASCII files, i.e. the dirctory containing the YYYY
            directory(s)
    dates: datetime.date
        the object is created based on command line (argparse) input, and is
        validated at that time.

    Returns
    -------
    dir_list_filtered: list
        list of string, which are the relative paths to the directories
        containing data between the dates.

    Notes
    -----
    This does NOT return the files, but only the directoreis which
    contain the data. code efficinecy is not optimal, but this should not be
    called often.
    """
    logger = logging.getLogger(__name__)
    logger.info("starting parsed directory traverse")

    def datenum1(date):
        '''integer representing YYYYMMDD from datetime.date object'''
        return date.year*10000 + date.month*100 + date.day

    def datenum2(dir_rel):
        '''integer representing YYYYMMDD from "YYYY/MM/DD" formatted string'''
        xx = os.path.split(dir_rel)
        yy = os.path.split(xx[0])
        return int(yy[0])*10000 + int(yy[1])*100 + int(xx[1])

    date_start = datenum1(dates[0])
    date_end = datenum1(dates[1])
    logger.debug("date_start = {};   date_end = {}".format(date_start,
                                                           date_end))
    dir_list = []
    startinglevel = dirpath.count(os.sep)
    for top, _, _ in os.walk(dirpath):
        if top.count(os.sep) - startinglevel == 3:
            dir_list.append(os.path.relpath(top, dirpath))
    dir_list.sort()
    dir_list_filtered = [xx for xx in dir_list
                         if (datenum2(xx) >= date_start and
                             datenum2(xx) <= date_end)]
    logger.info(("number of directories to Reimport via SQL = {}"
                 ).format(len(dir_list_filtered)))
    logger.debug("directories to import:\n{}".format(dir_list_filtered))
    return dir_list_filtered


def chkmkdir(dirpath):
    """
    checks if a folder-path exists; if path does not, path is created.

    Parameters
    ----------
    dirpath: string
        the path to the director

    Notes
    -----
    os module should work on Windows and Linux
    """
    logger = logging.getLogger(__name__)
    if dirpath[-1] != '/':
        dirpath = dirpath + '/'
    newdir = os.path.dirname(dirpath)
    if not os.path.exists(newdir):
        os.makedirs(newdir)
        logger.info("dirpath made to: {}".format(newdir))


def email_error(body, to_address=["joesmith@iastate.edu", ],
                tail_error_log=True,
                ffn_error=logger_config.ffn_error):
    """
    send email to joesmith@iastate.edu regarding specific fault for specified
    filename.
    The env parameter is for sellecting if this sends though the ISU network,
    or a VPN connetion, becasue different connections apply to each.

    Parameters
    ----------
    body: string
        email body text
    log_conf: dictionary   [default = 'svr']

    Returns
    -------
    none

    Notes
    -----
    Email may compress multiple spaces in formatted "fn" into one tab.
    """
    logger = logging.getLogger(__name__)
    toaddr = ",".join(CONFIG['email']['to'])
    fromaddr = CONFIG['email']['from']
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Talltowers - FAILURE"

    if tail_error_log:
        body = body + "\n\n" + subprocess.check_output(['tail', '-10',
                                                        ffn_error])
    msg.attach(MIMEText(body, 'plain'))

    logger.info('Emailing ERROR to: {}'.format(toaddr))

    server = smtplib.SMTP(CONFIG['email']['server'])
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


def email_exit(msg=""):
    """
    email error log tail, and then exit
    """
    logger = logging.getLogger(__name__)
    if msg:
        msg = msg + '\n'
    email_error(msg + "Fatal error, see error log.")
    logger.critical("ABORTED!\n" + "*"*20 + "  END OF LOG  " + "*"*20)
    sys.exit()


def ftp_del(fn):
    """
    Delete dataloger-side file associated with server side file named 'fn'.
    Dataloggers must have FTP service enabled.  Files must be in CRD:

    Paramters
    ---------
    fn : str
        the name of the file as it is on the FTP server, which contains
        the name of thefile as it is on the datalogger.

    Return
    ------
    None

    Notes
    -----
    Campbell dataloggers are active FTP so set pasv to False
    """
    # get file name as it exists on the datalogger
    fn_logger = fn[3:9]
    # identfiy which logger the file comes from
    cr6 = CONFIG['ftp'][fn[0:3]]
    if cr6['hostname'] == '...':
        logger.info("Skipping ftp_del since hostname is ...")
        return
    # log into dataloggers FTP service, navigate to direcotry, delete file
    site = ftplib.FTP(cr6['hostname'], cr6['user'], cr6['pass'])
    site.set_pasv(False)
    site.cwd('\CRD')
    site.delete(fn_logger)


def parse_TOA5_sql(ffn, chk_header=chk_header, dirpath=None,
                   chn_code=chn_code):
    """
    parse the TOA5 formatted .dat file (4 header rows) into a .sql file.

    Parameters
    ----------
    ffn: string
        full-filename (includes path and extention)
    chk_header: dictionary [optional]
        lists coresponding to datafile type (sonic,analog,monitor) the expected
        header as a list, for comparison to channels table in database
    dirpath: string [optional]
        location to store tempororary .sql file
    chn_code: dictionary
        of dictionaries, to define the chn_id encoding based on site & table

    Returns
    -------
    sql_filename: sting
        full-filename (includes path and extention)

    Notes
    -----
    dat(ts,chn_id,val)
    All data types are converted into floats, becasue the dat table is defined
        for 4-Byte floats; this means the diagnostic flags from the sonic are
        not integers in the database.
    float("NAN"),float("INF"),float("-INF") are converted into floats, and
        psycopg2 converts nan,inf,-inf into apporprate Postgres
        representations.  Therefore there is no need to filter and replace
        ['"NAN"','"INF"','"-INF"'].
    """
    logger = logging.getLogger(__name__)
    if dirpath is None:
        dirpath = CONFIG['dataroot']
    # setup filenames and
    fn = os.path.basename(ffn)
    logger.info("starting to parse TOA5 file: {}".format(fn))
    fn_basename = os.path.splitext(fn)[0]
    site, table, _ = fn_basename.split("_")
    sql_ffn = os.path.join(dirpath, fn_basename+'.sql')
    # chn_id encoding
    site_number = chn_code['sites'][site]
    table_number = chn_code['tables'][table]
    # get header & compare to expected header
    with open(ffn, 'r') as rf:
        for _ in range(2):
            header = rf.readline()
    header_list = header.replace('"', "").strip('\n').strip('\r').split(',')
    if header_list != chk_header[table]:
        logger.error(("TOA5 header does not match database channel table "
                      "for {}  Aborting.").format(ffn))
        return None
    # convert TOA5 data file to SQL file.
    with open(ffn, 'r') as rf, open(sql_ffn, 'w') as wf:
        for _ in range(4):
            next(rf)  # skip headers
        for row in rf:
            rowlist = row.replace('"', "").strip('\n').strip('\r').split(',')
            ts = rowlist[0]
            ts_format = ('%Y-%m-%d %H:%M:%S.%f'
                         if '.' in ts else '%Y-%m-%d %H:%M:%S')
            dts = datetime.datetime.strptime(ts, ts_format)
            # record number is not stored in database.
            for nn, val in zip(range(2, len(rowlist)), rowlist[2:]):
                wf.write(("{}\t{}\t{}\n"
                          ).format(dts, site_number + table_number + nn,
                                   float(val)))
    # return full file name for SQL formatted file
    return sql_ffn


def copy2db_execute(sql_ffn, db, table='dat', columns=('ts', 'chn_id', 'val'),
                    UTC=True):
    """
    Copy SQL formatted data file to database.  intended for use immedaitly
        after sql_ffn = parse_TOA5_sql(ffn)

    Parameters
    ----------
    sql_ffn : str
        full path file name, which contains SQL formatted data to copy to
        database.
    db: dictionary
        holds dbname, dbuser, & dbpass
    table: string [optional]
        table to COPY to, default is 'dat'
    columns : tuple of strings [optional]
        columns to COPY to (note columns must be a TUPLE)
    UTC: boolean [optional]
        default is False, or else there is an error on the server

    Returns
    -------
    : string
        if successful "COPY Successful."; if unsuccessful, error message string

    Notes
    -----
    requires psycopg2 version > 2.5, whos cursors are context managers, and
        can be used with "with" blocks.

    """
    logger = logging.getLogger(__name__)
    logger.info("starting COPY to db for {}".format(os.path.basename(sql_ffn)))
    try:
        conn = psycopg2.connect(('host={hostname} dbname={dbname} '
                                 'user={dbuser} password={dbpass}'
                                 ).format(**db))
        logger.debug('connected to database')
        curs = conn.cursor()
        infile = open(sql_ffn, 'r')
        logger.debug('database cursor established')
        if UTC:
            curs.execute("set timezone='UTC';")
        curs.copy_from(infile, table=table, columns=columns)
        curs.close()
        conn.commit()
        conn.close()
        logger.debug('copyed to database')
        return "COPY Successful."
        # return None
    except Exception, e:
        logger.exception('Failed to execute COPY for {}'.format(sql_ffn))
        return 'Failed to execute COPY for ' + sql_ffn + '; ErrMsg: ' + str(e)


def reparse_sql(dirpath, dates, dbconn):
    """
    incase of database truncation or making test database, where there is a
        need to reimport data from TOA5 files, which are already in YYYY/MM/DD
        directory struture.  Therefore need to walk the directory tree,
        and search for data between the dates provided.

    Parameters
    ----------
    dates: list
        two strings in lsit, formatted in YYYY-MM-DD format, represting the
        begining date and end date (inclusive) to find TOA5 data, parse it to
        SQL format, and import it to database.

    Returns
    -------
    None

    Notes
    -----
    uses same functions as the origional sql file creation and COPY, except for
        tree_list()
    """
    logger = logging.getLogger(__name__)
    logger.info("starting reparse_sql()")
    # return the directories to work on.
    tree_list = directory_traverse(dirpath, dates)

    for relpath in tree_list:
        fullpath = os.path.join(dirpath, relpath)
        # find only files which are complete, i.e. end with ".dat", there
        # for no partial files will be uploaded.
        fns = [ff for ff in os.listdir(fullpath) if re.match(r".*\.dat$", ff)]
        logger.debug(("number of file to reimport, in current directory = {}"
                      ).format(len(fns)))
        for fn in fns:
            ffn = os.path.join(fullpath, fn)
            # parse to sql
            sql_ffn = parse_TOA5_sql(ffn)
            result = copy2db_execute(sql_ffn, dbconn)
            logger.info(result + "  fn = {}".format(fn))
            if result == "COPY Successful.":
                os.remove(sql_ffn)
                logger.debug("SQL formated file deleted: {}".format(sql_ffn))
    return None


def arg_parse(argv=None):
    """
    command line argument parser.

    Parameters
    ----------
    argv: string
        string of arguments used; designed for command line, but could input
        values as a test.

    Returns
    -------
    arg: dictionary object

    Notes
    -----
    http://stackoverflow.com/questions/26785952/python-argparse-as-a-function
    """
    parser = argparse.ArgumentParser()
    # define arguments:
    parser.add_argument('--dataroot', type=str, default=CONFIG['dataroot'],
                        help="[optional] Root for data files to process.")
    parser.add_argument('--filename', type=str, nargs='+',
                        help=("[optional] Filename(s) to process.  Default "
                              "is to process all files in current directory, "
                              "which match the standard file nameing "
                              "convention"))
    # parser.add_argument("--timestamp", choices=['millisec','sec','csi'],
    #                     default='csi',
    #                     help="[optional] Format string for timestamps.
    #                           Default is 'csi'")
    parser.add_argument("--debug", action="store_true",
                        help=("[optional] Debugging; prints out intermediate "
                              "steps, especially for TOB3 processing"))
    parser.add_argument("--database", type=str,
                        help=("[optional] PostgreSQL database to COPY data "
                              "to.  Default according to pyenv.dbconn."))
    # action='append',
    parser.add_argument('--dates', nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help=("[optional] Two dates 'YYYY-MM-DD' "
                              "(separated by space), as inclusive endpoints "
                              "to RE-Import data to database; but can exceed "
                              "project data's dates in order to import all.  "
                              "Data is already in ASCII and standard folder "
                              "structure."))
    parser.add_argument("--save", action="store_true",
                        help=("[optional] retains the file on the Datalogger. "
                              " Default is to delete the file on the "
                              "Dataloger, after succesfully COPYing to "
                              "the database."))
    # return
    return parser.parse_args(argv)


def arg_check(args):
    """
    check the arguments for validtity and set other variables as necessicary.

    Parameters
    ----------
    args: dicitionary object
        keys are argument flags, and thier values

    Returns
    -------
    dirpath,fnames,dbconn,dates: tuple
    """
    logger = logging.getLogger(__name__)
    # dirpath
    dirpath = args.dataroot
    # fnames
    if args.filename:
        # because of the "nargs='+'" this args.filename is a list already
        fnames = args.filename
        checkpath = [os.path.isfile(os.path.join(dirpath, fn))
                     for fn in fnames]
        if False in checkpath:
            msg = "{}".format([os.path.join(dirpath, fn)
                               for fn, cp in zip(fnames, checkpath)
                               if not(cp)])
            logger.error("filename does not exist:\n"+msg+"\nABORT!")
            email_exit()
    else:
        fn_pattern = r"^(ham|sto)[SAM]{1}[0-9a-z-_]{5}\.bdat$"
        fnames = sorted([fn
                         for fn in os.listdir(dirpath)
                         if re.match(fn_pattern, fn)])
    # dbconn
    dbconn = CONFIG['dbconn']
    if args.database:
        dbconn['dbname'] = args.database
    # [debug] ...nothing returned, because it acts directly upon logger
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logstr = ""
        argdict = args.__dict__
        for key in argdict.keys():
            logstr += "\t{:<15} - {}".format(key, argdict[key]) + "\n"
        logger.debug('\nOptional Arguments: \n' + logstr)
    # dates
    if args.dates:
        try:
            dates = [datetime.datetime.strptime(xx, '%Y-%m-%d').date()
                     for xx in args.dates]
        except ValueError:
            logger.exception(("'--dates' arguments in wrong format; must be "
                              "YYYY-MM-DD, for both dates.\nABORT!"))
            email_exit()
        except Exception:
            logger.exception("{}  ABORT!".format(dates))
            email_exit()
    else:
        dates = None
    # save
    delete_datalogger_fn = not(args.save)
    return dirpath, fnames, dbconn, dates, delete_datalogger_fn


def bin2pg(dirpath, fnames, consumed_dir, dbconn, delete_datalogger_fn):
    """
    Convert Binary CSI file and Copy to postgres.
    """
    logger = logging.getLogger(__name__)
    for fn in fnames:
        logger.info("="*10 + "{:^20}".format(fn) + "="*10)
        # set input and output file names
        ffn = os.path.join(dirpath, fn)
        try:
            # decode filename and create output full-filename
            toa5_file = decode_filename(fn, dirpath)
            # just check header for file type
            with open(ffn, "r") as rf:
                file_type = rf.read(6)
            logger.debug(("file: {}; type: {}; TOA5:{}"
                          ).format(fn, file_type, toa5_file))
            # call appropriate function
            if file_type == '"TOB1"':
                rec_cnt = decode_TOB1(ffn, toa5_file)
                logger.info("file: {} ; records written: {}".format(fn,
                                                                    rec_cnt))
            elif file_type == '"TOB3"':
                rec_cnt = decode_TOB3(ffn, toa5_file)
                logger.info(("file: {} ; records written: {} ; "
                             "header expected: {}"
                             ).format(fn, *rec_cnt))
            elif file_type == '"TOB2"':
                logger.critical('No script to decode "TOB2" file types')
            else:
                logger.error(" unrecognized file type")
            # rename file, as an atomic action, after file writing is complete
            os.rename(toa5_file, toa5_file + '.dat')
            # ------------------------------------------------------------------------
            # parse resultant TOA5 file to SQL file
            sql_ffn = parse_TOA5_sql(toa5_file + '.dat')
            # copy SQL file to database
            result = copy2db_execute(sql_ffn, dbconn)

            if result is not None:
                logger.info(result)
            else:
                logger.info('COPIED \t ', os.path.basename(sql_ffn))
            # remove files

            if result == "COPY Successful.":
                logger.debug("moving .bdat file to /consumed: {}".format(fn))
                chkmkdir(consumed_dir)
                os.rename(ffn, os.path.join(consumed_dir, fn))
                logger.debug("deleteing SQL formated file: {}".format(sql_ffn))
                os.remove(sql_ffn)
                # delete file on CR6 ???
                if delete_datalogger_fn:
                    logger.info(("deleteing DataLogger file "
                                 "associated with: {}"
                                 ).format(fn))
                    ftp_del(fn)
        except:
            quarentine_path = os.path.join(dirpath, 'quarentine')
            chkmkdir(quarentine_path)
            logger.exception(("{}  FAILED.  Moved to '{}'"
                              ).format(fn, quarentine_path))
            # move file
            os.rename(ffn, os.path.join(quarentine_path, fn))


def main(argv):
    """
    The starting point, when program is called.
    """
    # parse the args, from Command Line
    args = arg_parse(argv)
    # check the args
    (dirpath, fnames, dbconn, dates, delete_datalogger_fn) = arg_check(args)

    # set consumed directory
    consumed_dir = os.path.join(dirpath, 'consumed')
    chkmkdir(consumed_dir)
    # reparse ASCII data or start with CSI binary data?
    if dates:
        reparse_sql(dirpath, dates, dbconn)  # reparse ASCII
    else:
        # CSI binary
        bin2pg(dirpath, fnames, consumed_dir, dbconn, delete_datalogger_fn)

if __name__ == "__main__":
    # notes
    # -----
    # logger already set, immediatly after import
    # envornomental varialbes set during import
    logger = logging.getLogger(__name__)
    logger.info("*"*20 + "  STARTING  " + "*"*20)
    main(sys.argv[1:])
