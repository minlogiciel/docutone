#!/bin/sh
D:\DocutoneSoftware\SmartDoc\bin\CRF++-0.58\crf_learn -p 4 -c 4.0 D:\DTNSoftware\src-smart\python\src\data\crf\template.data D:\DTNSoftware\src-smart\python\src\data\crf\房地产合同\training.data D:\DTNSoftware\src-smart\python\src\data\crf\房地产合同\model
D:\DocutoneSoftware\SmartDoc\bin\CRF++-0.58\crf_test -m model testing.data

