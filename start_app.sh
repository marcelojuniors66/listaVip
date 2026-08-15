#!/bin/bash
if ! command -v pip3 &> /dev/null; then
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py --break-system-packages
fi
if ! python3 -c "import streamlit" &> /dev/null; then
    python3 -m pip install -r requirements.txt --break-system-packages
fi
python3 -m streamlit run app.py --server.port 3000 --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false
