echo "Build turing machine emulator..."
cp ./turing.py ./turing
sed -i 's/\r$//' ./turing
chmod +x ./turing
echo "Try turing machine emulator..."
./turing -h