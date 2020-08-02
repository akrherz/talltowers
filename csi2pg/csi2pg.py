"""Parse CS Data

See `README.md` for more details on this code

@date: Feb 2016
@author: joesmith@iastate.edu
"""
# pylint: disable=too-many-lines

import argparse  # use command line arguments
import os  # os.path.join()  &  os.listdir()
import datetime  # datetime & timedelta
import sys  # sys.exit() & email (tail -5) & sys.path.append
import re  # re.match()
import struct  # unpacking binary
import ftplib  # deleting file from datalogger
import json

# email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import subprocess

# logging
import logging.config

# third party
import pandas as pd
import numpy as np
import pytz
import psycopg2

# local directory stuff
from log_conf import logger_configurator  # @UnresolvedImport

# assume we run the script from this directory
CONFIG = json.load(open("../config/settings.json", "r"))

# create logger
logger_config = logger_configurator()
logger_config.make_log_files()
logging.config.dictConfig(logger_config.log_conf_dict)

# CSI datalogger timestamps are based on seconds since midnight, 1-Jan-1990
CSI_EPOCH = datetime.datetime(1990, 1, 1)

data_type_dict = {
    # primary dictionary for decoding bytes and formatting output stirngs
    # used for decoding all TOB file types, even if some datatypes only appear
    # in one type of TOB file
    # name         format        size         reformat_string
    # {Bool8} string of eight bits; the bit order is reveresed (no idea why.)
    "BOOL8": {"fmt": "B", "size": 1, "refmt": '"{}"'},
    # {Boolean} "0" or "-1" (aka. False/True)
    "BOOL4": {"fmt": "4B", "size": 4, "refmt": "{}"},
    # {Boolean} "0" or "-1" (aka. False/True)
    "BOOL2": {"fmt": "2B", "size": 2, "refmt": "{}"},
    # {Boolean} "0" or "-1" (aka. False/True)
    "BOOL": {"fmt": "B", "size": 1, "refmt": "{}"},
    #
    "UINT2": {"fmt": ">H", "size": 2, "refmt": "{}"},
    #   TOB1
    "UINT4": {"fmt": ">L", "size": 4, "refmt": "{}"},
    #   TOB3
    "INT4": {"fmt": ">l", "size": 4, "refmt": "{}"},
    # {TIMESTAMP & RECORD}
    "ULONG": {"fmt": "<L", "size": 4, "refmt": "{}"},
    # {Long} signed integer; twos compliment! ?????
    "LONG": {"fmt": "<l", "size": 4, "refmt": "{}"},
    # {FP2}
    "FP2": {"fmt": ">H", "size": 2, "refmt": "{:.4g}"},
    # {IEEE4}  little-Endian for TOB1 !!!  TOB1
    "IEEE4": {"fmt": "<f", "size": 4, "refmt": "{:.7g}"},
    # {IEEE4}  little-Endian for TOB1 !!!  ...same as IEEE4
    "IEEE4L": {"fmt": "<f", "size": 4, "refmt": "{:.7g}"},
    # {IEEE4}   Big-Endian  for  TOB3 !!!  TOB3
    "IEEE4B": {"fmt": ">f", "size": 4, "refmt": "{:.7g}"},
    # {Nsec} string YYYY-MM-DD hh:mm:ss.  TOB1
    "SecNano": {"fmt": "<2L", "size": 8, "refmt": '"{}"'},
    # {Nsec} string YYYY-MM-DD hh:mm:ss.  TOB3
    "NSec": {"fmt": ">2I", "size": 8, "refmt": '"{}"'},
    # {String}; is still in ASCII, NOT binary!!!
    "ASCII": {"fmt": "s", "size": None, "refmt": '"{}"'},
}

FILE_TYPE_DICT = {
    # for TOB2 & TOB3
    # fhs := frame header size
    # ffs := frame footer size
    "TOB2": {"fhs": 8, "ffs": 4},
    "TOB3": {"fhs": 12, "ffs": 4},
}

