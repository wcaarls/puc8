#include "puc8.h"

unsigned char buf[] = "# ";

void writechar(char c, char reg)
{
  while (inp(reg));
  outp(c, reg);
}

void main(void)
{
  char c=0x0d;

  while (1)
  {
    if (c == 0x0d)
    {
      // Clear screen
      writechar(0x01, LCR);

      // Write prompt
      for (int ii=0; buf[ii]; ++ii)
        writechar(buf[ii], LDR);
    }
    else if (c != 0)
    {
      // Echo character
      writechar(c, LDR);
    }

    c = inp(KDR);
  }
}
