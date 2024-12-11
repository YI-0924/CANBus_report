# Usage
**To run simulator**
```bash
sudo apt-get install libsdl2-dev libsdl2-image-dev -y
sudo apt-get install can-utils -y
sudo apt install gcc -y
cd ICSim
sudo bash start.sh
```
```start.sh```will execute three program
1. ```candump``` show packges now sending
2. ```icsim```: dashboard simulator based on CAN bus
3. ```controls```: simulate modules on a car, send control signal(CAN packges) to icsim

**To re-build ICSim**: 
use ```make``` to build up.
```bash
# after some modify on source files...
~/ICSim$ make
```

# Replay Attack
```bash
cd candumplog
bash replayattack.sh
```
while the simulator is running (e.g. after execute start.sh), also execute ```candumplog/replayattack.sh```. it will first dump packages into a file(using ```candump```), then execute ```canplayer``` to replay the file just dumped.
```bash
# file: replayattack.sh
rm *.log
candump -l vcan0
canplayer -I candump*.log
```
you may need wait a few seconds then press ctrl+C to stop dumping packages. then the bash will start replayattack automatically.
for example:
```
~/candumplog$ ./replayattack.sh
recording packges......
Disable standard output while logging.

Enable Logfile 'candump-2024-12-06_005734.log'
### wait a few seconds ###
^C
executing replay attack......
```
now time stamp in ```icsim``` is equipped, so you will see that:
```
invalid time stamp: xxxxxxxxxx, now timestamp: xxxxxxxxxx
invalid time stamp: xxxxxxxxxx, now timestamp: xxxxxxxxxx
invalid time stamp: xxxxxxxxxx, now timestamp: xxxxxxxxxx 
``` 
which means the attack doesn't succeceed.
# DoS attack
## virtual machine(ubuntu 20.04)
**1.Constructed datasets with and without DoS**
```bash
~/ICSim$ vim icsim.c
make
```
put comment on open banned_id.txt
```bash
# (optional: open if applying DoS)
~/ICSim$ ./attack
```
apply DoS attack
```bash
~/ICSim$ candump -l vcan0 && find . -type f -name 'candump-*' -exec mv {} candumpFile.log \;
```
do candump (record data) and change log name

**2.change datasets into valid csv file for training**
```
~/ICSim$ python3 toCSV.py
```
turn candumpFile.log into test_value.csv file

**3.upload test_value.csv for PC**
# Spoofing Attack
xxxx can be any number you like from 0~F to represent the speed.
ID 244 stands for the accelerator, ID 200 stands for the dashboard.
```bash
./cansend vcan0 200#000000xxxx //if 000000xxxx is a speed more than 10, the dashboard will not change because the speed difference between dashboard and accelerator is too big.
./cansend vcan0 244#000000xxxx //change the accelerator speed.
./cansend vcan0 200#000000xxxx //dashboard should change if the number you enter is not too much bigger or smaller than the number you enter when ID is 244.
```
## PC
**1.download test_value.csv**

**2.train model on python**
```
~/model$ py change.py
py train.py
py DoS_detect.py
```
```change.py```: input trainset.csv and trainset_dos.csv to create file with target, target=1 means DoS

```train.py```: input trainset.csv and trainset_dos.csv to create(save) lstm_model.keras and scaler.joblib

```DoS_detect.py```: input testing dataset (.csv)

```delete_target.py```: used to remove target from csv file if mistakenly added

**3.got target.csv and banned_id.txt**

target.csv: file that contain datasets and predicted target

banned_id.txt: file that contain IDs that predicted target are 1 (IDs that are DoS attack)

## virtual machine
**banned ID that is DoS**
```bash
~/ICSim$ vim icsim.c
make
```
delete comment of banned_id.txt
## real-time implement process (not yet implement)
```
./icsim vcan0 and candump、toCSV.py、DoS_detect.py at the same time
```
problem: ubuntu20.04 cannot run tensorflow
## result
case1:no attack, keep going as usual

case2:DoS attack, create banned_id.txt with DoS ID that can be detected by icsim and print "Detect DoS Attack", return 0

**can achieve 100% accuracy of DoS detect**
## reference
_[1] "LSTM-Based Intrusion Detection System for In-Vehicle Can Bus Communications" - MD DELWAR HOSSAIN, HIROYUKI INOUE, HIDEYA OCHIAI, DOUDOU FALL, YOUKI KADOBAYASHI (2020)_

_[2] "OTIDS: A Novel Intrusion Detection System for In-vehicle Network by using Remote Frame" - Hyunsung Lee, Seong Hoon Jeong and Huy Kang Kim (2017)_

_[3] https://github.com/zombieCraig/ICSim_
**記得加上license**

_[4] https://github.com/linux-can/can-utils_
**記得加上license**

_[5] https://medium.com/@yogeshojha/car-hacking-101-practical-guide-to-exploiting-can-bus-using-instrument-cluster-simulator-part-i-cd88d3eb4a53_

_[6] https://xz.aliyun.com/t/13028?time__1311=GqmhBKYKAKYvK05DK7SiKRWT3NDkDIoEbD#toc-14_
