FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg libgl1 libglib2.0-0 libasound2 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python","src/app.py","--source","data/sample/route.mp4","--detector","hsv","--planner","beam","--h_min","30","--h_max","90","--s_min","60","--s_max","255","--v_min","60","--v_max","255","--topk","3","--ai_coach","local","--log_session"]
