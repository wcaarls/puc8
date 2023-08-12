#include "puc8.h"

unsigned char buf[] = "Hello, world!";

void main(void)
{
  for (int ii=0; buf[ii]; ++ii)
  {
    while (inp(LDR));
    outp(buf[ii], LDR);
  }
}
