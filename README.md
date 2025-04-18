```bash
docker build -t dijkstra-app .
docker run -d -p 5000:5000 --name dijkstra dijkstra-app
http://<your_ip>:5000
```
