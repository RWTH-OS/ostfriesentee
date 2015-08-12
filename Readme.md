# Ostfriesentee

`Ostfriesentee` is a fork of the [darjeeling](http://darjeeling.sourceforge.net)
JVM. While `darjeeling` supports `AVR` and `MSP430` targets, `Ostfriesentee`
currently only supports `ARM cortex-m` targets.

Have a look at the [examples](https://github.com/RWTH-OS/ostfriesentee-examples)
to get started.

## Infuser
This java program loads java `.class` files, converts JVM instructions
to `darjeeling`/`ostfriesentee` compatible instructions and links
them statically.

### Build

~~~{.sh}
scons
~~~

### Execute

~~~{.sh}
java -jar build/libs/ostfriesentee-infuser.jar ../ostfriesentee/app/testsuite/build/testsuite.jar -o test.di -h test.dih -d test.h -n hello
~~~

However, this currently leads to unexpected results.

## License

As a fork of `darjeeling`, this is also licensed under `LGPLv3+`.
