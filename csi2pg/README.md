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