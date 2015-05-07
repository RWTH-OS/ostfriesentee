env = Environment(JAVACLASSPATH="/usr/share/java/bcel.jar")
classes = env.Java('build/classes', 'src')
env.Jar('build/infuser.jar', classes + ['MANIFEST.MF'])
