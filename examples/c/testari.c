void error()
{
  while (1);
}

void main(void)
{
  if (12U == 13U) error();
  if (12U > 13U) error();
  if (12U >= 13U) error();
  if (13U < 12U) error();
  if (13U <= 12U) error();
  if (12U != 12U) error();

  if ((12+13) != 25) error();
  if ((13-12) != 1) error();
  if ((12<<1) != 24) error();
  if ((12>>1) != 6) error();
  if ((12|13) != 13) error();
  if ((12&13) != 12) error();
  if ((12^13) != 1) error();
}