INTERVAL_DICT = {
    # for TOB2 & TOB3
    # this dictionary converts the "Frame Time Resolution"
    # (header line 2) from,
    #   its subseconds (integer) into seconds (float value, if result is less
    # than one second)
    "NSEC": 1e-9,
    "USEC": 1e-6,
    "MSEC": 1e-3,
    "SEC": 1,
    "MIN": 60,
    "HR": 3600,
    "DAY": 86400,
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
    "Sec10Usec": 10,
    "Sec100Usec": 100,
    "SecUSec": 10,
}

# expected file header
#   used as a check, before importing into database
analog = [
    "TIMESTAMP",
    "RECORD",
    "AirTC_120m_1",
    "AirTC_120m_2",
    "AirTC_80m",
    "AirTC_40m",
    "AirTC_20m",
    "AirTC_10m",
    "AirTC_5m",
    "RH_120m_1",
    "RH_120m_2",
    "RH_80m",
    "RH_40m",
    "RH_20m",
    "RH_10m",
    "RH_5m",
    "BP_80m",
    "BP_10m",
    "WS_120m_NWht",
    "WS_120m_S",
    "WS_80m_NW",
    "WS_80m_S",
    "WS_40m_NWht",
    "WS_40m_S",
    "WS_20m_NW",
    "WS_20m_S",
    "WS_10m_NWht",
    "WS_10m_S",
    "WS_5m_NW",
    "WS_5m_S",
    "WindDir_120m_NW",
    "WindDir_120m_S",
    "WindDir_80m_NW",
    "WindDir_80m_S",
    "WindDir_40m_NW",
    "WindDir_40m_S",
    "WindDir_20m_NW",
    "WindDir_20m_S",
    "WindDir_10m_NW",
    "WindDir_10m_S",
    "WindDir_5m_NW",
    "WindDir_5m_S",
]
sonic = [
    "TIMESTAMP",
    "RECORD",
    "Ux_120m",
    "Uy_120m",
    "Uz_120m",
    "Ts_120m",
    "Diag_120m",
    "Ux_80m",
    "Uy_80m",
    "Uz_80m",
    "Ts_80m",
    "Diag_80m",
    "Ux_40m",
    "Uy_40m",
    "Uz_40m",
    "Ts_40m",
    "Diag_40m",
    "Ux_20m",
    "Uy_20m",
    "Uz_20m",
    "Ts_20m",
    "Diag_20m",
    "Ux_10m",
    "Uy_10m",
    "Uz_10m",
    "Ts_10m",
    "Diag_10m",
    "Ux_5m",
    "Uy_5m",
    "Uz_5m",
    "Ts_5m",
    "Diag_5m",
]
monitor = [
    "TIMESTAMP",
    "RECORD",
    "CR6_BattV",
    "CR6_PTemp",
    "BoardTemp_120m",
    "BoardHumidity_120m",
    "InclinePitch_120m",
    "InclineRoll_120m",
    "BoardTemp_80m",
    "BoardHumidity_80m",
    "InclinePitch_80m",
    "InclineRoll_80m",
    "BoardTemp_40m",
    "BoardHumidity_40m",
    "InclinePitch_40m",
    "InclineRoll_40m",
    "BoardTemp_20m",
    "BoardHumidity_20m",
    "InclinePitch_20m",
    "InclineRoll_20m",
    "BoardTemp_10m",
    "BoardHumidity_10m",
    "InclinePitch_10m",
    "InclineRoll_10m",
    "BoardTemp_5m",
    "BoardHumidity_5m",
    "InclinePitch_5m",
    "InclineRoll_5m",
]
CHK_HEADER = {"analog": analog, "sonic": sonic, "monitor": monitor}

# decoding dict for decode_filename()
table_code = {"S": "sonic", "A": "analog", "M": "monitor"}

# database's chn_id code
#  based on decode_filename()'s file naming convetions
CHN_CODE = {
    "sites": {"sto": 1, "ham": 0},
    "tables": {"analog": 100, "sonic": 200, "monitor": 300},
}

