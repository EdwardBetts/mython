import sys
import os
import mython as my
import subprocess as sub
from copy import deepcopy
import shutil as sh

cwd = os.getcwd()
baselines = open(sys.argv[1],'r').read().split('\n')
with open("base.d12",'w') as outf:
  outf.write("\n".join(baselines))

struct_p = []
#dxs = [-0.3,-0.2,-0.1,0.1,0.2,0.3]
#dxs += [-0.03,0.0,0.03]
#use_fort = "fort.9"
#with open("smooth_pruns.dat",'r') as inpf:
#  for line in inpf:
#    spl = line.split()
#    base = map(float,spl[1:])
#    for dx in dxs:
#      add = deepcopy(base)
#      add[-1]*=(1+dx)
#      struct_p.append(add)


# qsub options.
exe = "~/bin/Pcrystal" 
nn  = 1
np  = 8
time = "24:00:00"
queue = "batch"
#pc = ["module load openmpi/1.4-gcc+ifort","rm INPUT","cp XXX INPUT"]
pc = ["rm INPUT","cp XXX INPUT"]
fc = ["rm *.pe[0-9]","rm *.pe[0-9][0-9]"]

################################################################################
# Edit structure.

# Format (a,c,zse)
geolist = struct_p
tmplines  = deepcopy(baselines)
for gi,geo in enumerate(geolist):
  name = "geo_%d"%gi
  if not os.path.isdir(name):
    os.mkdir(name)
  if use_fort:
    sh.copyfile(use_fort,name+'/fort.20')
  os.chdir(name)
  tmplines[4] = " ".join(map(str,geo[:2]))
  se_part = tmplines[7].split(" ")
  se_part[-1] = str(geo[-1])
  tmplines[7] = " ".join(se_part)

  with open(name+".d12",'w') as outf:
    outf.write("\n".join(tmplines))

  pc[-1] = "cp %s.d12 INPUT"%name
  qsub = my.gen_qsub(exe,
    stdout = name+".d12.out",
    loc = os.getcwd(),
    name = "%s %s"%(os.getcwd(),name),
    time = time,
    nn = nn,
    queue = queue,
    prep_commands = pc,
    final_commands = fc
  )
  print name, sub.check_output("qsub %s"%qsub,shell=True)
  os.chdir(cwd)

################################################################################
# Edit options.

shrinklist = []#[2,4,6,8,10,12]
tmplines  = deepcopy(baselines)
for shrink in shrinklist:
  name = "shrink_%d"%shrink
  if not os.path.isdir(name):
    os.mkdir(name)
  os.chdir(name)
  for li,line in enumerate(tmplines):
    if "SHRINK" in line:
      tmplines[li+1] = " ".join(map(str,[shrink,2*shrink]))

  with open(name+".d12",'w') as outf:
    outf.write("\n".join(tmplines))

  pc[-1] = "cp %s.d12 INPUT"%name
  qsub = my.gen_qsub(exe,
    stdout = name+".d12.out",
    loc = os.getcwd(),
    name = "%s %s"%(os.getcwd(),name),
    time = time,
    nn = nn,
    queue = queue,
    prep_commands = pc,
    final_commands = fc
  )
  #print name, sub.check_output("qsub %s"%qsub,shell=True)
  os.chdir(cwd)

raycovlist = [-0.1,-0.2,-0.3,-0.4,-0.5]
tmplines  = deepcopy(baselines)
for raycov in raycovlist:
  name = "raycov_%2.2f"%raycov
  if not os.path.isdir(name):
    os.mkdir(name)
  os.chdir(name)
  for li,line in enumerate(tmplines):
    if "RAYCOV" in line:
      before = tmplines[li+2].split()
      tmplines[li+2] = " ".join(map(str,[before[0],raycov]))

  with open(name+".d12",'w') as outf:
    outf.write("\n".join(tmplines))

  pc[-1] = "cp %s.d12 INPUT"%name
  qsub = my.gen_qsub(exe,
    stdout = name+".d12.out",
    loc = os.getcwd(),
    name = "%s %s"%(os.getcwd(),name),
    time = time,
    nn=nn,np=np,
    queue = queue,
    prep_commands = pc,
    final_commands = fc
  )
  print name, sub.check_output("qsub %s"%qsub,shell=True)
  os.chdir(cwd)
