FROM python:3
ADD splunklib /splunklib
ADD main.py /
CMD [ "python", "./main.py" ]
