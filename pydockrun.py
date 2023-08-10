# pydockrun - single file containerized python scripts
# Inspired by PEP 723 ;)
# Run your python scripts within a docker container, with the
# Dockerfile defined right in your script!
# Example script for a FastAPI server:
# ### server.py: 
# __dockerfile__ = """
# from python:3.11-slim
#
# RUN pip install fastapi uvicorn
#
# EXPOSE 8000
#
# CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
# """
# from fastapi import FastAPI
#
# app = FastAPI()
#
# @app.get("/")
# def index():
#   return {"hello": "from docker!"}
# ### end server.py
#
# Run the server with: pydockrun server.py
import re, subprocess, uuid

def read_dockerfile_string(sourcefile_path: str):
    """Get Dockerfile content from source file""" 
    dfr = re.compile(r'(?ms)^__dockerfile__ *= *"""\\?$(.+?)^"""$')

    with open(sourcefile_path) as f:
        matches = dfr.search(f.read())
        if matches:
            return matches.group(1)

    return None

def get_ports(dockerfile_string: str):
    pr = re.compile(r'EXPOSE (.+)')

    return [match.group(1) for match in pr.finditer(dockerfile_string)]

def main(argv):
    if len(argv) < 2:
        print(f"usage: {argv[0]} source_file") 
        exit(127)

    # Get dockerfile contents from script file
    dockerfile_string = read_dockerfile_string(sys.argv[1])

    # If no __dockerfile__ string found, run as plain python
    if not dockerfile_string:
        return subprocess.run(["python", sys.argv[1:]])

    # Copy source file to container
    dockerfile_string += f'\nCOPY {sys.argv[1]} .'

    # Get any ports needed to map
    ports = get_ports(dockerfile_string)

    # If no command is specified in __dockerfile__, script will be ran with python and args
    if "CMD" not in dockerfile_string: 
        cmd = ["python"] + argv[1:]
        dockerfile_string += f'\nCMD {cmd}'

    # Unique image ID
    image_id = str(uuid.uuid1()) 

    # Write completed dockerfile string to temp file
    with open(f".{image_id}", "w") as dockerfile:
        dockerfile.write(dockerfile_string)

    # Build image
    subprocess.run(["docker", "build", "-t", image_id, "-f", f".{image_id}", "."])
    # Rm dockerfile
    subprocess.run(["rm", f".{image_id}"])

    # Compile run command
    run_command = ["docker", "run"]
    # If any ports are EXPOSEd in __dockerfile__, map them exactly to host
    for port in ports:
      run_command += ["-p", f"{port}:{port}"] 
 
    # Run container 
    try:
        subprocess.run(run_command + [image_id])
    except KeyboardInterrupt:
        pass
    # Remove image when complete
    subprocess.run(["docker", "image", "rm", image_id])

if __name__ == "__main__":
    import sys
    main(sys.argv)
