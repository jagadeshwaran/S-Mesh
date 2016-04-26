#define ENABLE_BIT_DEFINITIONS
#include <ioavr.h>
#include <iom128rfa1.h>
#include "snappy.h"

#define REFERENCE_VOLTAGE       ((1 << REFS1) | (1 << REFS0))

//split into 31 parts
static int16_t  AnalogValues[8][130];
static int16_t  AnalogValuesOneSample[8];
static int16_t  counter[8];

int16_t take_sample()
{
    // take a sample
    ADCSRA |= (1 << ADSC) | (1 << ADIF);
    while ( ADCSRA & (1<<ADSC) ) ;
    
    // return when clear
    return ADC;
}

// In this example, we are assuming we're only interested in taking
// samples from a single ended ADC (one of channels ADC0-7).
void enable_adc_and_set_channel(int16_t channel)
{
    ADCSRA &= (1 << ADEN);
    
    //ADMUX = (channel & 0x1F);
    ADMUX = REFERENCE_VOLTAGE | (channel & 0x1F);
    
    // select the ADC we want
    ADCSRB &= ~(1 << MUX5);
    
    // start one converstion to throw away to let the power supply settle
    ADCSRA = (1 << ADEN) | (1 << ADSC) | (1 << ADPS1);    

    // Wait for conversion to complete
    while (ADCSRA & (1 << ADSC)) ;

    // Now reset the sample rate to 4MHz
    ADCSRA = (1 << ADEN) | (1 << ADPS1);
}

int16_t take_averaged_sample(int16_t channel)
{
    #define NUM_SAMPLES_PER_AVERAGE1 20
	int16_t sum = 0;
	enable_adc_and_set_channel(channel);
	
	for ( int i = 0; i < NUM_SAMPLES_PER_AVERAGE1; ++i )
	{
		 sum += take_sample();
	}
	AnalogValues[channel][counter[channel]] = sum;
	counter[channel]++;
	if (counter[channel]==500)
	{
		counter[channel]=0;
	}
	return sum; // NUM_SAMPLES_PER_AVERAGE;
}

void take_averaged_sample_all_channels(int16_t channel)
{
    #define NUM_SAMPLES_PER_AVERAGE 20
	for(int j=0; j<8; j++)
	{
		int16_t sum = 0;
		enable_adc_and_set_channel(j);
		
		for ( int l = 0; l < NUM_SAMPLES_PER_AVERAGE; ++l )
		{
			 sum += take_sample();
		}
		
		AnalogValuesOneSample[j] = sum;
	}
	
	//return AnalogValuesOneSample; // NUM_SAMPLES_PER_AVERAGE;
}

int16_t GetValues(int16_t channel, int16_t sampleNo)
{
	return AnalogValues[channel][sampleNo];
}

void ReadADCdatachunks(uint8_t *s, int16_t count)
{
    int16_t k;
    for(k = 0; k < count; k++)
    {
        s[k] =  's';
    }
SET_STR_LEN(s, count);
}