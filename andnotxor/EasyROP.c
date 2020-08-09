// gcc -static -m32 -fno-stack-protector easyropme.c -o easyropme

void function(char *str)
{
   char buffer[16];
   strcpy(buffer,str);
}

void main()
{
  char large_string[256];
  gets(large_string);

  function(large_string);
  printf("Nope. String is %s\n", large_string);
}
