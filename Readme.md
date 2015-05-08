# Ostfriesentee Infuser

This is the infuser of the [darjeeling](http://darjeeling.sourceforge.net)
fork `ostfriesentee`.

This java program loads java `.class` files, converts JVM instructions
to `darjeeling`/`ostfriesentee` compatible instructions and links
them statically.

## Build

~~~{.sh}
scons
~~~

## Execute

~~~{.sh}
java -jar build/libs/ostfriesentee-infuser.jar ../ostfriesentee/app/testsuite/build/testsuite.jar -o test.di -h test.dhi -d test.h -n hello
~~~

However, this currently leads to unexpected results.

## License

As a fork of `darjeeling`, this is also licensed under `LGPLv3+`.
