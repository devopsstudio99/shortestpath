docker build -t dijkstra-app .
docker run -d -p 5000:5000 --name dijkstra dijkstra-app
open browser http://<your_ip>:5000
