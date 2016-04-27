import_c("ADC_C.c")

@c_function(api=["none"])
def startup():
    """ Clears all the buffers  """
    pass

@c_function(api=["int", "int"])
def take_averaged_sample(channel):
    """ Takes samples of the specified channel at a time and stores it"""
    pass

@c_function(api=["none", "int"])
def take_averaged_sample_all_channels(samples):
    """ It takes the samples of all 7 different ADC channels at a single call"""
    pass

#-------------------------------------------------------------
# say channel 0 and 120, you will get the return values as the 
# zeroth channel ADCs last reading of 120th moment.
# Its periodicity is based on the peridiocity of take_averaged_sample()
#------------------------------------------------------------

@c_function(api=["int","int", "int"])
def GetADCSanmpledValues(channel,sampleNo):
    """ The last 130 values of 8 channels are stored sequentially, you can access
    any of it by just giving the channel no and Samplepoint which should be less than 130 """
    pass

@c_function(api=["none", "str", "int"])
def ReadADCdatachunks(s, count):
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