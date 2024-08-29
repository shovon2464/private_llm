export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/miniconda3/envs/privateGPTAPI/lib/python3.12/site-packages/nvidia/cudnn/lib
uvicorn privateGPTAPI.asgi:application --host 192.168.1.111 --port 8000