# for COPYing to dat file
dat_tablecolumns = {"table": "dat", "columns": ("ts", "chn_id", "val")}


def decode_data_bin(rec, dtl, bl):
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
        fmt = data_type_dict[dtype]["fmt"]
        if dtype == "FP2":  # special handling: FP2 floating point number
            fp2 = struct.unpack(fmt, rec[offset : offset + size])[0]
            mant = fp2 & 0x1FFF  # mantissa is in bits 1-13
            exp = fp2 >> 13 & 0x3  # exponent is in bits 14-15
            sign = fp2 >> 15  # sign is in bit 16
            value = (-1) ** sign * float(mant) / 10 ** exp
            if exp == 0:
                if mant == 8190:  # and sign == 0:
                    value = float("nan")
                if mant == 8191:
                    if sign == 0:
                        value = float("inf")
                    else:
                        value = float("-inf")
        elif "ASCII" in dtype:
            string = rec[
                offset : offset + size - 1
            ]  # the -1 is because the null
            # terminator (\x00) is included in the dimmensioning allocation.
            # ...sometimes hex values come through in the converstion, often
            # "\x00" but sometimes others like "\x05"
            # ...based on a very few (!) observations, if there is one "\x00"
            # value, ignore everything after it within that string's remaining
            # byte allocation.
            value = string.split("\x00", 1)[0]
        elif dtype == "SecNano" or dtype == "NSec":
            ts_list = struct.unpack(fmt, rec[offset : offset + size])
            # ts_list[seconds since CSI epoch, NANOseconds into second]
            ts = CSI_EPOCH + datetime.timedelta(
                0, ts_list[0], ts_list[1] / 1000
            )
            value = ts_formatter(ts)
        else:
            # standard processing for all other data types
            value = struct.unpack(fmt, rec[offset : offset + size])[0]
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


def ts_formatter(ts, ts_format="csi"):
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
    valid_frame: Boolean
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
    Length of footer is 4 bytes.
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
    footer_bits = "{0:032b}".format(struct.unpack("<I", footer)[0])
    logger.debug("footer_bits: %s", footer_bits)
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
            # all records in current frame occur before the FILE Mark and
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
    logger.debug(
        "V: %s validation_int: %s minor_frame_size: %s",
        V,
        validation_int,
        minor_frame_size,
    )
    # size includes the minor frame header.
    # This is 0 for a TOB3 Major frame, but if there are minor frames, the
    # major frames footer
    #  is the last minor frame's footer, so this will will have a value, when
    # there is a minor frame flag.
    # if invalid, the unknown what the minor_frame_size is
    return valid_frame, F, R, E, M, minor_frame_size


def header_parse(header, ts_resolution):
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
    header_tuple = struct.unpack("<3L", header)
    # datetime.timedelta(days, seconds, microseconds)
    ts = CSI_EPOCH + datetime.timedelta(
        0, header_tuple[0], header_tuple[1] * ts_resolution
    )
    return ts, header_tuple[2]


