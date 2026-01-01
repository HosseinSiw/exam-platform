FROM python:3.12

WORKDIR /app
ENV PYTHONDONTWRITEBYCODE=1

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple 

COPY . .
EXPOSE 8000

