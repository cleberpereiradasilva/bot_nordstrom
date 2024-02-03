docker build . -t local/vncubuntu:0.0.1

docker run -d -p 6901:6901 -p 5901:5901 -v /dev/shm:/dev/shm -v ./out:/home/rpa/out local/vncubuntu:0.0.1