def decode_frameTOB3(
    head_and_data, fhs, trs, dtl, bl, rfs, rec_interval, ts_resolution
):
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
    logger.debug("+++ decoding TOB3 frame +++")
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
        record_list = decode_data_bin(data[pt : pt + trs], dtl, bl)
        raw_str = rfs.format(*record_list)
        records_raw.append(
            (
                raw_str.replace("nan", '"NAN"')
                .replace("inf", '"INF"')
                .replace("-inf", '"-INF"')
            )
        )
    # calculate TIMESTAMP & RECORD number for each record and prepend to each
    # formatted data row,
    #   This results in the format how each row will be written to file.
    records = []
    for row in records_raw:
        ts_str = ts_formatter(frame_ts)
        records.append('"' + ts_str + '",' + str(frame_rec) + "," + row)
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

    Returns
    -------
    none
        this just writes a new file.

    Notes
    -----
    TOB3 files are written in major and minor frames, from top to bottom.  Each
        frame's footer must be check first.  If the frame if valid, it is
        decoded.
    """
    logger = logging.getLogger(__name__)
    fn = os.path.basename(ffn)
    logger.info("starting to decode TOB3 file:  %s", fn)
    rec_cnt = 0
    header = []
    valid_frame_cnt, not_valid_frame_cnt = 0, 0
    rf = open(ffn, "rb")
    for _ in range(6):
        header.append(
            (
                rf.readline()
                .decode("ascii", "ignore")
                .replace('"', "")
                .replace("\r\n", "")
                .replace("\n", "")
                .split(",")
            )
        )
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
    rfs = ",".join([data_type_dict[xx]["refmt"] for xx in dtl]) + "\n"
    bl = [
        int(xx.split("(")[1][:-1])
        if ("ASCII" in xx)
        else data_type_dict[xx]["size"]
        for xx in dtypes
    ]
    trs = sum(bl)
    # -- look-up header & footer size --
    # fs := data Frame Size
    # tbl := table size; intendes number of records in file
    fs = int(header[1][2])
    tbl = int(header[1][3])
    # fft := file format type
    # fhs := frame header size
    # ffs := frame footer size
    # check file's format
    if header[0][0] != "TOB3":
        logger.critical("File (%s) is not TOB3 type!", ffn)
        email_exit()
    fhs = FILE_TYPE_DICT["TOB3"]["fhs"]
    ffs = FILE_TYPE_DICT["TOB3"]["ffs"]

    # interval := non-timestamped record interval; for intra-frame
    # timestamps; in seconds
    interval_str = header[1][1].split(" ")
    interval = int(interval_str[0]) * INTERVAL_DICT[interval_str[1]]
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
    ho[0].append(fn)  # add origional file name to header.
    ho[1] = ["TIMESTAMP", "RECORD"] + ho[1]
    ho[2] = ["TS", "RN"] + ho[2]
    ho[3] = ["", ""] + ho[3]
    # open output file for writing
    outfile = open(toa5_file, "w")
    # outfile = open(output,"w")
    # write header
    for hh in ho:
        outfile.write('"' + '","'.join(hh) + '"\n')
    # examine contents
    # loop though file's Major Frames
    major_cnt = 0  # used only for debugging
    frame = rf.read(fs)
    while len(frame) == fs:
        # read frame footer
        (valid_frame, F, R, E, M, minor_frame_size) = footer_parse(
            frame[-ffs:], validation_int
        )
        logger.debug(
            "MajorFrame: %s len(frame): %s fs: %s valid_frame: %s "
            "F: %s R: %s E: %s M: %s",
            major_cnt,
            len(frame),
            fs,
            valid_frame,
            F,
            R,
            E,
            M,
        )
        major_cnt += 1  # used only for above
        if valid_frame:
            valid_frame_cnt += 1
            # initialize list to hold formatted strings, which will
            # be written to out file, after processing
            # each Major frame.
            records = []
            if not (E == 1 or M == 1):
                # standard Major Frame processing
                records = decode_frameTOB3(
                    frame[:-ffs],
                    fhs,
                    trs,
                    dtl,
                    bl,
                    rfs,
                    interval,
                    ts_resolution,
                )
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
                    (subframe_end_ptr - minor_frame_size) : subframe_end_ptr
                ]
                while True:
                    # sub-frame at a Major frame boundary may be listed
                    # as empty, but the other sub-frames may have data
                    if E != 1:
                        # append sub-frame records to records, i.e.
                        # make a list (i.e. major frame) of lists
                        # (i.e. minor frames).
                        records.append(
                            decode_frameTOB3(
                                sub_frame[:-ffs],
                                fhs,
                                trs,
                                dtl,
                                bl,
                                rfs,
                                interval,
                                ts_resolution,
                            )
                        )
                    # identify location of next sub-frame
                    subframe_offset += minor_frame_size
                    subframe_end_ptr = fs - subframe_offset
                    if skip_sub_frame == cnt_sub_frame:
                        # int(raw_input("**-Paused for
                        # debugging-**\n**Enter number of MINOR
                        # frames to skip over; 0 (zero) is
                        # default.**\n"))
                        skip_sub_frame = 0
                        cnt_sub_frame = -1
                    cnt_sub_frame += 1  # used for skip subframes
                    subframe_cnt += 1  # only used for debugging
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
                    (valid_frame, F, R, E, M, minor_frame_size) = footer_parse(
                        frame[-(subframe_offset + ffs) : -subframe_offset],
                        validation_int,
                    )
                    # read next subframe
                    sub_frame = frame[
                        (
                            subframe_end_ptr - minor_frame_size
                        ) : subframe_end_ptr
                    ]
            # record list of valid frame has been assembled.
            # check if sub-frames exist; if yes, reorder sub-frames,
            # and prepare for writing
            if records:
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
                logger.info(
                    (
                        "breaking out of major frame parse loop, "
                        "becaue not_valid_frame_cnt > 5"
                    )
                )
                break
        # move to next MAJOR frame
        frame = rf.read(fs)
        logger.debug("read() got %s bytes", len(frame))
    logger.debug("TOB3 file (%s);  rec_cnt = %s", fn, rec_cnt)
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
    logger.info("starting to decode TOB1 file %s", fn)
    rec_cnt = 0
    header = []
    with open(ffn, "rb") as rf:
        # read the 5 header lines into variable and then parse it.
        for _ in range(5):
            header.append(
                (
                    rf.readline()
                    .decode("ascii", "ignore")
                    .replace('"', "")
                    .replace("\r\n", "")
                    .replace("\n", "")
                    .split(",")
                )
            )
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
        rfs = ",".join([data_type_dict[xx]["refmt"] for xx in dtl]) + "\n"
        bl = [
            int(xx.split("(")[1][:-1])
            if ("ASCII" in xx)
            else data_type_dict[xx]["size"]
            for xx in dtypes
        ]
        trs = sum(bl)
        if (
            header[1][0] == "SECONDS"
            and header[1][1] == "NANOSECONDS"
            and dtypes[0] == "ULONG"
            and dtypes[1] == "ULONG"
        ):
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
        ho[0].append(fn)  # add origional file name to header.
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
                    ts = CSI_EPOCH + datetime.timedelta(
                        0, ts_list[0], ts_list[1] / 1000
                    )
                    values.insert(0, ts_formatter(ts))
                values = ['"NAN"' if xx == "nan" else xx for xx in values]
                outfile.write(rfs.format(*values))
                rec = rf.read(trs)
                rec_cnt += 1
    logger.debug("TOB1 file (%s); rec_cnt = %s", fn, rec_cnt)
    return rec_cnt


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
    if value == 45:  # - (dash)
        yy = 36
    elif value < 58:  # [0-9]
        yy = value - 48
    elif value > 96:  # [a-z]
        yy = value - 87
    elif value == 95:  # _ (underscore)
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
    valid: datetime
        the timestamp this file is valid for

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
    yyyy = str(decode[0] + 2000)
    mm = "{:02}".format(decode[1])
    dd = "{:02}".format(decode[2])
    hhtt = "{:02}{:02}".format(*divmod(decode[3] * 38 + decode[4], 60))
    valid = datetime.datetime.strptime(
        "%s%s%s%s" % (yyyy, mm, dd, hhtt), "%Y%m%d%H%M"
    )
    valid = valid.replace(tzinfo=pytz.utc)
    filepath = os.path.join(dirpath, yyyy, mm, dd)
    chkmkdir(filepath)
    newfn = (
        fn[:3]
        + "_"
        + table_code[fn[3]]
        + "_"
        + yyyy[2:]
        + mm
        + dd
        + "-"
        + hhtt
    )
    newffn = os.path.join(filepath, newfn)
    logger.info("filename decoded: %s = %s", fn, newfn)
    return newffn, valid


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
        """integer representing YYYYMMDD from datetime.date object"""
        return date.year * 10000 + date.month * 100 + date.day

    def datenum2(dir_rel):
        """integer representing YYYYMMDD from "YYYY/MM/DD" formatted string"""
        xx = os.path.split(dir_rel)
        yy = os.path.split(xx[0])
        return int(yy[0]) * 10000 + int(yy[1]) * 100 + int(xx[1])

    date_start = datenum1(dates[0])
    date_end = datenum1(dates[1])
    logger.debug("date_start = %s; date_end = %s", date_start, date_end)
    dir_list = []
    startinglevel = dirpath.count(os.sep)
    for top, _, _ in os.walk(dirpath):
        if top.count(os.sep) - startinglevel == 3:
            dir_list.append(os.path.relpath(top, dirpath))
    dir_list.sort()
    dir_list_filtered = [
        xx
        for xx in dir_list
        if (datenum2(xx) >= date_start and datenum2(xx) <= date_end)
    ]
    logger.info(
        ("number of directories to Reimport via SQL = %s"),
        len(dir_list_filtered),
    )
    logger.debug("directories to import:\n%s", dir_list_filtered)
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
    if dirpath[-1] != "/":
        dirpath = dirpath + "/"
    newdir = os.path.dirname(dirpath)
    if not os.path.exists(newdir):
        os.makedirs(newdir)
        logger.info("dirpath made to: %s", newdir)


def email_error(body, tail_error_log=True, ffn_error=logger_config.ffn_error):
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
    toaddr = ",".join(CONFIG["email"]["to"])
    fromaddr = CONFIG["email"]["from"]
    msg = MIMEMultipart()
    msg["From"] = fromaddr
    msg["To"] = toaddr
    msg["Subject"] = "Talltowers - FAILURE"

    if tail_error_log:
        body = (
            body + "\n\n" + subprocess.check_output(["tail", "-10", ffn_error])
        )
    msg.attach(MIMEText(body, "plain"))

    logger.info("Emailing ERROR to: %s", toaddr)

    server = smtplib.SMTP(CONFIG["email"]["server"])
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


def email_exit(msg=""):
    """
    email error log tail, and then exit
    """
    logger = logging.getLogger(__name__)
    if msg:
        msg = msg + "\n"
    email_error(msg + "Fatal error, see error log.")
    logger.critical("ABORTED!\n%s%s%s", "*" * 20, "  END OF LOG  ", "*" * 20)
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
    logger = logging.getLogger(__name__)
    # get file name as it exists on the datalogger
    fn_logger = fn[3:9]
    # identfiy which logger the file comes from
    cr6 = CONFIG["ftp"][fn[0:3]]
    if cr6["hostname"] == "...":
        logger.info("Skipping ftp_del since hostname is ...")
        return
    # log into dataloggers FTP service, navigate to direcotry, delete file
    site = ftplib.FTP(cr6["hostname"], cr6["user"], cr6["pass"])
    site.set_pasv(False)
    site.cwd(r"\CRD")
    site.delete(fn_logger)


def parse_TOA5_sql(ffn, dirpath=None):
    """
    parse the TOA5 formatted .dat file (4 header rows) into a .sql file.

    Parameters
    ----------
    ffn: string
        full-filename (includes path and extention)
    dirpath: string [optional]
        location to store tempororary .sql file

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
        dirpath = CONFIG["dataroot"]
    # setup filenames and
    fn = os.path.basename(ffn)
    logger.info("starting to parse TOA5 file: %s", fn)
    fn_basename = os.path.splitext(fn)[0]
    site, table, _ = fn_basename.split("_")
    sql_ffn = os.path.join(dirpath, fn_basename + ".sql")
    # chn_id encoding
    site_number = CHN_CODE["sites"][site]

    df = pd.read_csv(
        ffn, skiprows=[0, 2, 3], header=0, na_values=["NAN", "-INF", "INF"]
    )
    if df.empty:
        raise Exception("0 data rows found in %s" % (fn,))
    # add site
    df["tower"] = site_number
    df.drop("RECORD", axis=1, inplace=True)
    df["valid"] = pd.to_datetime(df["TIMESTAMP"])
    df.drop("TIMESTAMP", axis=1, inplace=True)
    if table == "sonic":
        # Convert the diag columns to int
        for m in [5, 10, 20, 40, 80, 120]:
            c = "Diag_%sm" % (m,)
            if df[c].dtype != np.dtype(int):
                # Hack as pandas can't have an int dtype with missing values
                df[c] = df[c].apply(
                    lambda x: (
                        "%.0f" % (x,)
                        if (pd.notnull(x) and x > -32768 and x < 32767)
                        else None
                    )
                )
    # Database uses partitioned tables, so can insert directly into parent
    table = f"data_{table}"
    df.to_csv(sql_ffn, sep="\t", header=False, index=False, na_rep=r"\N")
    return sql_ffn, table, df.columns


