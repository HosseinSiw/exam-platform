FROM python:3.12

WORKDIR /app
ENV PYTHONDONTWRITEBYCODE=1

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple 

COPY . .
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "-c", "gunicorn.conf.py"]

