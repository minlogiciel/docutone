#!/bin/sh
/home/richard/min/CRF++-0.58/bin/linux/crf_learn -c 10.0 template train.data model
/home/richard/min/CRF++-0.58/bin/linux/crf_test  -m model test.data

echo /home/richard/min/CRF++-0.58/crf_learn -a MIRA template train.data model
/home/richard/min/CRF++-0.58/crf_test  -m model test.data

