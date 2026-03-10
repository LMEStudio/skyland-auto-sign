# 构建云函数,必须使用linux编译
cd ../
mkdir ./dist/cloud_functions
pyinstaller --distpath ./dist/cloud_functions src/index.py
touch dist/cloud_functions/INPUT_HYPERGRYPH_TOKEN.txt
cp ./.build/bootstrap ./dist/cloud_functions