void error()
{
  while (1);
}

void main(void)
{
  unsigned int a=12, b=13;

  if (a == b) error();
  if (a > b) error();
  if (a >= b) error();
  if (b < a) error();
  if (b <= a) error();
  if (a != a) error();
}
