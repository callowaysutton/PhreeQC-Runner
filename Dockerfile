# 
FROM python:3.11

#
RUN apt update && apt upgrade -y && apt install -y s3fs
# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./app /code/app

# 
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]