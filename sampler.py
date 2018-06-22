from subprocess import Popen, PIPE

p = Popen(["find", "output/", "-name", "*.jpg"], stdout=PIPE)
imagepaths = p.stdout.read().strip().split()
print(imagepaths)
