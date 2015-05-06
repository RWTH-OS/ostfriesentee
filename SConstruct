env = Environment(JAVACLASSPATH="/usr/share/java/bcel.jar")
classes = env.Java('build', 'src/main')
env.Jar('build/lib/infuser.jar', classes + ['MANIFEST.MF'])
