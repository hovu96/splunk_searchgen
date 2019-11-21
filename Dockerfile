FROM python:3
ADD main.py /
ADD splunklib /
CMD [ "python", "./main.py" ]
