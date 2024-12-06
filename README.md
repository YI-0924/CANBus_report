# DoS attack
## virtual machine(ubuntu 20.04)
**1.implement 3 or 4 terminal at the same time to record with/without attack**
```
cd ICSim
./setup_vcan.sh
./vim icsim  //add comment of open file and banned_id.txt
make
./icsim vcan0 
```
```
cd ICSim
./controls vcan0
```
```
(optional: open if applying DoS)
cd ICSim
./attack  //apply DoS attack
```
```
cd ICSim
candump -l vcan0 && find . -type f -name 'candump-*' -exec mv {} candumpFile.log \;  //do candump and change log name
```
**2.after recording**
```
python3 toCSV.py  //turn candumpFile.log into test_value.csv file
```
**3.upload test_value.csv for PC**
## PC
**1.download test_value.csv**

**2.train model on python**
```
py change.py  //input trainset.csv and trainset_dos.csv to create file with target, target=1 means DoS
py train.py  //input trainset.csv and trainset_dos.csv to create(save) lstm_model.keras and scaler.joblib
py DoS_detect.py  //input test_value_dos.csv or test_value_not000.csv or test_value_dos_noControls.csv or test_value.csv
//py delete_target.py is used to remove target from csv file if mistakenly added
```
**3.create target.csv and banned_id.txt after doing DoS_detect.py**
## virtual machine
**banned ID that is DoS**
```
cd ICSim
vim icsim.c  //delete comment of open file and banned_id.txt
make
```
## real-time implement process (not yet implement)
```
./icsim vcan0 and candump、toCSV.py、DoS_detect.py at the same time
```

case1:no attack, then keep going as usual

case2:DoS attack, then will create banned_id.txt with DoS ID, and then detected by icsim( will return 0 )

_ubuntu20.04 cannot run tensorflow_

_can achieve 100% accuracy of DoS detect_

## reference
_[1] "LSTM-Based Intrusion Detection System for In-Vehicle Can Bus Communications" - MD DELWAR HOSSAIN, HIROYUKI INOUE, HIDEYA OCHIAI, DOUDOU FALL, YOUKI KADOBAYASHI (2020)_

_[2] "OTIDS: A Novel Intrusion Detection System for In-vehicle Network by using Remote Frame" - Hyunsung Lee, Seong Hoon Jeong and Huy Kang Kim (2017)_

_[3] https://github.com/zombieCraig/ICSim_
**記得加上license**

_[4] https://github.com/linux-can/can-utils_
**記得加上license**

_[5] https://www.reddit.com/r/learnpython/comments/1ef2tmc/struggling_with_realtime_detection_of_dos_attacks/?rdt=63945_

_[6] https://bbs.kanxue.com/thread-278946.htm_

_[7] https://medium.com/@yogeshojha/car-hacking-101-practical-guide-to-exploiting-can-bus-using-instrument-cluster-simulator-part-i-cd88d3eb4a53_

_[8] https://xz.aliyun.com/t/13028?time__1311=GqmhBKYKAKYvK05DK7SiKRWT3NDkDIoEbD#toc-14_
