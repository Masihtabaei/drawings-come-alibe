FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt update
# Dependency for opencv-python (cv2). `import cv2` raises ImportError: libGL.so.1: cannot open shared object file: No such file or directory
# Solution from https://askubuntu.com/a/1015744
RUN apt install -y libgl1-mesa-glx
RUN apt-get update && apt-get install -y libzbar0
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 


COPY ./template_generator.py /code/
COPY ./main.py /code/
# 


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
