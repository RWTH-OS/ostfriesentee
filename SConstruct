#env = Environment(tools=['javac', 'javah', 'jar'])
#env.Append(JAVACLASSPATH="/usr/share/java/bcel.jar")
#env.Java('classes', 'src')
#env.Jar(target = 'infuser.jar', source = ['classes/org', 'Manifest.txt'])


env = Environment(JAVACLASSPATH="/usr/share/java/bcel.jar")
classes = env.Java('build', 'src/main')
env.Jar('build/lib/infuser.jar', classes + ['MANIFEST.MF'])

