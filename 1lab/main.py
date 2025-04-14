#!/usr/bin/env python3

import sys
import os
import server

if __name__ == "__main__":
    initial_programs = sys.argv[1:] if len(sys.argv) > 1 else []
    
    server.run_server(initial_programs) 