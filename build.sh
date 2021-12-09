echo "Check running environment (Python 3)..."

/usr/bin/python3 --version

echo "Build turing machine emulator to ./turing ..."

cp ./turing.py ./turing
sed -i 's/\r$//' ./turing
chmod +x ./turing

echo "Try turing machine emulator..."

./turing -h