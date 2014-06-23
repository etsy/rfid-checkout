/*
 * HID_Reader:
 *********************************************************************************
 *
 *  This was too slow in Python, so moving to a C app. Note if you make changes
 *  here, you might have to update the python app to account for changes in the
 *  output, file name, or data
 *
 *  Requires - wiringPi   https://projects.drogon.net/wiring-pi
 *
 *  Note RapPI GPIO pins defined differently for this app. 
 *  The HID Reader must be wired to GPIO pins "0" and "1" 
 *  which are BCM Pins "17" and "18"
 *
 */
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <wiringPi.h>
#include <unistd.h>

static volatile int bitcount ;

// If you use a mix of RFID tags with different bit lengths, set these appropriately 
static int bits_shortest = 12;
static int bits_longest = 42;


void myInterrupt0 (void) { printf ("0"); bitcount++; }
void myInterrupt1 (void) { printf ("1"); bitcount++; }


int main (void)
{
  int read_delay = (bits_longest - bits_shortest) * 2000;

  wiringPiSetup () ;
  wiringPiISR (0, INT_EDGE_FALLING, &myInterrupt0) ;
  wiringPiISR (1, INT_EDGE_FALLING, &myInterrupt1) ;


  while (1) 
  {
    bitcount = 0 ;
    printf ("Waiting ... ") ; fflush (stdout) ;

    while(1)
    {
      if (bitcount >= bits_shortest)
      {
        // This delay on the main thread is to make sure we have all the bits
        // even from longer tags before restarting our loop
        usleep(read_delay);
        break ;
      }
      else
        usleep(50000);
    }
    printf ("\n") ; fflush (stdout) ;
  }

  return 0 ;
}