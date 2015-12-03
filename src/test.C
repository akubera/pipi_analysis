

// struct Foo;

void test()
{
  cout << "TEST\n";
  // cout << foo().first << "\n";
  Foo q;
  cout << q.b << "\n";

}

struct Foo {
  Foo(): a(10)
       , b(100)
  {};

  int a;
  int b;
};

std::pair<int,int> foo() { return std::pair<int,int>(10,10); }
