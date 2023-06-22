#!/bin/bash

# Create data folder and its subfolders
mkdir -p data/ref_data
mkdir -p data/tx_data/archive
mkdir -p data/tx_data/input
mkdir -p data/tx_data/output

# Create log folder and app.log file
mkdir -p log
touch log/app.log

echo "Setup completed successfully"