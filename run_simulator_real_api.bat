@echo off
echo Starting Smart Fridge Simulator with real API integration...
python run_simulator.py --interval 30 --image-interval 60 --real-api
echo Simulator stopped.
pause 