def copy2db_execute(sql_ffn, db, table, columns, UTC=True):
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
    logger.info("starting COPY to db for %s", os.path.basename(sql_ffn))
    try:
        conn = psycopg2.connect(
            (
                "host={hostname} dbname={dbname} "
                "user={dbuser} password={dbpass}"
            ).format(**db)
        )
        logger.debug("connected to database")
        curs = conn.cursor()
        infile = open(sql_ffn, "r")
        logger.debug("database cursor established")
        if UTC:
            curs.execute("set timezone='UTC';")
        curs.copy_from(infile, table=table, columns=columns)
        curs.close()
        conn.commit()
        conn.close()
        logger.debug("copyed to database")
        return "COPY Successful."
        # return None
    except Exception as e:
        logger.exception("Failed to execute COPY for %s", sql_ffn)
        return "Failed to execute COPY for " + sql_ffn + "; ErrMsg: " + str(e)


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
    parser.add_argument(
        "--dataroot",
        type=str,
        default=CONFIG["dataroot"],
        help="[optional] Root for data files to process.",
    )
    parser.add_argument(
        "--filename",
        type=str,
        nargs="+",
        help=(
            "[optional] Filename(s) to process.  Default "
            "is to process all files in current directory, "
            "which match the standard file nameing "
            "convention"
        ),
    )
    # parser.add_argument("--timestamp", choices=['millisec','sec','csi'],
    #                     default='csi',
    #                     help="[optional] Format string for timestamps.
    #                           Default is 'csi'")
    parser.add_argument(
        "--debug",
        action="store_true",
        help=(
            "[optional] Debugging; prints out intermediate "
            "steps, especially for TOB3 processing"
        ),
    )
    parser.add_argument(
        "--database",
        type=str,
        help=(
            "[optional] PostgreSQL database to COPY data "
            "to.  Default according to pyenv.dbconn."
        ),
    )
    # action='append',
    parser.add_argument(
        "--dates",
        nargs=2,
        metavar=("START_DATE", "END_DATE"),
        help=(
            "[optional] Two dates 'YYYY-MM-DD' "
            "(separated by space), as inclusive endpoints "
            "to RE-Import data to database; but can exceed "
            "project data's dates in order to import all.  "
            "Data is already in ASCII and standard folder "
            "structure."
        ),
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help=(
            "[optional] retains the file on the Datalogger. "
            " Default is to delete the file on the "
            "Dataloger, after succesfully COPYing to "
            "the database."
        ),
    )
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
        checkpath = [
            os.path.isfile(os.path.join(dirpath, fn)) for fn in fnames
        ]
        if False in checkpath:
            msg = "{}".format(
                [
                    os.path.join(dirpath, fn)
                    for fn, cp in zip(fnames, checkpath)
                    if not cp
                ]
            )
            logger.error("filename does not exist:\n%s\nABORT!", msg)
            email_exit()
    else:
        fn_pattern = r"^(ham|sto)[SAM]{1}[0-9a-z-_]{5}\.bdat$"
        fnames = sorted(
            [fn for fn in os.listdir(dirpath) if re.match(fn_pattern, fn)]
        )
    # dbconn
    dbconn = CONFIG["dbconn"]
    if args.database:
        dbconn["dbname"] = args.database
    # [debug] ...nothing returned, because it acts directly upon logger
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logstr = ""
        argdict = args.__dict__
        for key in argdict.keys():
            logstr += "\t{:<15} - {}".format(key, argdict[key]) + "\n"
        logger.debug("\nOptional Arguments: \n%s", logstr)
    # save
    delete_datalogger_fn = not args.save
    return dirpath, fnames, dbconn, delete_datalogger_fn


