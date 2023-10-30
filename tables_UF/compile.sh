#!/bin/bash

gcc tables.c -O0 -o tables.exe

for UF in 2 4 8 16 32;
do
	gcc tables_uf${UF}.c -O0 -o tables_uf${UF}.exe
done
