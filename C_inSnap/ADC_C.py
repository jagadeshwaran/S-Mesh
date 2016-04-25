import_c("ADC_C.c")

@c_function(api=["int", "int"])
def take_averaged_sample(channel):
    pass

###########################################################################
# fill_data1
# This function potentially changes the length of the passed string, so
# there is risk of overflowing the string buffer.
###########################################################################
@c_function(api=["none", "str", "int"])
def ReadADCdatachunks(s, count):
    '''
    Take a string s and fill make it length count, with 'w' at each character.
    This function returns None.
    Note: This is potentially dangerous. If you pass a count value longer
    than the string buffer in use for the passed string, you can overflow
    into other data in RAM.
    '''
    # Associated C code in wrap_test.c as fill_data1
    pass

def ReadADCdatachunks1(data):
    s = ''
    i = 0
    # Construct a string as large as SNAPpy can handle to pass in.
    while i < 255:
        s += ' '
        i+= 1
    ReadADCdatachunks(s, data)
    return "ADC Chunk datas are: " + s