def bin2pg(dirpath, fnames, consumed_dir, dbconn, delete_datalogger_fn):
    """
    Convert Binary CSI file and Copy to postgres.
    """
    logger = logging.getLogger(__name__)
    for fn in fnames:
        logger.info("%s%s%s", "=" * 10, "{:^20}".format(fn), "=" * 10)
        # set input and output file names
        ffn = os.path.join(dirpath, fn)
        try:
            # decode filename and create output full-filename
            toa5_file, valid = decode_filename(fn, dirpath)
            # just check header for file type
            with open(ffn, "rb") as rf:
                file_type = rf.read(6).decode("ascii", "ignore")
            logger.debug(
                "file: %s; type: %s; TOA5: %s", fn, file_type, toa5_file
            )
            # call appropriate function
            if file_type == '"TOB1"':
                rec_cnt = decode_TOB1(ffn, toa5_file)
                logger.info("file: %s; records written: %s", fn, rec_cnt)
            elif file_type == '"TOB3"':
                rec_cnt = decode_TOB3(ffn, toa5_file)
                logger.info(
                    "file: %s; records written: %s; header expected: %s",
                    fn,
                    *rec_cnt,
                )
            elif file_type == '"TOB2"':
                logger.critical('No script to decode "TOB2" file types')
            else:
                logger.error(" unrecognized file type")
            # rename file, as an atomic action, after file writing is complete
            os.rename(toa5_file, toa5_file + ".dat")
            # ------------------------------------------------------------------------
            # parse resultant TOA5 file to SQL file
            sql_ffn, table, columns = parse_TOA5_sql(toa5_file + ".dat")
            # copy SQL file to database
            result = copy2db_execute(sql_ffn, dbconn, table, columns)

            logger.info(result)
            if result == "COPY Successful.":
                # Copy the .bdat file to consumed/YYYY/mm/dd/
                restingplace = "%s/%s" % (
                    consumed_dir,
                    valid.strftime("%Y/%m/%d"),
                )
                chkmkdir(restingplace)
                restingfn = "%s/%s_%s" % (
                    restingplace,
                    valid.strftime("%Y%m%d%H%M"),
                    fn,
                )
                logger.debug("moving %s to %s", fn, restingfn)
                os.rename(ffn, restingfn)
                logger.debug("deleteing SQL formated file: %s", sql_ffn)
                os.remove(sql_ffn)
                logger.info(
                    "deleteing DataLogger file associated with: %s", fn
                )
                ftp_del(fn)
            else:
                logger.info(
                    "deleteing DataLogger file associated with: %s", fn
                )
                ftp_del(fn)
                raise Exception("DBCopy failed")
        except ftplib.error_perm as exp:
            logger.debug(exp)
        except Exception as exp:
            logger.debug(exp)
            quarentine_path = os.path.join(dirpath, "quarentine")
            chkmkdir(quarentine_path)
            func = logger.exception if fn[3] != "M" else logger.warning
            func("%s FAILED. Moved to '%s'", fn, quarentine_path)
            # move file
            try:
                os.rename(ffn, os.path.join(quarentine_path, fn))
            except Exception:
                pass


def main(argv):
    """
    The starting point, when program is called.
    """
    logger = logging.getLogger(__name__)
    logger.info("%s%s%s", "*" * 20, "  STARTING  ", "*" * 20)
    # parse the args, from Command Line
    args = arg_parse(argv)
    # check the args
    (dirpath, fnames, dbconn, delete_datalogger_fn) = arg_check(args)

    # set consumed directory
    consumed_dir = os.path.join(dirpath, "consumed")
    chkmkdir(consumed_dir)
    # CSI binary
    bin2pg(dirpath, fnames, consumed_dir, dbconn, delete_datalogger_fn)


if __name__ == "__main__":
    main(sys.argv[1:])
