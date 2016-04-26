import_c("ADC_C.c")

@c_function(api=["int", "int"])
def take_averaged_sample(channel):
    pass

@c_function(api=["none", "int"])
def take_averaged_sample_all_channels(samples):
    pass

@c_function(api=["int","int", "int"])
def GetValues(channel,sampleNo):
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